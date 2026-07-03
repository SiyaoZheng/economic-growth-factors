# 各国经济增长影响因素

This repository builds a reproducible country-year panel for studying factors associated with national economic growth since 1960.

## Current Pipeline

The first milestone downloads and processes:

- Penn World Table 11.0 (primary GDP per capita and economic structure source)
- Maddison Project Database 2023 (long-run GDP per capita validation source)
- World Bank WDI indicators (official growth, population, and economic controls)

Planned follow-up modules are documented for V-Dem, QoG, CEPII GeoDist, Barro-Lee, and UN WPP.

## Run

```bash
python3 scripts/download_data.py
python3 scripts/build_panels.py
python3 scripts/validate_outputs.py
```

Or run the full sequence:

```bash
python3 scripts/run_pipeline.py
```

## Outputs

- `data/processed/outcome_panel_1960plus.parquet`
- `data/processed/outcome_panel_1960plus.csv`
- `data/processed/growth_panel_1960plus.parquet`
- `data/processed/growth_panel_1960plus.csv`
- `docs/data_inventory.md`
- `docs/variable_dictionary.csv`
- `reports/coverage_report.html`
- `reports/validation_report.md`

Raw downloads are retained under `data/raw/` and are not edited by processing scripts.
