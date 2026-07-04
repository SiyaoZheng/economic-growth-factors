library(arrow)
library(fixest)
library(modelsummary)
library(tinytable)

df <- arrow::read_parquet("data/processed/growth_panel_1960plus.parquet")
df$growth_pct <- df$growth_annual * 100
df <- df[!is.na(df$growth_pct), ]

high_income_oecd <- c(
  "AUS","AUT","BEL","CAN","CHE","CYP","CZE","DEU","DNK","ESP","EST","FIN","FRA",
  "GBR","GRC","HUN","IRL","ISL","ISR","ITA","JPN","KOR","LTU","LUX","LVA",
  "MLT","NLD","NOR","NZL","POL","PRT","SVK","SVN","SWE","USA"
)

# Estimation sample (complete cases for all RHS vars)
est <- df[complete.cases(df[, c("growth_pct","pwt_human_capital_index_lag1",
                                "pwt_investment_share_lag1","pwt_tfp_lag1",
                                "pwt_export_share_lag1","pwt_import_share_lag1")]), ]

cat(sprintf("Estimation sample: %d obs, %d countries, %d-%d, mean DV = %.2f\n",
            nrow(est), length(unique(est$iso3)),
            min(est$year), max(est$year), mean(est$growth_pct, na.rm = TRUE)))

# --- Models (fit on the same complete-case sample for consistent comparisons) ---
m1 <- feols(growth_pct ~ pwt_human_capital_index_lag1 + pwt_investment_share_lag1 +
              pwt_tfp_lag1 + pwt_export_share_lag1 + pwt_import_share_lag1 |
              iso3 + year, data = est, cluster = ~iso3)

est2 <- est[est$iso3 != "CHN", ]
m2 <- feols(growth_pct ~ pwt_human_capital_index_lag1 + pwt_investment_share_lag1 +
              pwt_tfp_lag1 + pwt_export_share_lag1 + pwt_import_share_lag1 |
              iso3 + year, data = est2, cluster = ~iso3)

est3 <- est[!est$iso3 %in% high_income_oecd, ]
m3 <- feols(growth_pct ~ pwt_human_capital_index_lag1 + pwt_investment_share_lag1 +
              pwt_tfp_lag1 + pwt_export_share_lag1 + pwt_import_share_lag1 |
              iso3 + year, data = est3, cluster = ~iso3)

est4 <- est[abs(est$growth_annual) <= 0.30, ]
m4 <- feols(growth_pct ~ pwt_human_capital_index_lag1 + pwt_investment_share_lag1 +
              pwt_tfp_lag1 + pwt_export_share_lag1 + pwt_import_share_lag1 |
              iso3 + year, data = est4, cluster = ~iso3)

vars <- c(
  pwt_human_capital_index_lag1 = "Human Capital Index (lagged)",
  pwt_investment_share_lag1     = "Investment Share (lagged)",
  pwt_tfp_lag1                  = "TFP (lagged)",
  pwt_export_share_lag1         = "Export Share (lagged)",
  pwt_import_share_lag1         = "Import Share (lagged)"
)

gm <- data.frame(
  raw   = c("nobs", "r2", "r2.within"),
  clean = c("Observations", "R²", "Within R²"),
  fmt   = c(0, 3, 3)
)

notes <- c(
  "All models include country and year fixed effects.",
  "Standard errors clustered at country level in parentheses.",
  "Dependent variable: annual log GDP per capita growth (×100 = percentage points).",
  "Column (2): excluding China (63 obs dropped). Column (3): excluding 35 high-income OECD countries (1,973 obs dropped).",
  "Column (4): excluding |growth| > 30% observations (18 obs dropped).",
  sprintf("Baseline estimation sample: %d obs, %d countries, years %d–%d, mean DV = %.2f.",
          nrow(est), length(unique(est$iso3)), min(est$year), max(est$year), mean(est$growth_pct)),
  "Growth computed from PWT 11.0 real GDP per capita (rgdpna / population), log-differenced annually."
)

models <- list("(1)" = m1, "(2)" = m2, "(3)" = m3, "(4)" = m4)

tab <- modelsummary(models,
  stars     = TRUE,
  coef_map  = vars,
  gof_map   = gm,
  notes     = notes,
  title     = "Table 1. Growth Determinants: Country-Year Panel (PWT 1961–2023)",
  output    = "tinytable"
)

html <- tinytable::save_tt(tab, "html")
writeLines(html, "reports/growth_table.html")
cat("\nDone. reports/growth_table.html written.\n")
