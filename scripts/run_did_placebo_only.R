library(arrow)
library(fixest)
library(dplyr)
library(ggplot2)
library(gridExtra)
library(showtext)

font_add("heiti", "/System/Library/Fonts/STHeiti Light.ttc")
showtext_auto()

set.seed(42)

COLOR_ESTIMATE  <- "#377EB8"
COLOR_REFERENCE <- "#E41A1C"

theme_aer <- theme_minimal(base_size = 11) +
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major = element_line(linewidth = 0.2, color = "grey88"),
    axis.title = element_text(size = 11),
    axis.text  = element_text(size = 10),
    plot.caption = element_text(size = 8.5, hjust = 0, color = "grey40",
                                margin = margin(t = 10)),
    legend.position = "bottom",
    legend.title = element_blank(),
    plot.title = element_blank(),
    plot.subtitle = element_blank(),
    plot.margin = margin(12, 12, 8, 12)
  )

theme_set(theme_aer)

df <- read_parquet("data/interim/did_ready.parquet")
controls_base <- c("pwt_human_capital_index_lag1", "pwt_investment_share_lag1",
                    "pwt_tfp_lag1", "pwt_export_share_lag1", "pwt_import_share_lag1")

# ---- 安慰剂检验：二元随机化 ----
n_rep <- 2000
true_mod <- feols(growth_pct ~ treated_binary | unit_id + year, data = df, cluster = ~iso3)
true_coef <- coef(true_mod)["treated_binary"]
unit_fc <- df %>% distinct(iso3, first_compute)
placebo_coefs <- replicate(n_rep, {
  unit_perm <- unit_fc %>% mutate(fc = sample(first_compute, n(), replace = FALSE))
  pd <- df %>% select(-treated_binary) %>%
    left_join(unit_perm %>% select(iso3, fc), by = "iso3") %>%
    mutate(treat_bin = as.integer(year >= fc & fc > 0))
  coef(feols(growth_pct ~ treat_bin | unit_id + year, data = pd, cluster = ~iso3))["treat_bin"]
})
placebo_pval <- mean(abs(placebo_coefs) >= abs(true_coef))

p_pl <- ggplot(data.frame(coef = placebo_coefs), aes(x = coef)) +
  geom_histogram(bins = 50, fill = COLOR_ESTIMATE, alpha = 0.82,
                 color = "white", linewidth = 0.2) +
  geom_vline(xintercept = true_coef, color = COLOR_REFERENCE, linewidth = 1.2) +
  geom_vline(xintercept = 0, linetype = "dashed", linewidth = 0.4) +
  annotate("text", x = true_coef + 0.03, y = Inf,
           label = sprintf("真实值 = %.3f", true_coef),
           vjust = 2, color = COLOR_REFERENCE, size = 4.2, fontface = "bold") +
  annotate("text", x = Inf, y = Inf,
           label = sprintf("p = %.3f\n(%d 次置换)", placebo_pval, n_rep),
           hjust = 1.1, vjust = 1.3, size = 3.8, color = "grey40") +
  labs(x = "安慰剂系数（二元处理）", y = "频数",
       caption = "注：随机打乱各国首次进入 TOP500 的年份后重估处理效应。")

ggsave("reports/did_diagnostics/placebo_randomization.pdf", p_pl,
       width = 7, height = 5, device = cairo_pdf)
ggsave("outputs/figures/placebo_randomization.png", p_pl,
       width = 7, height = 5, dpi = 300)

cat(sprintf("二元安慰剂：真实值=%.4f，p=%.4f\n", true_coef, placebo_pval))

# ---- 安慰剂检验：连续处理 ----
formula_cont <- as.formula(paste("growth_pct ~ log_total_rmax +",
                                  paste(controls_base, collapse = " + "),
                                  "| unit_id + year"))
est_cc <- df[complete.cases(df[, c("growth_pct", "log_total_rmax", controls_base)]), ]
true_cont <- feols(formula_cont, data = est_cc, cluster = ~iso3)
tcc <- coef(true_cont)["log_total_rmax"]
set.seed(43); n_rep_c <- 2000
cont_pb <- replicate(n_rep_c, {
  pd <- est_cc %>%
    group_by(year) %>%
    mutate(rp = sample(log_total_rmax, n(), replace = FALSE)) %>%
    ungroup()
  coef(feols(as.formula(paste("growth_pct ~ rp +",
                               paste(controls_base, collapse = " + "),
                               "| unit_id + year")),
             data = pd, cluster = ~iso3))["rp"]
})
cpval <- mean(abs(cont_pb) >= abs(tcc))

p_cp <- ggplot(data.frame(coef = cont_pb), aes(x = coef)) +
  geom_histogram(bins = 50, fill = COLOR_ESTIMATE, alpha = 0.82,
                 color = "white", linewidth = 0.2) +
  geom_vline(xintercept = tcc, color = COLOR_REFERENCE, linewidth = 1.2) +
  geom_vline(xintercept = 0, linetype = "dashed", linewidth = 0.4) +
  annotate("text", x = tcc + 0.01, y = Inf,
           label = sprintf("真实值 = %.4f", tcc),
           vjust = 2, color = COLOR_REFERENCE, size = 4.2, fontface = "bold") +
  annotate("text", x = Inf, y = Inf,
           label = sprintf("p = %.3f\n(%d 次置换)", cpval, n_rep_c),
           hjust = 1.1, vjust = 1.3, size = 3.8, color = "grey40") +
  labs(x = "安慰剂系数（连续处理：log Rmax）", y = "频数",
       caption = "注：在年份内随机打乱 log(Total Rmax) 后重估连续处理效应。")

ggsave("reports/did_diagnostics/placebo_continuous.pdf", p_cp,
       width = 7, height = 5, device = cairo_pdf)
ggsave("outputs/figures/placebo_continuous.png", p_cp,
       width = 7, height = 5, dpi = 300)

cat(sprintf("连续安慰剂：真实值=%.4f，p=%.4f\n", tcc, cpval))

# ---- 系数稳定性 ----
m_raw  <- feols(growth_pct ~ log_total_rmax | unit_id + year, data = est_cc, cluster = ~iso3)
m_hc   <- feols(growth_pct ~ log_total_rmax + pwt_human_capital_index_lag1 | unit_id + year,
                data = est_cc, cluster = ~iso3)
m_inv  <- feols(growth_pct ~ log_total_rmax + pwt_human_capital_index_lag1 + pwt_investment_share_lag1 | unit_id + year,
                data = est_cc, cluster = ~iso3)

stab <- data.frame(
  model = rev(c("仅固定效应", "+\u00a0人力资本", "+\u00a0投资率", "+\u00a0TFP + 贸易")),
  coef  = c(coef(m_raw)["log_total_rmax"], coef(m_hc)["log_total_rmax"],
            coef(m_inv)["log_total_rmax"], coef(true_cont)["log_total_rmax"]),
  se    = c(se(m_raw)["log_total_rmax"], se(m_hc)["log_total_rmax"],
            se(m_inv)["log_total_rmax"], se(true_cont)["log_total_rmax"])
) %>%
  mutate(
    ci_low  = coef - 1.96 * se,
    ci_high = coef + 1.96 * se,
    model = factor(model, levels = rev(c("仅固定效应", "+\u00a0人力资本", "+\u00a0投资率", "+\u00a0TFP + 贸易")))
  )

p_stab <- ggplot(stab, aes(x = coef, y = model)) +
  geom_point(size = 3.2, color = COLOR_ESTIMATE) +
  geom_linerange(aes(xmin = ci_low, xmax = ci_high),
                 linewidth = 1.6, color = COLOR_ESTIMATE) +
  geom_vline(xintercept = 0, linetype = "dashed", linewidth = 0.4) +
  labs(x = expression("系数：log(Total Rmax) " %->% " GDP 增长率（百分点）"), y = "",
       caption = sprintf("注：逐步加入控制变量。全部包含国家与年份固定效应，标准误在国家层面聚类。N = %d。",
                         nobs(true_cont)))

ggsave("reports/did_diagnostics/coef_stability.pdf", p_stab,
       width = 7.5, height = 3.5, device = cairo_pdf)
ggsave("outputs/figures/coef_stability.png", p_stab,
       width = 7.5, height = 3.5, dpi = 300)

etable(m_raw, m_hc, m_inv, true_cont, cluster = ~iso3,
       headers = c("仅固定效应", "+ 人力资本", "+ 投资率", "+ TFP+贸易"),
       file = "reports/did_diagnostics/regression_etable.txt")

showtext_auto(FALSE)
cat("\n完成。\n")
