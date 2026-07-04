# Research Starter Packet

## Research Question
*Provisional.* What factors are empirically associated with national economic growth since 1960, and how sensitive are these associations to measurement sources, sample composition, and model specification?

## Materials Inventory

### Usable
- Penn World Table 11.0 (1960-2023): GDP per capita, population, human capital index, TFP, investment & trade shares — **already processed in pipeline**
- Maddison Project Database 2023 (1960-2022): GDP per capita validation source — **processed, merged**
- WDI current API snapshot: official growth, population, trade, investment, sector shares, urbanization, life expectancy — **processed, lagged controls available**
- Full Python pipeline: `download_data.py` → `build_panels.py` → `validate_outputs.py`
- Variable dictionary (`docs/variable_dictionary.csv`) with 30+ variables, coverage years, lag & missingness rules
- Validation suite: source consistency checks, extreme growth flagging, hash tracking

### Uncertain
- **WDI raw data is incomplete**: only 4 of 10 indicator JSON files are downloaded (missing imports, investment, agriculture, industry, services, urbanization, life expectancy)
- Pipeline has never been fully run — `data/processed/` and `reports/` are empty

### Unavailable
- V-Dem v16, QoG Standard, CEPII GeoDist, Barro-Lee, UN WPP 2024 — all planned, none implemented

### Off-limits
- Data in `data/raw/` is read-only; no manual Excel/Stata edits

## Evidence Affordance
Current materials can support descriptive growth correlations and initial model specification testing (annual / 5-year / 10-year windows), with WDI-based structural controls. Cannot yet support institutional (V-Dem, QoG), geographic (CEPII), educational (Barro-Lee), or demographic (UN WPP) analyses. Source consistency between PWT / WDI / Maddison can be quantified immediately.

## Route Cards

### R1: Core Specification & Source Validation
| Field | Value |
|---|---|
| `research_question` | How do growth correlations differ across PWT, WDI, and Maddison measurement sources, and how sensitive are benchmark panel estimates to sample exclusions (China, high-income OECD, extreme growth observations)? |
| `study_type` | descriptive / replication |
| `unit_of_analysis` | country-year |
| `materials_available` | PWT 11.0, WDI incomplete (4/10 indicators), Maddison 2023, full pipeline scripts, validation suite |
| `materials_gap` | 6 missing WDI indicators; pipeline not yet run |
| `first_action` | Run `scripts/run_pipeline.py` to produce all processed outputs, then inspect coverage report and source consistency output |
| `expected_first_output` | `data/processed/growth_panel_1960plus.parquet`, `reports/coverage_report.html`, `reports/source_consistency.csv`, `reports/validation_report.md` |
| `failure_signal` | Pipeline errors, zero overlap between PWT and WDI, or >20% large source discrepancies |
| `feasibility_status` | `try_now` |
| `stop_reason` | Do not estimate models until pipeline completes and all source variables are verified |
| `researcher_decision_needed` | Whether to continue with partial WDI coverage or extend WDI download; whether growth_annual, growth_5yr, or growth_10yr should be the primary outcome |
| `next_skill_route` | `research-data-builder` (to extend WDI coverage or add new sources) |

### R2: WDI Coverage Extension
| Field | Value |
|---|---|
| `research_question` | Can the full WDI indicator set be downloaded to provide structural controls (investment, sector shares, urbanization, life expectancy)? |
| `study_type` | data pipeline extension |
| `unit_of_analysis` | country-year |
| `materials_available` | Existing `download_data.py` with WDI indicator codes in `config.py`; wbdata package in `requirements.txt` |
| `materials_gap` | 6 indicators not yet downloaded: imports, investment, agriculture, industry, services, urbanization, life expectancy |
| `first_action` | Read `scripts/download_data.py` and diagnose why only 4/10 WDI indicators were downloaded |
| `expected_first_output` | Fixed download script and all 10 WDI indicators in `data/raw/wdi/` |
| `failure_signal` | API rate limiting, missing indicator codes, country coverage gaps |
| `feasibility_status` | `try_now` |
| `stop_reason` | Downloading data is safe; stop after pipeline re-run confirms all 10 indicators are present |
| `researcher_decision_needed` | Whether to add additional WDI indicators (e.g., inflation, FDI, education enrollment) |
| `next_skill_route` | `research-data-builder` |

### R3: Planned Source Expansion
| Field | Value |
|---|---|
| `research_question` | Can institutional (V-Dem, QoG), geographic (CEPII), educational (Barro-Lee), and demographic (UN WPP) modules be integrated into the existing panel pipeline? |
| `study_type` | data pipeline design |
| `unit_of_analysis` | country-year (or country, for time-invariant CEPII data) |
| `materials_available` | Variable definitions and URL references in `docs/variable_dictionary.csv`; source inventory in `docs/data_inventory.md` |
| `materials_gap` | No raw data downloaded; no processing scripts written; no merge strategy coded |
| `first_action` | Design the integration plan: download APIs, file formats, merge keys, and missingness rules for one source (e.g., V-Dem v16) |
| `expected_first_output` | `docs/vdem_integration_plan.md` with download specification, processing logic, and coverage expectations |
| `failure_signal` | V-Dem API requires authentication or is not freely available; country coverage mismatch with existing panel |
| `feasibility_status` | `needs_author_decision` |
| `stop_reason` | Adding planned sources is methodologically important but requires author prioritization before committing to implementation |
| `researcher_decision_needed` | Which of the five planned sources to prioritize; whether to implement one at a time or design a multi-source merger |
| `next_skill_route` | `research-data-builder` |

## Minimum Viable Study

**Start with R1 + R2 in sequence.** The smallest viable output is:

1. **Run the pipeline** (R1 first action) to produce the baseline country-year panel and validation diagnostics.
2. **Fix and extend WDI downloads** (R2) so structural controls are complete.
3. **Re-run pipeline** and produce a **first specification table**: country + year FE, single control at a time (parsimonious), with `growth_annual` / `growth_5yr` / `growth_10yr` as alternating outcomes.

This gives Adrian:
- a working, reproducible end-to-end pipeline
- source consistency evidence (PWT vs WDI vs Maddison)
- a first table shell showing what each control does to the growth correlation
- clear evidence of which observations are driving results

## First Observation
*(to be filled after pipeline is run)*

## Stop Reason
Do not write paper prose, abstracts, or full model batteries until the pipeline produces stable output and the researcher confirms the R1 specification direction.

## Researcher Decision Needed
1. **Primary outcome**: annual growth, 5-year average, or 10-year average? (Each has different noise and time-horizon properties for the research question.)
2. **Source priority**: Fix WDI download first (R2) or start with whatever is already available (R1 only)?
3. **Extreme growth handling**: Confirm the 0.30 log-point threshold or adjust it?

## Handoff Prompt

```text
Use $research-data-builder.

Route: R1 + R2 in sequence.

Step 1: Run `python3 scripts/run_pipeline.py` from the project root. Report any errors. If successful, inspect:
- reports/coverage_report.html (variable coverage)
- reports/source_consistency.csv (PWT-WDI-Maddison discrepancies)
- reports/extreme_growth_annual.csv (outliers)

Step 2: Read scripts/download_data.py, diagnose why only 4 of 10 WDI indicators exist in data/raw/wdi/, and fix the script to download all 10. Re-run pipeline.

Step 3: Report coverage improvement and any new discrepancies.

Goals:
- Produce a verified growth_panel_1960plus.parquet.
- Report country count, year range, and variable coverage table.
- Flag any iso3 key conflicts, >10% source discrepancies, or missing WDI indicators.

Do not estimate regression models.
```

## Next Skill Route
`research-data-builder`
