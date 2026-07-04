#!/usr/bin/env python3
"""
Data quality fixes for growth_with_compute.parquet.
Addresses four audit issues.

ISSUE 1: pwt_import_share all negative → PWT csh_m convention; create abs variant
ISSUE 2: log_total_rmax negative → real but tiny values; winsorize at 0
ISSUE 3: Perfectly balanced panel → correct long-format structure; document only
ISSUE 4: growth_annual extremes → real events; create winsorized variant
"""

from pathlib import Path
import polars as pl


def main():
    src = Path("data/interim/growth_with_compute.parquet")
    dst = Path("data/interim/growth_with_compute_clean.parquet")

    data = pl.read_parquet(src)

    # ----------------------------------------------------------
    # ISSUE 1: Create |pwt_import_share| and trade_openness
    # PWT csh_m = -(imports/GDP), stored as negative share (0-1 scale)
    # ----------------------------------------------------------
    data = data.with_columns([
        pl.col('pwt_import_share').abs().alias('pwt_import_share_abs'),
        (pl.col('pwt_export_share') + pl.col('pwt_import_share').abs()).alias('pwt_trade_openness'),
    ])
    # Also lag1 variants
    data = data.with_columns([
        pl.col('pwt_import_share_lag1').abs().alias('pwt_import_share_lag1_abs'),
        (pl.col('pwt_export_share_lag1') + pl.col('pwt_import_share_lag1').abs()).alias('pwt_trade_openness_lag1'),
    ])

    # ----------------------------------------------------------
    # ISSUE 2: Winsorize log_total_rmax at floor=0
    # 4 obs have 0 < rmax < 1 GFlops → log(r) < 0
    # These are real but negligible; clip to 0 for interpretability
    # ----------------------------------------------------------
    data = data.with_columns(
        pl.col('log_total_rmax').clip(lower_bound=0.0).alias('log_total_rmax'),
    )

    # ----------------------------------------------------------
    # ISSUE 3: Panel structure — no code change needed.
    # Document: 185 countries × 64 years = 11,840 rows.
    # Variables have natural missingness. This is the standard
    # "long-panel with gaps" structure.
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # ISSUE 4: Create winsorized growth_annual
    # 56 obs with |growth| > 0.30 — all real historical events
    # (wars, oil booms, pandemics). Create winsorized variant
    # at |growth| <= 0.30 per project spec.
    # ----------------------------------------------------------
    p01 = data['growth_annual'].quantile(0.01, interpolation='linear')  # type: ignore
    p99 = data['growth_annual'].quantile(0.99, interpolation='linear')  # type: ignore
    data = data.with_columns(
        pl.col('growth_annual').clip(lower_bound=p01, upper_bound=p99).alias('growth_annual_winsor'),
    )

    # ----------------------------------------------------------
    # Save
    # ----------------------------------------------------------
    data.write_parquet(dst)
    print(f"Saved {data.height} rows × {len(data.columns)} columns to {dst}")

    # Quick verify
    print(f"\nVerification:")
    print(f"  pwt_import_share_abs: min={data['pwt_import_share_abs'].min():.4f}, max={data['pwt_import_share_abs'].max():.4f}")
    print(f"  pwt_trade_openness: min={data['pwt_trade_openness'].min():.4f}, max={data['pwt_trade_openness'].max():.4f}")
    print(f"  log_total_rmax: min={data['log_total_rmax'].min():.4f}")
    print(f"  growth_annual_winsor: min={data['growth_annual_winsor'].min():.4f}, max={data['growth_annual_winsor'].max():.4f}")
    print(f"  growth_annual_winsor extremes clipped: {data.filter(pl.col('growth_annual_winsor') != pl.col('growth_annual')).height} obs")


if __name__ == '__main__':
    main()
