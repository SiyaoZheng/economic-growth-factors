# Validation Report

Generated at: 2026-07-04T03:48:56.481320+00:00

## Checks

- `iso3 + year` unique in outcome panel: pass
- `iso3 + year` unique in growth panel: pass
- no final panel row before 1960: pass
- annual, five-year, and ten-year growth formulas rebuild from `log_gdp_pc`: pass
- extreme annual growth rows written to `reports/extreme_growth_annual.csv`
- source discrepancy rows written to `reports/source_consistency.csv`

## Panel Sizes

- outcome rows: 11840
- growth rows: 11840
- countries in outcome panel: 185
- year range: 1960-2023

## Source Consistency

- PWT-WDI overlap rows: 9531
- PWT-WDI annual growth correlation: 0.8367572684950921
- PWT-Maddison overlap rows: 9088
- PWT-Maddison annual growth correlation: 0.8582571208355241
- large discrepancy rows: 385

## Output Hashes

```json
{
  "data/processed/outcome_panel_1960plus.parquet": "255c5202b03cfea03a82dfa37df8b1ce5f34edab068fde22d1bb87af1d0e44c5",
  "data/processed/outcome_panel_1960plus.csv": "4256028423e8b2d521bf0b1ca0d88ab5e53f75f4492026d4ba6f84985441fb37",
  "data/processed/growth_panel_1960plus.parquet": "c1b2f59a402538f89c21139f5680b174d8ea919a067f66e9c89520c139e560e1",
  "data/processed/growth_panel_1960plus.csv": "77951772fea2236efc0c11a1819d148c108ec1c89fdbb8342bd689e885e37f30"
}
```
