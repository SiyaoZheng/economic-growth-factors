from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import (
    DATAVERSE_API,
    DATAVERSE_FILES,
    DATA_RAW,
    END_YEAR,
    START_YEAR,
    WDI_INDICATORS,
    ensure_dirs,
)


def make_session() -> requests.Session:
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=1.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=8)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": "growth-factors-data-pipeline/0.1"})
    return session


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_dataverse_file_id(session: requests.Session, persistent_id: str, filename: str) -> int:
    url = f"{DATAVERSE_API}/datasets/:persistentId/"
    response = session.get(url, params={"persistentId": persistent_id}, timeout=60)
    response.raise_for_status()
    payload = response.json()
    files = payload["data"]["latestVersion"]["files"]
    matches = [
        file_info["dataFile"]["id"]
        for file_info in files
        if file_info.get("dataFile", {}).get("filename") == filename
    ]
    if not matches:
        available = [file_info.get("dataFile", {}).get("filename") for file_info in files]
        raise RuntimeError(f"Could not find {filename} in {persistent_id}. Available: {available}")
    return int(matches[0])


def download_file(session: requests.Session, url: str, dest: Path, force: bool = False) -> dict[str, Any]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0 and not force:
        return {
            "path": str(dest),
            "downloaded": False,
            "bytes": dest.stat().st_size,
            "sha256": sha256_file(dest),
            "url": url,
        }

    tmp = dest.with_suffix(dest.suffix + ".part")
    with session.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with tmp.open("wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
    tmp.replace(dest)
    return {
        "path": str(dest),
        "downloaded": True,
        "bytes": dest.stat().st_size,
        "sha256": sha256_file(dest),
        "url": url,
    }


def download_dataverse_sources(session: requests.Session, force: bool) -> dict[str, Any]:
    manifest: dict[str, Any] = {}
    for source_name, spec in DATAVERSE_FILES.items():
        print(f"Downloading Dataverse source: {source_name} ({spec['filename']})", flush=True)
        file_id = get_dataverse_file_id(session, spec["persistent_id"], spec["filename"])
        url = f"{DATAVERSE_API}/access/datafile/{file_id}"
        result = download_file(session, url, spec["raw_path"], force=force)
        result.update(
            {
                "persistent_id": spec["persistent_id"],
                "filename": spec["filename"],
                "source_url": spec["source_url"],
                "dataverse_file_id": file_id,
            }
        )
        manifest[source_name] = result
    return manifest


def fetch_wdi_country_metadata(session: requests.Session, force: bool) -> dict[str, Any]:
    dest = DATA_RAW / "wdi" / "countries.json"
    if dest.exists() and not force:
        payload = json.loads(dest.read_text(encoding="utf-8"))
    else:
        print("Downloading WDI country metadata", flush=True)
        url = "https://api.worldbank.org/v2/country"
        response = session.get(url, params={"format": "json", "per_page": 400}, timeout=90)
        response.raise_for_status()
        payload = response.json()
        write_json(dest, payload)
    return {
        "path": str(dest),
        "bytes": dest.stat().st_size,
        "sha256": sha256_file(dest),
        "url": "https://api.worldbank.org/v2/country?format=json&per_page=400",
    }


def fetch_wdi_indicator(
    session: requests.Session,
    indicator: str,
    variable: str,
    force: bool,
) -> dict[str, Any]:
    dest = DATA_RAW / "wdi" / f"{indicator}.json"
    if dest.exists() and dest.stat().st_size > 0 and not force:
        return {
            "path": str(dest),
            "downloaded": False,
            "bytes": dest.stat().st_size,
            "sha256": sha256_file(dest),
            "indicator": indicator,
            "variable": variable,
        }

    print(f"Downloading WDI indicator: {indicator} -> {variable}", flush=True)
    url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}"
    per_page = 1000
    page = 1
    metadata: dict[str, Any] | None = None
    rows: list[dict[str, Any]] = []
    while True:
        params = {
            "format": "json",
            "per_page": per_page,
            "page": page,
            "date": f"{START_YEAR}:{END_YEAR}",
        }
        response = session.get(url, params=params, timeout=120)
        if response.status_code >= 400:
            raise RuntimeError(
                f"WDI request failed for {indicator} with {response.status_code}: {response.text[:500]}"
            )
        payload = response.json()
        if not isinstance(payload, list) or len(payload) < 2:
            raise RuntimeError(f"Unexpected WDI payload for {indicator}: {str(payload)[:500]}")
        metadata = payload[0]
        rows.extend(payload[1] or [])
        pages = int(metadata.get("pages") or 1)
        if page >= pages:
            break
        page += 1
        time.sleep(0.15)
    payload = [metadata or {}, rows]
    write_json(dest, payload)
    time.sleep(0.3)
    return {
        "path": str(dest),
        "downloaded": True,
        "bytes": dest.stat().st_size,
        "sha256": sha256_file(dest),
        "indicator": indicator,
        "variable": variable,
        "url": response.url,
    }


def download_wdi_sources(session: requests.Session, force: bool) -> dict[str, Any]:
    manifest: dict[str, Any] = {"countries": fetch_wdi_country_metadata(session, force=force)}
    for indicator, variable in WDI_INDICATORS.items():
        manifest[indicator] = fetch_wdi_indicator(session, indicator, variable, force=force)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Download raw data for the growth factors project.")
    parser.add_argument("--force", action="store_true", help="Redownload files even when raw files exist.")
    parser.add_argument(
        "--source",
        choices=("all", "dataverse", "wdi"),
        default="all",
        help="Limit downloads to one source family.",
    )
    args = parser.parse_args()

    ensure_dirs()
    session = make_session()
    manifest: dict[str, Any] = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": {},
    }
    if args.source in ("all", "dataverse"):
        manifest["sources"]["dataverse"] = download_dataverse_sources(session, force=args.force)
    if args.source in ("all", "wdi"):
        manifest["sources"]["wdi"] = download_wdi_sources(session, force=args.force)

    write_json(DATA_RAW / "source_manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
