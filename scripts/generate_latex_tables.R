library(arrow)
library(fixest)
library(modelsummary)
library(dplyr)
options("modelsummary_format_numeric_latex" = "plain")

# ---- Data ----
compute_raw <- arrow::read_parquet("data/interim/growth_with_compute.parquet")
growth_raw <- arrow::read_parquet("data/processed/growth_panel_1960plus.parquet")
growth_raw <- growth_raw %>%
  filter(year >= 2015) %>%
  select(iso3, year, wdi_industry_value_added_gdp, wdi_services_value_added_gdp)

df <- compute_raw %>%
  filter(year >= 2015) %>%
  left_join(growth_raw, by = c("iso3", "year")) %>%
  mutate(growth_pct = growth_annual * 100)

high_income_oecd <- c("AUS","AUT","BEL","CAN","CHE","CYP","CZE","DEU","DNK","ESP","EST","FIN","FRA","GBR","GRC","HUN","IRL","ISL","ISR","ITA","JPN","KOR","LTU","LUX","LVA","MLT","NLD","NOR","NZL","POL","PRT","SVK","SVN","SWE","USA")

controls_base <- c("pwt_human_capital_index_lag1", "pwt_investment_share_lag1", "pwt_tfp_lag1", "pwt_export_share_lag1", "pwt_import_share_lag1")
t1_vars <- c("growth_pct", "log_total_rmax", controls_base)
est_t1 <- df[complete.cases(df[, t1_vars]), ]

formula_base <- as.formula(paste("growth_pct ~ log_total_rmax +", paste(controls_base, collapse = " + "), "| iso3 + year"))

m1_1 <- feols(formula_base, data = est_t1, cluster = ~iso3)
m1_2 <- feols(formula_base, data = est_t1[est_t1$iso3 != "CHN", ], cluster = ~iso3)
m1_3 <- feols(formula_base, data = est_t1[!est_t1$iso3 %in% high_income_oecd, ], cluster = ~iso3)
m1_4 <- feols(formula_base, data = est_t1[abs(est_t1$growth_annual) <= 0.30, ], cluster = ~iso3)

models_t1 <- list("(1)" = m1_1, "(2)" = m1_2, "(3)" = m1_3, "(4)" = m1_4)

# ---- Manual LaTeX generation ----
# Extract coefs manually from fixest objects
extract_row <- function(model, coef_name) {
  co <- coef(model)
  se <- sqrt(diag(vcov(model)))
  if (coef_name %in% names(co)) {
    est <- sprintf("%.3f", co[coef_name])
    se_val <- sprintf("(%.3f)", se[coef_name])
    return(c(est, se_val))
  }
  return(c("", ""))
}

coef_names <- c("log_total_rmax", "pwt_human_capital_index_lag1", "pwt_investment_share_lag1",
                "pwt_tfp_lag1", "pwt_export_share_lag1", "pwt_import_share_lag1")

coef_display <- c("log(TOP500 Total Rmax)", "Human Capital Index (lagged)", "Investment Share (lagged)",
                  "TFP (lagged)", "Export Share (lagged)", "Import Share (lagged)")

# Add stars
add_stars <- function(pval) {
  if (is.na(pval)) return("")
  if (pval < 0.001) return("***")
  if (pval < 0.01) return("**")
  if (pval < 0.05) return("*")
  if (pval < 0.1) return("+")
  return("")
}

lines <- c()
lines <- c(lines, "\\begin{tabular}{@{}lcccc@{}}")
lines <- c(lines, "\\toprule")
lines <- c(lines, "& \\multicolumn{4}{c}{Dependent variable: GDP per capita growth $\\times$ 100} \\\\")
lines <- c(lines, "\\cmidrule(lr){2-5}")
lines <- c(lines, "& (1) & (2) & (3) & (4) \\\\")
lines <- c(lines, "\\midrule")

model_list <- list(m1_1, m1_2, m1_3, m1_4)

for (i in seq_along(coef_names)) {
  cn <- coef_names[i]
  cd <- coef_display[i]
  ests <- c()
  ses <- c()
  for (m in model_list) {
    co <- coef(m)
    se <- sqrt(diag(vcov(m)))
    pv <- tryCatch(pvalue(m)[cn], error = function(e) NA)
    if (cn %in% names(co)) {
      stars <- add_stars(pv)
      ests <- c(ests, paste0(sprintf("%.3f", co[cn]), stars))
      ses <- c(ses, sprintf("(%.3f)", se[cn]))
    } else {
      ests <- c(ests, "")
      ses <- c(ses, "")
    }
  }
  lines <- c(lines, paste(c(cd, ests), collapse = " & "), "\\\\")
  lines <- c(lines, paste(c("", ses), collapse = " & "), "\\\\")
}

# GOF
nobs <- sapply(model_list, function(m) nobs(m))
r2w  <- sapply(model_list, function(m) round(r2(m, type = "war2")[["war2"]], 3))

lines <- c(lines, "\\midrule")
lines <- c(lines, paste(c("Observations", nobs), collapse = " & "), "\\\\")
lines <- c(lines, paste(c("Adj. Within R\\textsuperscript{2}", r2w), collapse = " & "), "\\\\")
lines <- c(lines, "\\bottomrule")
lines <- c(lines, "\\end{tabular}")

writeLines(lines, "outputs/writing/table1_main_effect.tex")
cat("Table 1 written.\n")

# ---- Table 2 ----
t2_vars <- c(t1_vars, "wdi_industry_value_added_gdp", "wdi_services_value_added_gdp")
est_t2 <- df[complete.cases(df[, t2_vars]), ]

formula_int <- as.formula(paste(
  "growth_pct ~ log_total_rmax +",
  "log_total_rmax:wdi_industry_value_added_gdp +",
  "log_total_rmax:wdi_services_value_added_gdp +",
  paste(controls_base, collapse = " + "),
  "| iso3 + year"
))

m2_1 <- feols(formula_int, data = est_t2, cluster = ~iso3)
m2_2 <- feols(formula_int, data = est_t2[est_t2$iso3 != "CHN", ], cluster = ~iso3)
m2_3 <- feols(formula_int, data = est_t2[!est_t2$iso3 %in% high_income_oecd, ], cluster = ~iso3)
m2_4 <- feols(formula_int, data = est_t2[abs(est_t2$growth_annual) <= 0.30, ], cluster = ~iso3)

model_list2 <- list(m2_1, m2_2, m2_3, m2_4)

coef_names2 <- c("log_total_rmax", "log_total_rmax:wdi_industry_value_added_gdp",
                 "log_total_rmax:wdi_services_value_added_gdp",
                 "pwt_human_capital_index_lag1", "pwt_investment_share_lag1",
                 "pwt_tfp_lag1", "pwt_export_share_lag1", "pwt_import_share_lag1")

coef_display2 <- c("log(Total Rmax)", "log(Total Rmax) $\\times$ Industry VA/GDP",
                   "log(Total Rmax) $\\times$ Services VA/GDP",
                   "Human Capital Index (lagged)", "Investment Share (lagged)",
                   "TFP (lagged)", "Export Share (lagged)", "Import Share (lagged)")

lines2 <- c()
lines2 <- c(lines2, "\\begin{tabular}{@{}lcccc@{}}")
lines2 <- c(lines2, "\\toprule")
lines2 <- c(lines2, "& \\multicolumn{4}{c}{Channel Interactions: Compute $\\times$ Economic Structure} \\\\")
lines2 <- c(lines2, "\\cmidrule(lr){2-5}")
lines2 <- c(lines2, "& (1) & (2) & (3) & (4) \\\\")
lines2 <- c(lines2, "\\midrule")

for (i in seq_along(coef_names2)) {
  cn <- coef_names2[i]
  cd <- coef_display2[i]
  ests <- c()
  ses <- c()
  for (m in model_list2) {
    co <- coef(m)
    se <- sqrt(diag(vcov(m)))
    pv <- tryCatch(pvalue(m)[cn], error = function(e) NA)
    if (cn %in% names(co)) {
      stars <- add_stars(pv)
      ests <- c(ests, paste0(sprintf("%.3f", co[cn]), stars))
      ses <- c(ses, sprintf("(%.3f)", se[cn]))
    } else {
      ests <- c(ests, "")
      ses <- c(ses, "")
    }
  }
  lines2 <- c(lines2, paste(c(cd, ests), collapse = " & "), "\\\\")
  lines2 <- c(lines2, paste(c("", ses), collapse = " & "), "\\\\")
}

nobs2 <- sapply(model_list2, function(m) nobs(m))
r2w2  <- sapply(model_list2, function(m) round(r2(m, type = "war2")[["war2"]], 3))

lines2 <- c(lines2, "\\midrule")
lines2 <- c(lines2, paste(c("Observations", nobs2), collapse = " & "), "\\\\")
lines2 <- c(lines2, paste(c("Adj. Within R\\textsuperscript{2}", r2w2), collapse = " & "), "\\\\")
lines2 <- c(lines2, "\\bottomrule")
lines2 <- c(lines2, "\\end{tabular}")

writeLines(lines2, "outputs/writing/table2_channel.tex")
cat("Table 2 written.\n")
