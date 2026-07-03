from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Iterable

import pandas as pd
import polars as pl

from config import (
    DATA_INTERIM,
    DATA_PROCESSED,
    DATA_RAW,
    DATAVERSE_FILES,
    REPORTS,
    START_YEAR,
    WDI_INDICATORS,
    ensure_dirs,
)


PRIMARY_COLUMNS = [
    "iso3",
    "country",
    "year",
    "source_outcome",
    "gdp_pc",
    "log_gdp_pc",
    "growth_annual",
    "growth_5yr",
    "growth_10yr",
    "population",
    "sample_flag_1960plus",
]


def read_excel_sheet(path: Path, required_columns: Iterable[str]) -> pd.DataFrame:
    xls = pd.ExcelFile(path)
    required = {col.lower() for col in required_columns}
    for sheet_name in xls.sheet_names:
        frame = pd.read_excel(path, sheet_name=sheet_name)
        frame.columns = [str(col).strip().lower() for col in frame.columns]
        if required.issubset(set(frame.columns)):
            return frame
    raise RuntimeError(f"No sheet in {path} contains required columns: {sorted(required)}")


def require_raw_inputs() -> None:
    missing = [
        str(spec["raw_path"])
        for spec in DATAVERSE_FILES.values()
        if not spec["raw_path"].exists()
    ]
    missing.extend(
        str(DATA_RAW / "wdi" / f"{indicator}.json")
        for indicator in WDI_INDICATORS
        if not (DATA_RAW / "wdi" / f"{indicator}.json").exists()
    )
    if not (DATA_RAW / "wdi" / "countries.json").exists():
        missing.append(str(DATA_RAW / "wdi" / "countries.json"))
    if missing:
        raise FileNotFoundError("Missing raw inputs. Run scripts/download_data.py first:\n" + "\n".join(missing))


def add_growth_columns(df: pl.DataFrame, value_col: str = "log_gdp_pc") -> pl.DataFrame:
    out = df
    for lag, name in [(1, "growth_annual"), (5, "growth_5yr"), (10, "growth_10yr")]:
        lagged = (
            df.select(
                "iso3",
                (pl.col("year") + lag).alias("year"),
                pl.col(value_col).alias(f"{value_col}_lag{lag}"),
            )
            .filter(pl.col(f"{value_col}_lag{lag}").is_not_null())
        )
        out = out.join(lagged, on=["iso3", "year"], how="left")
        out = out.with_columns(
            ((pl.col(value_col) - pl.col(f"{value_col}_lag{lag}")) / lag).alias(name)
        ).drop(f"{value_col}_lag{lag}")
    return out


def add_lagged_controls(df: pl.DataFrame, control_cols: list[str]) -> pl.DataFrame:
    lagged = df.select(
        "iso3",
        (pl.col("year") + 1).alias("year"),
        *[pl.col(col).alias(f"{col}_lag1") for col in control_cols if col in df.columns],
    )
    return df.join(lagged, on=["iso3", "year"], how="left")


def clean_pwt() -> pl.DataFrame:
    raw = read_excel_sheet(DATAVERSE_FILES["pwt"]["raw_path"], ["countrycode", "country", "year", "rgdpna", "pop"])
    frame = pl.from_pandas(raw)
    optional_map = {
        "hc": "pwt_human_capital_index",
        "rtfpna": "pwt_tfp",
        "csh_i": "pwt_investment_share",
        "csh_x": "pwt_export_share",
        "csh_m": "pwt_import_share",
    }
    select_exprs = [
        pl.col("countrycode").cast(pl.String).str.strip_chars().str.to_uppercase().alias("iso3"),
        pl.col("country").cast(pl.String).str.strip_chars().alias("country"),
        pl.col("year").cast(pl.Int32).alias("year"),
        pl.col("rgdpna").cast(pl.Float64, strict=False).alias("pwt_rgdpna"),
        pl.col("pop").cast(pl.Float64, strict=False).alias("pwt_population_millions"),
    ]
    for source, target in optional_map.items():
        if source in frame.columns:
            select_exprs.append(pl.col(source).cast(pl.Float64, strict=False).alias(target))

    out = (
        frame.select(select_exprs)
        .filter(pl.col("iso3").str.len_chars() == 3)
        .filter(pl.col("year") >= 1950)
        .with_columns(
            pl.when((pl.col("pwt_rgdpna") > 0) & (pl.col("pwt_population_millions") > 0))
            .then(pl.col("pwt_rgdpna") / pl.col("pwt_population_millions"))
            .otherwise(None)
            .alias("gdp_pc"),
            (pl.col("pwt_population_millions") * 1_000_000).alias("population"),
            pl.lit("pwt110_rgdpna_per_capita").alias("source_outcome"),
        )
        .with_columns(
            pl.when(pl.col("gdp_pc") > 0)
            .then(pl.col("gdp_pc").log())
            .otherwise(None)
            .alias("log_gdp_pc")
        )
        .sort(["iso3", "year"])
    )
    out = add_growth_columns(out)
    out.write_parquet(DATA_INTERIM / "pwt_clean.parquet")
    out.write_csv(DATA_INTERIM / "pwt_clean.csv")
    return out


def clean_maddison() -> pl.DataFrame:
    raw = read_excel_sheet(DATAVERSE_FILES["maddison"]["raw_path"], ["countrycode", "country", "year", "gdppc"])
    frame = pl.from_pandas(raw)
    out = (
        frame.select(
            pl.col("countrycode").cast(pl.String).str.strip_chars().str.to_uppercase().alias("iso3"),
            pl.col("country").cast(pl.String).str.strip_chars().alias("maddison_country"),
            pl.col("year").cast(pl.Int32).alias("year"),
            pl.col("gdppc").cast(pl.Float64, strict=False).alias("maddison_gdp_pc"),
        )
        .filter(pl.col("iso3").str.len_chars() == 3)
        .filter(pl.col("year") >= 1950)
        .with_columns(
            pl.when(pl.col("maddison_gdp_pc") > 0)
            .then(pl.col("maddison_gdp_pc").log())
            .otherwise(None)
            .alias("maddison_log_gdp_pc")
        )
        .sort(["iso3", "year"])
    )
    out = add_growth_columns(out, value_col="maddison_log_gdp_pc").rename(
        {
            "growth_annual": "maddison_growth_annual",
            "growth_5yr": "maddison_growth_5yr",
            "growth_10yr": "maddison_growth_10yr",
        }
    )
    out.write_parquet(DATA_INTERIM / "maddison_clean.parquet")
    out.write_csv(DATA_INTERIM / "maddison_clean.csv")
    return out


def country_metadata() -> set[str]:
    payload = json.loads((DATA_RAW / "wdi" / "countries.json").read_text(encoding="utf-8"))
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    return {
        row.get("id")
        for row in rows
        if row.get("id")
        and len(row.get("id", "")) == 3
        and row.get("region", {}).get("value") != "Aggregates"
    }


def clean_wdi() -> pl.DataFrame:
    valid_iso3 = country_metadata()
    long_frames: list[pl.DataFrame] = []
    for indicator, variable in WDI_INDICATORS.items():
        payload = json.loads((DATA_RAW / "wdi" / f"{indicator}.json").read_text(encoding="utf-8"))
        rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        records = [
            {
                "iso3": row.get("countryiso3code"),
                "country_wdi": row.get("country", {}).get("value"),
                "year": int(row["date"]) if row.get("date") else None,
                "indicator": indicator,
                "variable": variable,
                "value": row.get("value"),
            }
            for row in rows
        ]
        frame = pl.DataFrame(records) if records else pl.DataFrame(
            schema={
                "iso3": pl.String,
                "country_wdi": pl.String,
                "year": pl.Int32,
                "indicator": pl.String,
                "variable": pl.String,
                "value": pl.Float64,
            }
        )
        frame = frame.with_columns(
            pl.col("iso3").cast(pl.String).str.strip_chars().str.to_uppercase(),
            pl.col("year").cast(pl.Int32, strict=False),
            pl.col("value").cast(pl.Float64, strict=False),
        ).filter(pl.col("iso3").is_in(valid_iso3))
        long_frames.append(frame)

    long = pl.concat(long_frames, how="vertical")
    wide = (
        long.select("iso3", "country_wdi", "year", "variable", "value")
        .pivot(index=["iso3", "country_wdi", "year"], on="variable", values="value", aggregate_function="first")
        .sort(["iso3", "year"])
    )
    if {"wdi_exports_gdp", "wdi_imports_gdp"}.issubset(set(wide.columns)):
        wide = wide.with_columns(
            pl.when(pl.col("wdi_exports_gdp").is_not_null() & pl.col("wdi_imports_gdp").is_not_null())
            .then(pl.col("wdi_exports_gdp") + pl.col("wdi_imports_gdp"))
            .otherwise(None)
            .alias("wdi_trade_gdp")
        )
    wide.write_parquet(DATA_INTERIM / "wdi_clean.parquet")
    wide.write_csv(DATA_INTERIM / "wdi_clean.csv")
    return wide


def coverage_rows(df: pl.DataFrame, variables: list[str], stage: str) -> list[dict[str, object]]:
    rows = []
    for variable in variables:
        if variable not in df.columns:
            continue
        non_null = df.filter(pl.col(variable).is_not_null())
        rows.append(
            {
                "stage": stage,
                "variable": variable,
                "rows": df.height,
                "non_missing_rows": non_null.height,
                "non_missing_pct": round(non_null.height / df.height * 100, 2) if df.height else 0.0,
                "countries": non_null.select(pl.col("iso3").n_unique()).item() if non_null.height else 0,
                "min_year": non_null.select(pl.col("year").min()).item() if non_null.height else None,
                "max_year": non_null.select(pl.col("year").max()).item() if non_null.height else None,
            }
        )
    return rows


def write_coverage_report(coverage: pl.DataFrame) -> None:
    coverage.write_csv(REPORTS / "coverage_table.csv")
    rows = coverage.to_dicts()
    table_rows = "\n".join(
        "<tr>"
        + "".join(f"<td>{html.escape(str(row.get(col, '')))}</td>" for col in coverage.columns)
        + "</tr>"
        for row in rows
    )
    header = "".join(f"<th>{html.escape(col)}</th>" for col in coverage.columns)
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Growth Factors Coverage Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #202124; }}
    h1 {{ font-size: 24px; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border: 1px solid #d0d7de; padding: 6px 8px; text-align: left; }}
    th {{ background: #f6f8fa; position: sticky; top: 0; }}
    tr:nth-child(even) {{ background: #fbfbfb; }}
  </style>
</head>
<body>
  <h1>Growth Factors Coverage Report</h1>
  <p>Rows describe non-missing coverage after applying the 1960+ sample rule.</p>
  <table>
    <thead><tr>{header}</tr></thead>
    <tbody>{table_rows}</tbody>
  </table>
</body>
</html>
"""
    (REPORTS / "coverage_report.html").write_text(document, encoding="utf-8")


def build_panels() -> None:
    ensure_dirs()
    require_raw_inputs()

    pwt = clean_pwt()
    maddison = clean_maddison()
    wdi = clean_wdi()

    pwt_1960 = (
        pwt.filter(pl.col("year") >= START_YEAR)
        .with_columns(pl.lit(True).alias("sample_flag_1960plus"))
        .sort(["iso3", "year"])
    )
    outcome = pwt_1960.select([col for col in PRIMARY_COLUMNS if col in pwt_1960.columns])
    outcome.write_parquet(DATA_PROCESSED / "outcome_panel_1960plus.parquet")
    outcome.write_csv(DATA_PROCESSED / "outcome_panel_1960plus.csv")

    maddison_keep = maddison.select(
        "iso3",
        "year",
        "maddison_gdp_pc",
        "maddison_growth_annual",
        "maddison_growth_5yr",
        "maddison_growth_10yr",
    )
    wdi_keep = wdi.drop("country_wdi") if "country_wdi" in wdi.columns else wdi
    growth = outcome.join(maddison_keep, on=["iso3", "year"], how="left").join(
        wdi_keep, on=["iso3", "year"], how="left"
    )

    controls = [
        "pwt_human_capital_index",
        "pwt_tfp",
        "pwt_investment_share",
        "pwt_export_share",
        "pwt_import_share",
    ]
    pwt_controls = pwt_1960.select("iso3", "year", *[col for col in controls if col in pwt_1960.columns])
    growth = growth.join(pwt_controls, on=["iso3", "year"], how="left")
    lag_candidates = [
        col
        for col in growth.columns
        if col.startswith("wdi_")
        or col in controls
    ]
    growth = add_lagged_controls(growth, lag_candidates).sort(["iso3", "year"])
    growth.write_parquet(DATA_PROCESSED / "growth_panel_1960plus.parquet")
    growth.write_csv(DATA_PROCESSED / "growth_panel_1960plus.csv")

    coverage = pl.DataFrame(
        coverage_rows(outcome, [col for col in outcome.columns if col not in {"iso3", "country", "year"}], "outcome")
        + coverage_rows(growth, [col for col in growth.columns if col not in {"iso3", "country", "year"}], "growth")
    )
    write_coverage_report(coverage)

    print(f"Wrote {outcome.height:,} outcome rows and {growth.height:,} growth rows.")


if __name__ == "__main__":
    build_panels()
