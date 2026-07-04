library(arrow); library(fixest); library(dplyr); library(ggplot2); library(gridExtra)
set.seed(42)

df <- read_parquet("data/interim/did_ready.parquet")
controls_base <- c("pwt_human_capital_index_lag1","pwt_investment_share_lag1",
                    "pwt_tfp_lag1","pwt_export_share_lag1","pwt_import_share_lag1")

# ---- Placebo: binary ----
n_rep <- 2000
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
       subtitle=paste0("p = ",round(placebo_pval,4)," (",n_rep," permutations)")) + theme_minimal(base_size=13)
ggsave("reports/did_diagnostics/placebo_randomization.pdf", p_pl, width=8, height=6)
cat(sprintf("Binary placebo: true=%.4f, p=%.4f\n", true_coef, placebo_pval))

# ---- Placebo: continuous ----
formula_cont <- as.formula(paste("growth_pct ~ log_total_rmax +", paste(controls_base, collapse=" + "), "| unit_id + year"))
est_cc <- df[complete.cases(df[, c("growth_pct","log_total_rmax",controls_base)]), ]
tmod <- feols(formula_cont, data=est_cc, cluster=~iso3)
tcc <- coef(tmod)["log_total_rmax"]

n_rep_c <- 2000
cont_pb <- replicate(n_rep_c, {
  pd <- est_cc; pd$rp <- ave(pd$log_total_rmax, pd$year, FUN=function(x) sample(x, length(x), replace=FALSE))
  coef(feols(as.formula(paste("growth_pct ~ rp +", paste(controls_base, collapse=" + "), "| unit_id + year")),
             data=pd, cluster=~iso3))["rp"]
})
cpval <- mean(abs(cont_pb) >= abs(tcc))

p_cp <- ggplot(data.frame(coef=cont_pb), aes(x=coef)) +
  geom_histogram(bins=50, fill="#1565C0", alpha=0.75, color="white") +
  geom_vline(xintercept=tcc, color="#D32F2F", linewidth=1.5) + geom_vline(xintercept=0, linetype="dashed") +
  annotate("text", x=tcc+0.008, y=Inf, label=paste0("True = ",round(tcc,4)), vjust=2, color="#D32F2F", size=4.5) +
  labs(x="Placebo Coefficient", y="Count", title="Placebo: Permuted log(Compute) within Year",
       subtitle=paste0("p = ",round(cpval,4)," (",n_rep_c," permutations)")) + theme_minimal(base_size=13)
ggsave("reports/did_diagnostics/placebo_continuous.pdf", p_cp, width=8, height=6)
cat(sprintf("Continuous placebo: true=%.4f, p=%.4f\n", tcc, cpval))

# ---- Coef Stability ----
m_raw  <- feols(growth_pct ~ log_total_rmax | unit_id + year, data=est_cc, cluster=~iso3)
m_hc   <- feols(growth_pct ~ log_total_rmax + pwt_human_capital_index_lag1 | unit_id + year, data=est_cc, cluster=~iso3)
m_inv  <- feols(growth_pct ~ log_total_rmax + pwt_human_capital_index_lag1 + pwt_investment_share_lag1 | unit_id + year, data=est_cc, cluster=~iso3)

stab <- data.frame(
  model = c("Raw FE","+ Human Capital","+ Investment","+ TFP+Trade"),
  coef = c(coef(m_raw)["log_total_rmax"], coef(m_hc)["log_total_rmax"], coef(m_inv)["log_total_rmax"], coef(tmod)["log_total_rmax"]),
  se = c(se(m_raw)["log_total_rmax"], se(m_hc)["log_total_rmax"], se(m_inv)["log_total_rmax"], se(tmod)["log_total_rmax"])
) %>% mutate(ci_low=coef-1.96*se, ci_high=coef+1.96*se, model=factor(model, levels=rev(c("Raw FE","+ Human Capital","+ Investment","+ TFP+Trade"))))

p_stab <- ggplot(stab, aes(x=coef, y=model)) +
  geom_point(size=3, color="#1565C0") + geom_linerange(aes(xmin=ci_low, xmax=ci_high), linewidth=1.5, color="#1565C0") +
  geom_vline(xintercept=0, linetype="dashed") +
  labs(x="Coefficient: log(Total Rmax) → Growth (pct. pts)", y="", title="Coefficient Stability: Adding Controls") + theme_minimal(base_size=13)
ggsave("reports/did_diagnostics/coef_stability.pdf", p_stab, width=9, height=4.5)

# ---- Regression etable ----
etable(m_raw, m_hc, m_inv, tmod, cluster=~iso3, headers=c("Raw FE","+ HC","+ Investment","+ TFP+Trade"),
       file="reports/did_diagnostics/regression_etable.txt")
cat("Done.\n")
