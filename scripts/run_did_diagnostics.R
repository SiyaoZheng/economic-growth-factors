library(arrow)
library(fixest)
library(dplyr)
library(ggplot2)
library(gridExtra)

set.seed(42)

# Load
df <- read_parquet("data/interim/did_ready.parquet")
controls_base <- c("pwt_human_capital_index_lag1", "pwt_investment_share_lag1",
                    "pwt_tfp_lag1", "pwt_export_share_lag1", "pwt_import_share_lag1")

# ---- 1. Raw Trends ----
compute_full <- read_parquet("data/interim/growth_with_compute.parquet")
df_trends <- compute_full %>%
  filter(year >= 2010, year <= 2023) %>%
  mutate(has_compute = as.integer(log_total_rmax > 0)) %>%
  group_by(iso3) %>%
  mutate(ever = max(has_compute, na.rm = TRUE)) %>%
  ungroup() %>%
  group_by(year, ever) %>%
  summarise(mean_growth = mean(growth_annual, na.rm = TRUE) * 100,
            sd_growth = sd(growth_annual, na.rm = TRUE) * 100,
            n = n(),
            se_growth = sd_growth / sqrt(n),
            .groups = "drop") %>%
  mutate(group = if_else(ever == 1, "Ever in TOP500 (N=44)", "Never in TOP500 (N=141)"))

p_trends <- ggplot(df_trends, aes(x = year, y = mean_growth, color = group, fill = group)) +
  geom_line(linewidth = 1.3) +
  geom_ribbon(aes(ymin = mean_growth - 1.96 * se_growth, ymax = mean_growth + 1.96 * se_growth), alpha = 0.15) +
  geom_point(size = 2.5) +
  geom_vline(xintercept = 2015, linetype = "dashed", color = "darkred", linewidth = 0.8) +
  annotate("text", x = 2015.3, y = -Inf, label = "Sample start", vjust = -1, hjust = 0, size = 3.5, color = "darkred") +
  scale_color_manual(values = c("Ever in TOP500 (N=44)" = "#2196F3", "Never in TOP500 (N=141)" = "#FF9800")) +
  scale_fill_manual(values = c("Ever in TOP500 (N=44)" = "#2196F3", "Never in TOP500 (N=141)" = "#FF9800")) +
  labs(x = "Year", y = "Mean Annual GDP Growth (% pts)",
       title = "GDP Growth Trends: TOP500 vs Non-TOP500 Countries",
       subtitle = "Pre-2015 shown for context. Shaded = ±1.96 × SE.",
       caption = "Sources: PWT 11.0 (growth), TOP500 (compute).") +
  theme_minimal(base_size = 13) +
  theme(legend.position = "bottom")
ggsave("reports/did_diagnostics/raw_trends.pdf", p_trends, width = 10, height = 6)

# ---- 2. Event Study (binary, diagnostic) ----
est_es <- df %>%
  mutate(rel_time = if_else(first_compute > 0, year - first_compute, -1000L))
es_mod <- feols(growth_pct ~ i(rel_time, ref = -1) | unit_id + year, data = est_es, cluster = ~iso3)
es_coef <- coef(es_mod); es_se <- se(es_mod)
es_periods <- as.integer(gsub("rel_time::", "", names(es_coef)))
es_df <- data.frame(rel_time = es_periods, estimate = as.numeric(es_coef), se = as.numeric(es_se)) %>%
  mutate(ci_lower = estimate - 1.96 * se, ci_upper = estimate + 1.96 * se) %>%
  filter(between(rel_time, -5, 5))

p_es <- ggplot(es_df, aes(x = rel_time, y = estimate)) +
  geom_rect(aes(xmin = -0.5, xmax = 0.5, ymin = -Inf, ymax = Inf), fill = "grey90", alpha = 0.3) +
  geom_linerange(aes(ymin = ci_lower, ymax = ci_upper), linewidth = 1.2, color = "#1565C0") +
  geom_point(size = 3, color = "#1565C0") +
  geom_hline(yintercept = 0, linetype = "dashed") + geom_vline(xintercept = -1, linetype = "dotted", linewidth = 0.5) +
  scale_x_continuous(breaks = seq(-5, 5, 1)) +
  labs(x = "Years Relative to First TOP500 Appearance", y = "Coefficient: Growth (pct. pts)",
       title = "Event Study: TOP500 Entry and GDP Growth",
       subtitle = sprintf("TWFE, country+year FE, clustered SE. %d countries.", n_distinct(est_es$iso3)),
       caption = "Reference: t=-1. Grey: treatment onset. 35/44 treated already in at t=0.") +
  theme_minimal(base_size = 13)
ggsave("reports/did_diagnostics/event_study_twfe.pdf", p_es, width = 10, height = 6)

# ---- 3. Pre-trend Diagnostic ----
pre_periods <- es_df %>% filter(rel_time < -1)
post_periods <- es_df %>% filter(rel_time >= 0)
max_pre <- max(abs(pre_periods$estimate), na.rm = TRUE)
post_avg <- mean(post_periods$estimate[post_periods$rel_time %in% 0:3], na.rm = TRUE)
ratio_val <- max_pre / (abs(post_avg) + 1e-10)

p_pretrend <- ggplot(es_df %>% filter(rel_time <= 0), aes(x = rel_time, y = estimate)) +
  geom_hline(yintercept = 0, linetype = "dashed") +
  geom_linerange(aes(ymin = ci_lower, ymax = ci_upper), linewidth = 1.5, color = "#1565C0") +
  geom_point(size = 3.5, color = "#1565C0") +
  geom_vline(xintercept = -1, linetype = "dotted", linewidth = 0.5) +
  scale_x_continuous(breaks = unique(es_df$rel_time[es_df$rel_time <= 0])) +
  labs(x = "Years Relative to TOP500 Entry", y = "Coefficient: Growth (pct. pts)",
       title = "Pre-Trend Diagnostic",
       subtitle = sprintf("Max |pre-trend| = %.4f. Avg post (t=0:3) = %.4f. Ratio = %.2f.", max_pre, post_avg, ratio_val),
       caption = "Reference: t=-1.") +
  theme_minimal(base_size = 13)
ggsave("reports/did_diagnostics/pretrend_diagnostic.pdf", p_pretrend, width = 9, height = 6)

# ---- 4. Treatment Heatmap ----
iso_order <- df %>% distinct(iso3, first_compute) %>% arrange(first_compute, iso3) %>% pull(iso3)
df_h <- df %>% mutate(iso3 = factor(iso3, levels = iso_order))
p_heat <- ggplot(df_h, aes(x = year, y = iso3, fill = factor(treated_binary))) +
  geom_tile(color = "white", linewidth = 0.08) +
  scale_fill_manual(values = c("0" = "#F5F5F5", "1" = "#1565C0"), labels = c("0"="No TOP500","1"="In TOP500"), name="") +
  scale_x_continuous(breaks = 2015:2023, expand = c(0,0)) +
  labs(x="Year", y="Country (sorted by first TOP500 year)", title="Treatment Status: Country-Year Map of TOP500 Presence",
       subtitle=paste0("44 ever-treated + 141 never = 185.")) +
  theme_minimal(base_size=10) + theme(axis.text.y=element_text(size=3.5,hjust=1), legend.position="bottom", panel.grid=element_blank())
ggsave("reports/did_diagnostics/treatment_heatmap.pdf", p_heat, width=12, height=10)

# ---- 5. Compute Distribution ----
p_hist <- ggplot(df %>% filter(log_total_rmax > 0), aes(x = log_total_rmax)) +
  geom_histogram(bins=40, fill="#1565C0", alpha=0.75, color="white") +
  geom_vline(aes(xintercept=mean(log_total_rmax)), linetype="dashed", color="darkred", linewidth=1) +
  labs(x="log(Total Rmax, GFlops)", y="Country-Year Count", title="Distribution: log Compute Capacity",
       subtitle=paste0(sum(df$log_total_rmax > 0)," non-zero obs, ",n_distinct(df$iso3[df$log_total_rmax > 0])," countries")) +
  theme_minimal(base_size=13)

top12 <- df %>% filter(log_total_rmax > 0) %>% group_by(iso3) %>% summarise(max_rmax = max(log_total_rmax), .groups="drop") %>%
  slice_max(max_rmax, n=12) %>% pull(iso3)
p_top <- ggplot(df %>% filter(iso3 %in% top12), aes(x=year, y=log_total_rmax, color=iso3, group=iso3)) +
  geom_line(linewidth=1.1) + geom_point(size=2) + scale_color_viridis_d(option="turbo") +
  labs(x="Year", y="log(Total Rmax, GFlops)", title="Compute Trajectories: Top 12 Countries", color="Country") +
  theme_minimal(base_size=12) + theme(legend.position="right")

p_compute <- grid.arrange(p_hist, p_top, ncol=2)
ggsave("reports/did_diagnostics/compute_distribution.pdf", p_compute, width=14, height=6)

# ---- 6. Placebo: Binary Randomization ----
set.seed(42); n_rep <- 2000
true_mod <- feols(growth_pct ~ treated_binary | unit_id + year, data=df, cluster=~iso3)
true_coef <- coef(true_mod)["treated_binary"]
unit_fc <- df %>% distinct(iso3, first_compute)
placebo_coefs <- replicate(n_rep, {
  unit_perm <- unit_fc %>% mutate(fc = sample(first_compute, n(), replace=FALSE))
  pd <- df %>% select(-treated_binary) %>% left_join(unit_perm %>% select(iso3, fc), by="iso3") %>%
    mutate(treat_bin = as.integer(year >= fc & fc > 0))
  coef(feols(growth_pct ~ treat_bin | unit_id + year, data=pd, cluster=~iso3))["treat_bin"]
})
placebo_pval <- mean(abs(placebo_coefs) >= abs(true_coef))

p_pl <- ggplot(data.frame(coef=placebo_coefs), aes(x=coef)) +
  geom_histogram(bins=50, fill="#1565C0", alpha=0.75, color="white") +
  geom_vline(xintercept=true_coef, color="#D32F2F", linewidth=1.5) + geom_vline(xintercept=0, linetype="dashed") +
  annotate("text", x=true_coef+0.02, y=Inf, label=paste0("True = ",round(true_coef,4)), vjust=2, color="#D32F2F", size=4.5) +
  labs(x="Placebo Coefficient", y="Count", title="Randomization Inference: Permuted Treatment Timing",
       subtitle=paste0("p = ",round(placebo_pval,4)," (",n_rep," perms)")) + theme_minimal(base_size=13)
ggsave("reports/did_diagnostics/placebo_randomization.pdf", p_pl, width=8, height=6)

# ---- 7. Placebo: Continuous ----
set.seed(43); n_rep_c <- 2000
formula_cont <- as.formula(paste("growth_pct ~ log_total_rmax +", paste(controls_base, collapse=" + "), "| unit_id + year"))
est_cc <- df[complete.cases(df[, c("growth_pct","log_total_rmax",controls_base)]), ]
true_cont <- feols(formula_cont, data=est_cc, cluster=~iso3)
tcc <- coef(true_cont)["log_total_rmax"]
cont_pb <- replicate(n_rep_c, {
  pd <- est_cc %>% group_by(year) %>% mutate(rp = sample(log_total_rmax, n(), replace=FALSE)) %>% ungroup()
  coef(feols(as.formula(paste("growth_pct ~ rp +", paste(controls_base, collapse=" + "), "| unit_id + year")),
             data=pd, cluster=~iso3))["rp"]
})
cpval <- mean(abs(cont_pb) >= abs(tcc))

p_cp <- ggplot(data.frame(coef=cont_pb), aes(x=coef)) +
  geom_histogram(bins=50, fill="#1565C0", alpha=0.75, color="white") +
  geom_vline(xintercept=tcc, color="#D32F2F", linewidth=1.5) + geom_vline(xintercept=0, linetype="dashed") +
  annotate("text", x=tcc+0.008, y=Inf, label=paste0("True = ",round(tcc,4)), vjust=2, color="#D32F2F", size=4.5) +
  labs(x="Placebo Coefficient", y="Count", title="Placebo: Permuted log(Compute) within Year",
       subtitle=paste0("p = ",round(cpval,4)," (",n_rep_c," perms)")) + theme_minimal(base_size=13)
ggsave("reports/did_diagnostics/placebo_continuous.pdf", p_cp, width=8, height=6)

# ---- 8. Coefficient Stability ----
m_raw  <- feols(growth_pct ~ log_total_rmax | unit_id + year, data=est_cc, cluster=~iso3)
m_hc   <- feols(growth_pct ~ log_total_rmax + pwt_human_capital_index_lag1 | unit_id + year, data=est_cc, cluster=~iso3)
m_inv  <- feols(growth_pct ~ log_total_rmax + pwt_human_capital_index_lag1 + pwt_investment_share_lag1 | unit_id + year, data=est_cc, cluster=~iso3)
m_full <- true_cont

stab <- data.frame(
  model = rev(c("Raw FE", "+ Human Capital", "+ Investment", "+ TFP + Trade")),
  coef  = c(coef(m_raw)["log_total_rmax"], coef(m_hc)["log_total_rmax"],
            coef(m_inv)["log_total_rmax"], coef(m_full)["log_total_rmax"]),
  se    = c(se(m_raw)["log_total_rmax"], se(m_hc)["log_total_rmax"],
            se(m_inv)["log_total_rmax"], se(m_full)["log_total_rmax"])
) %>% mutate(ci_low=coef-1.96*se, ci_high=coef+1.96*se, model=factor(model, levels=rev(c("Raw FE","+ Human Capital","+ Investment","+ TFP + Trade"))))

p_stab <- ggplot(stab, aes(x=coef, y=model)) +
  geom_point(size=3, color="#1565C0") + geom_linerange(aes(xmin=ci_low, xmax=ci_high), linewidth=1.5, color="#1565C0") +
  geom_vline(xintercept=0, linetype="dashed") +
  labs(x="Coefficient: log(Total Rmax) → Growth (pct. pts)", y="", title="Coefficient Stability: Adding Controls") +
  theme_minimal(base_size=13)
ggsave("reports/did_diagnostics/coef_stability.pdf", p_stab, width=9, height=4.5)

# ---- 9. Full Table ----
etable(m_raw, m_hc, m_inv, m_full, cluster=~iso3,
       headers=c("Raw FE","+ HC","+ Investment","+ TFP+Trade"),
       file="reports/did_diagnostics/regression_etable.txt")

# ---- 10. Summary ----
cat("\n====== DIAGNOSTICS SUMMARY ======\n")
cat(sprintf("Panel: %d countries x %d years = %d obs (balanced)\n", n_distinct(df$iso3), n_distinct(df$year), nrow(df)))
cat(sprintf("Continuous log_total_rmax: coeff=%.4f (se=%.4f, p=%.4f)\n", tcc, se(true_cont)["log_total_rmax"], pvalue(true_cont)["log_total_rmax"]))
cat(sprintf("Binary treated: coeff=%.4f (p=%.4f)\n", true_coef, pvalue(true_mod)["treated_binary"]))
cat(sprintf("Binary placebo p=%.4f, Continuous placebo p=%.4f\n", placebo_pval, cpval))
cat(sprintf("Pre-trend: max|pre|=%.4f, avg post=%.4f, ratio=%.2f\n", max_pre, post_avg, ratio_val))
cat(sprintf("N=%d, R2=%.3f, Adj.Within R2=%.3f\n", nobs(true_cont), r2(true_cont), r2(true_cont,"war2")))
cat("\nDone.\n")
