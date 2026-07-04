from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from config import DATA_PROCESSED, OUTPUTS, START_YEAR, ensure_dirs


OUTPUT_FILES = [
    DATA_PROCESSED / "outcome_panel_1960plus.parquet",
    DATA_PROCESSED / "outcome_panel_1960plus.csv",
    DATA_PROCESSED / "growth_panel_1960plus.parquet",
    DATA_PROCESSED / "growth_panel_1960plus.csv",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_unique_key(df: pl.DataFrame, name: str) -> None:
    duplicate_count = (
        df.group_by(["iso3", "year"])
        .len()
        .filter(pl.col("len") > 1)
        .height
    )
    if duplicate_count:
        raise AssertionError(f"{name} has duplicate iso3 + year keys: {duplicate_count}")


def assert_year_floor(df: pl.DataFrame, name: str) -> None:
    min_year = df.select(pl.col("year").min()).item()
    if min_year < START_YEAR:
        raise AssertionError(f"{name} contains year < {START_YEAR}: min year {min_year}")


def check_growth_formula(outcome: pl.DataFrame) -> None:
    source = outcome.select("iso3", "year", "log_gdp_pc", "growth_annual", "growth_5yr", "growth_10yr")
    for lag, col in [(1, "growth_annual"), (5, "growth_5yr"), (10, "growth_10yr")]:
        lagged = source.select(
            "iso3",
            (pl.col("year") + lag).alias("year"),
            pl.col("log_gdp_pc").alias("lag_log_gdp_pc"),
        )
        checked = (
            source.join(lagged, on=["iso3", "year"], how="left")
            .with_columns(((pl.col("log_gdp_pc") - pl.col("lag_log_gdp_pc")) / lag).alias("expected"))
            .filter(pl.col("expected").is_not_null() & pl.col(col).is_not_null())
            .with_columns((pl.col(col) - pl.col("expected")).abs().alias("diff"))
        )
        max_diff = checked.select(pl.col("diff").max()).item()
        if max_diff is not None and max_diff > 1e-12:
            raise AssertionError(f"{col} formula mismatch; max diff {max_diff}")


def write_extreme_growth(growth: pl.DataFrame) -> None:
    extreme = (
        growth.filter(pl.col("growth_annual").is_not_null() & (pl.col("growth_annual").abs() > 0.30))
        .select("iso3", "country", "year", "growth_annual", "gdp_pc", "population")
        .sort(["growth_annual"], descending=True)
    )
    extreme.write_csv(OUTPUTS / "data_checks" / "extreme_growth_annual.csv")


def write_source_consistency(growth: pl.DataFrame) -> dict[str, float | int | None]:
    has_wdi_growth = "wdi_gdp_growth_annual_pct" in growth.columns
    select_cols = ["iso3", "country", "year", "growth_annual"]
    if has_wdi_growth:
        select_cols.append("wdi_gdp_growth_annual_pct")
    select_cols.append("maddison_growth_annual")
    comparisons = growth.select(select_cols)
    if has_wdi_growth:
        comparisons = comparisons.with_columns(
            (pl.col("wdi_gdp_growth_annual_pct") / 100).alias("wdi_growth_decimal"),
        )
    comparisons = comparisons.with_columns(
        (pl.col("growth_annual") - pl.col("maddison_growth_annual")).abs().alias("abs_diff_maddison"),
    )
    if has_wdi_growth:
        comparisons = comparisons.with_columns(
            (pl.col("growth_annual") - (pl.col("wdi_gdp_growth_annual_pct") / 100)).abs().alias("abs_diff_wdi"),
        )
    if has_wdi_growth:
        large = comparisons.filter(
            (pl.col("abs_diff_maddison") > 0.10) | (pl.col("abs_diff_wdi") > 0.10)
        ).sort(["abs_diff_wdi", "abs_diff_maddison"], descending=True)
    else:
        large = comparisons.filter(
            (pl.col("abs_diff_maddison") > 0.10)
        ).sort(["abs_diff_maddison"], descending=True)
    large.write_csv(OUTPUTS / "data_checks" / "source_consistency.csv")

    wdi_overlap = comparisons.filter(
        pl.col("growth_annual").is_not_null() & pl.col("wdi_growth_decimal").is_not_null()
    ) if has_wdi_growth else pl.DataFrame(schema={"growth_annual": pl.Float64, "wdi_growth_decimal": pl.Float64})
    maddison_overlap = comparisons.filter(
        pl.col("growth_annual").is_not_null() & pl.col("maddison_growth_annual").is_not_null()
    )
    return {
        "wdi_overlap_rows": wdi_overlap.height if has_wdi_growth else 0,
        "maddison_overlap_rows": maddison_overlap.height,
        "wdi_corr": wdi_overlap.select(pl.corr("growth_annual", "wdi_growth_decimal")).item()
        if (has_wdi_growth and wdi_overlap.height > 1)
        else None,
        "maddison_corr": maddison_overlap.select(pl.corr("growth_annual", "maddison_growth_annual")).item()
        if maddison_overlap.height > 1
        else None,
        "large_discrepancy_rows": large.height,
    }


def write_hashes() -> dict[str, str]:
    hashes = {str(path.relative_to(path.parents[2])): sha256_file(path) for path in OUTPUT_FILES if path.exists()}
    payload = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "hashes": hashes,
    }
    (OUTPUTS / "data_checks" / "output_hashes.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return hashes


def main() -> None:
    ensure_dirs()
    missing = [str(path) for path in OUTPUT_FILES if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing processed outputs:\n" + "\n".join(missing))

    outcome = pl.read_parquet(DATA_PROCESSED / "outcome_panel_1960plus.parquet")
    growth = pl.read_parquet(DATA_PROCESSED / "growth_panel_1960plus.parquet")

    assert_unique_key(outcome, "outcome_panel_1960plus")
    assert_unique_key(growth, "growth_panel_1960plus")
    assert_year_floor(outcome, "outcome_panel_1960plus")
    assert_year_floor(growth, "growth_panel_1960plus")
    check_growth_formula(outcome)
    write_extreme_growth(growth)
    consistency = write_source_consistency(growth)
    hashes = write_hashes()

    report = f"""# Validation Report

Generated at: {datetime.now(timezone.utc).isoformat()}

## Checks

- `iso3 + year` unique in outcome panel: pass
- `iso3 + year` unique in growth panel: pass
- no final panel row before {START_YEAR}: pass
- annual, five-year, and ten-year growth formulas rebuild from `log_gdp_pc`: pass
- extreme annual growth rows written to `outputs/data_checks/extreme_growth_annual.csv`
- source discrepancy rows written to `outputs/data_checks/source_consistency.csv`

## Panel Sizes

- outcome rows: {outcome.height}
- growth rows: {growth.height}
- countries in outcome panel: {outcome.select(pl.col("iso3").n_unique()).item()}
- year range: {outcome.select(pl.col("year").min()).item()}-{outcome.select(pl.col("year").max()).item()}

## Source Consistency

- PWT-WDI overlap rows: {consistency["wdi_overlap_rows"]}
- PWT-WDI annual growth correlation: {consistency["wdi_corr"]}
- PWT-Maddison overlap rows: {consistency["maddison_overlap_rows"]}
- PWT-Maddison annual growth correlation: {consistency["maddison_corr"]}
- large discrepancy rows: {consistency["large_discrepancy_rows"]}

## Output Hashes

```json
{json.dumps(hashes, indent=2)}
```
"""
    (OUTPUTS / "data_checks" / "validation_report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
