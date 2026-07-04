library(arrow)
library(fixest)
library(modelsummary)
library(tinytable)
library(dplyr)

# ============================================================
# Data loading and preparation
# ============================================================

# Load compute panel (has PWT lag1 controls + TOP500 compute variables)
compute_raw <- arrow::read_parquet("data/interim/growth_with_compute.parquet")

# Load growth panel only for WDI industry/services shares (interaction terms)
growth_raw <- arrow::read_parquet("data/processed/growth_panel_1960plus.parquet")
growth_raw <- growth_raw %>%
  filter(year >= 2015) %>%
  select(iso3, year, wdi_industry_value_added_gdp, wdi_services_value_added_gdp)

# Merge WDI interaction vars into compute panel, restrict to 2015+
df <- compute_raw %>%
  filter(year >= 2015) %>%
  left_join(growth_raw, by = c("iso3", "year")) %>%
  mutate(growth_pct = growth_annual * 100)

# OECD high-income list for robustness check
high_income_oecd <- c(
  "AUS","AUT","BEL","CAN","CHE","CYP","CZE","DEU","DNK","ESP","EST","FIN","FRA",
  "GBR","GRC","HUN","IRL","ISL","ISR","ITA","JPN","KOR","LTU","LUX","LVA",
  "MLT","NLD","NOR","NZL","POL","PRT","SVK","SVN","SWE","USA"
)

# Baseline controls (all PWT, lagged one year)
controls_base <- c("pwt_human_capital_index_lag1", "pwt_investment_share_lag1",
                    "pwt_tfp_lag1", "pwt_export_share_lag1", "pwt_import_share_lag1")

# ============================================================
# Table 1: Main effect + robustness
# ============================================================

t1_vars <- c("growth_pct", "log_total_rmax", controls_base)
est_t1 <- df[complete.cases(df[, t1_vars]), ]

cat(sprintf("\nTable 1 baseline: %d obs, %d countries, years %d\u2013%d, mean DV = %.2f%%\n",
            nrow(est_t1), length(unique(est_t1$iso3)),
            min(est_t1$year), max(est_t1$year),
            mean(est_t1$growth_pct, na.rm = TRUE)))

formula_base <- as.formula(paste("growth_pct ~ log_total_rmax +",
                                  paste(controls_base, collapse = " + "),
                                  "| iso3 + year"))

# (1) Baseline: all countries
m1_1 <- feols(formula_base, data = est_t1, cluster = ~iso3)

# (2) Excluding China
est_t1_nochn <- est_t1[est_t1$iso3 != "CHN", ]
m1_2 <- feols(formula_base, data = est_t1_nochn, cluster = ~iso3)

# (3) Excluding high-income OECD
est_t1_nooecd <- est_t1[!est_t1$iso3 %in% high_income_oecd, ]
m1_3 <- feols(formula_base, data = est_t1_nooecd, cluster = ~iso3)

# (4) Excluding extreme growth (|growth_annual| > 0.30)
est_t1_noext <- est_t1[abs(est_t1$growth_annual) <= 0.30, ]
m1_4 <- feols(formula_base, data = est_t1_noext, cluster = ~iso3)

coef_map_t1 <- c(
  log_total_rmax                   = "log(TOP500 Total Rmax)",
  pwt_human_capital_index_lag1     = "Human Capital Index (lagged)",
  pwt_investment_share_lag1         = "Investment Share (lagged)",
  pwt_tfp_lag1                      = "TFP (lagged)",
  pwt_export_share_lag1             = "Export Share (lagged)",
  pwt_import_share_lag1             = "Import Share (lagged)"
)

gof_map <- data.frame(
  raw   = c("nobs", "r2", "r2.within.adjusted"),
  clean = c("Observations", "R\u00b2", "Adj. Within R\u00b2"),
  fmt   = c(0, 3, 3)
)

notes_t1 <- c(
  "All models include country and year fixed effects. Standard errors clustered at country level in parentheses.",
  "Dependent variable: annual log GDP per capita growth \u00d7 100 (percentage points).",
  "Column (2): excluding China. Column (3): excluding 35 high-income OECD countries.",
  "Column (4): excluding observations where |growth_annual| > 0.30.",
  sprintf("Baseline estimation sample: %d obs, %d countries, years %d\u2013%d, mean DV = %.2f%%.",
          nrow(est_t1), length(unique(est_t1$iso3)), min(est_t1$year), max(est_t1$year),
          mean(est_t1$growth_pct)),
  "Growth computed from PWT 11.0 real GDP per capita, log-differenced annually. TOP500 total Rmax aggregated to country-year."
)

models_t1 <- list("(1)" = m1_1, "(2)" = m1_2, "(3)" = m1_3, "(4)" = m1_4)

tab1 <- modelsummary(models_t1,
  stars       = TRUE,
  coef_map    = coef_map_t1,
  gof_map     = gof_map,
  notes       = notes_t1,
  title       = "",
  output      = "tinytable"
)

html1 <- tinytable::save_tt(tab1, "html")
writeLines(html1, "reports/table1_main_effect.html")
cat("\nDone. reports/table1_main_effect.html written.\n")

# ============================================================
# Table 2: Channel interaction + robustness
# ============================================================

t2_vars <- c(t1_vars, "wdi_industry_value_added_gdp", "wdi_services_value_added_gdp")
est_t2 <- df[complete.cases(df[, t2_vars]), ]

cat(sprintf("\nTable 2 baseline: %d obs, %d countries, years %d\u2013%d, mean DV = %.2f%%\n",
            nrow(est_t2), length(unique(est_t2$iso3)),
            min(est_t2$year), max(est_t2$year),
            mean(est_t2$growth_pct, na.rm = TRUE)))

# Interaction formula: compute \u00d7 industry (automation) + compute \u00d7 services (new task)
formula_int <- as.formula(paste(
  "growth_pct ~ log_total_rmax +",
  "log_total_rmax:wdi_industry_value_added_gdp +",
  "log_total_rmax:wdi_services_value_added_gdp +",
  paste(controls_base, collapse = " + "),
  "| iso3 + year"
))

# (1) Baseline interaction
m2_1 <- feols(formula_int, data = est_t2, cluster = ~iso3)

# (2) Excluding China
est_t2_nochn <- est_t2[est_t2$iso3 != "CHN", ]
m2_2 <- feols(formula_int, data = est_t2_nochn, cluster = ~iso3)

# (3) Excluding high-income OECD
est_t2_nooecd <- est_t2[!est_t2$iso3 %in% high_income_oecd, ]
m2_3 <- feols(formula_int, data = est_t2_nooecd, cluster = ~iso3)

# (4) Excluding extreme growth
est_t2_noext <- est_t2[abs(est_t2$growth_annual) <= 0.30, ]
m2_4 <- feols(formula_int, data = est_t2_noext, cluster = ~iso3)

coef_map_t2 <- c(
  log_total_rmax                                      = "log(Total Rmax)",
  "log_total_rmax:wdi_industry_value_added_gdp"       = "log(Total Rmax) \u00d7 Industry VA/GDP",
  "log_total_rmax:wdi_services_value_added_gdp"       = "log(Total Rmax) \u00d7 Services VA/GDP",
  pwt_human_capital_index_lag1                        = "Human Capital Index (lagged)",
  pwt_investment_share_lag1                            = "Investment Share (lagged)",
  pwt_tfp_lag1                                         = "TFP (lagged)",
  pwt_export_share_lag1                                = "Export Share (lagged)",
  pwt_import_share_lag1                                = "Import Share (lagged)"
)

notes_t2 <- c(
  "All models include country and year fixed effects. Standard errors clustered at country level in parentheses.",
  "Dependent variable: annual log GDP per capita growth \u00d7 100 (percentage points).",
  "Interaction terms test whether the growth effect of compute capacity varies by economic structure.",
  "Industry value-added share proxies automation exposure; services share proxies new-task absorption capacity.",
  "Column (2): excluding China. Column (3): excluding 35 high-income OECD countries. Column (4): excluding |growth| > 0.30.",
  sprintf("Estimation sample: %d obs, %d countries, years %d\u2013%d, mean DV = %.2f%%.",
          nrow(est_t2), length(unique(est_t2$iso3)), min(est_t2$year), max(est_t2$year),
          mean(est_t2$growth_pct)),
  "Growth from PWT 11.0. Industry/Services value-added shares from WDI."
)

models_t2 <- list("(1)" = m2_1, "(2)" = m2_2, "(3)" = m2_3, "(4)" = m2_4)

tab2 <- modelsummary(models_t2,
  stars       = TRUE,
  coef_map    = coef_map_t2,
  gof_map     = gof_map,
  notes       = notes_t2,
  title       = "",
  output      = "tinytable"
)

html2 <- tinytable::save_tt(tab2, "html")
writeLines(html2, "reports/table2_channel.html")
cat("\nDone. reports/table2_channel.html written.\n")
