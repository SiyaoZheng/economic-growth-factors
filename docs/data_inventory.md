# Data Inventory

This inventory is the source-of-record for dataset provenance and first-pass coverage expectations.

## Implemented In First Milestone

| Source | Version | Role | Access | Local Raw File | Status |
|---|---:|---|---|---|---|
| Penn World Table | 11.0 | Primary GDP per capita, population, human capital, TFP, investment and trade shares | Dataverse DOI `10.34894/FABVLR` | `data/raw/pwt/pwt110.xlsx` | Implemented |
| Maddison Project Database | 2023 | GDP per capita validation source | Dataverse DOI `10.34894/INZBF2` | `data/raw/maddison/mpd2023_web.xlsx` | Implemented |
| World Development Indicators | Current API snapshot | Official GDP growth, population, trade, investment, sector shares, urbanization, life expectancy | World Bank API | `data/raw/wdi/*.json` | Implemented (8/10 indicators; urbanization & life expectancy blocked) |

## Planned Follow-Up Modules

| Source | Role | Default Use | Status |
|---|---|---|---|
| V-Dem v16 | Democracy, institutions, political competition, executive constraints | Lagged one year, merged on `iso3 + year` | Planned |
| QoG Standard Time-Series | Governance, corruption, state capacity, regime indicators | Lagged one year, merged on `iso3 + year` | Planned |
| CEPII GeoDist | Distance, landlocked status, language, border, colonial relationship | Time-invariant country attributes and bilateral-derived accessibility | Planned |
| Barro-Lee | Educational attainment and schooling structure | Five-year source values forward-filled within a five-year window only | Planned |
| UN WPP 2024 | Age structure, population, life expectancy | Lagged one year for demographic covariates | Planned |

## Sample Rules

- Final analysis panels keep `year >= 1960`.
- Pre-1960 data may be used internally only to compute lagged growth rates for 1960 onward.
- The merge key is `iso3 + year`.
- Country entities that cannot be safely mapped to ISO3 must be handled in `country_crosswalk.csv`; no silent mapping is allowed.
- No mean imputation and no cross-country interpolation are allowed.

## Generated Diagnostics

The pipeline writes these diagnostics after processing:

- `reports/coverage_report.html`
- `reports/source_consistency.csv`
- `reports/extreme_growth_annual.csv`
- `reports/output_hashes.json`
- `reports/validation_report.md`

## Blocked / Pending Download

| Indicator | Code | Blocked Reason |
|---|---|---|
| Urban population share | `SP.URB.TOTL.IN.ZS` | Raw file not yet downloaded (network timeout) |
| Life expectancy at birth | `SP.DYN.LE00.IN` | Raw file not yet downloaded (network timeout) |
