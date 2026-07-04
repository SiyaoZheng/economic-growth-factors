library(arrow)
library(fixest)
library(dplyr)
library(ggplot2)
library(gridExtra)
library(showtext)

# ---- 中文字体支持 ----
font_add("heiti", "/System/Library/Fonts/STHeiti Light.ttc")
showtext_auto()

set.seed(42)

# ---- 颜色方案（ColorBrewer Dark2 + 自定义） ----
COLOR_TREATED   <- "#1B9E77"   # 进入TOP500 - 深绿
COLOR_NEVER     <- "#D95F02"   # 从未进入 - 橙色
COLOR_ESTIMATE  <- "#377EB8"   # 蓝色 - 系数估计
COLOR_REFERENCE <- "#E41A1C"   # 红色 - 参考线/真实值
COLOR_CI_FILL   <- "#377EB8"   # 置信区间填充色
SHADE_GREY      <- "grey85"

# ---- 全局 ggplot2 主题（AER 级简洁风格） ----
theme_aer <- theme_minimal(base_size = 11, base_family = "sans") +
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major = element_line(linewidth = 0.2, color = "grey88"),
    axis.title = element_text(size = 11),
    axis.text  = element_text(size = 10),
    plot.caption = element_text(size = 8.5, hjust = 0, color = "grey40",
                                margin = margin(t = 10)),
    legend.position = "bottom",
    legend.title = element_blank(),
    legend.text = element_text(size = 9),
    plot.title = element_blank(),
    plot.subtitle = element_blank(),
    plot.margin = margin(12, 12, 8, 12)
  )

theme_set(theme_aer)

# Load
df <- read_parquet("data/interim/did_ready.parquet")
controls_base <- c("pwt_human_capital_index_lag1", "pwt_investment_share_lag1",
                    "pwt_tfp_lag1", "pwt_export_share_lag1", "pwt_import_share_lag1")

# =====================================================================
# 图1: 原始趋势 —— GDP增长率：进入与未进入 TOP500 的国家
# =====================================================================
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
  mutate(group = if_else(ever == 1,
    "曾进入 TOP500（N=44）",
    "从未进入 TOP500（N=141）"))

# Direct labeling: get the last year's value for each group
labels_trends <- df_trends %>%
  filter(year == max(year)) %>%
  mutate(label_y = mean_growth)

p_trends <- ggplot(df_trends, aes(x = year, y = mean_growth, color = group, fill = group)) +
  geom_ribbon(aes(ymin = mean_growth - 1.96 * se_growth,
                  ymax = mean_growth + 1.96 * se_growth),
              alpha = 0.18, color = NA) +
  geom_line(linewidth = 1.0) +
  geom_point(size = 1.8) +
  geom_vline(xintercept = 2015, linetype = "dashed",
             color = COLOR_REFERENCE, linewidth = 0.6) +
  annotate("text", x = 2015.3, y = -Inf, label = "样本起点 2015",
           vjust = -1, hjust = 0, size = 3.2, color = COLOR_REFERENCE) +
  scale_color_manual(values = c("曾进入 TOP500（N=44）" = COLOR_TREATED,
                                 "从未进入 TOP500（N=141）" = COLOR_NEVER)) +
  scale_fill_manual(values = c("曾进入 TOP500（N=44）" = COLOR_TREATED,
                                 "从未进入 TOP500（N=141）" = COLOR_NEVER)) +
  scale_x_continuous(breaks = seq(2010, 2023, 2)) +
  labs(x = "年份", y = "年均 GDP 增长率（%）",
       caption = "注：实线为组均值，阴影区域为 ±1.96 × 标准误。2015 年前数据仅作背景参考。数据来源：PWT 11.0（增长率）、TOP500（计算能力）。") +
  # Direct labeling at line ends
  geom_text(data = labels_trends,
            aes(x = year + 0.15, y = label_y, label = group, color = group),
            hjust = 0, size = 3.5, fontface = "bold", show.legend = FALSE) +
  theme(legend.position = "none") +
  coord_cartesian(xlim = c(2010, 2025))

ggsave("reports/did_diagnostics/raw_trends.pdf", p_trends,
       width = 8, height = 4.8, device = cairo_pdf)
ggsave("outputs/figures/raw_trends.png", p_trends,
       width = 8, height = 4.8, dpi = 300)

# =====================================================================
# 图2: 事件研究法
# =====================================================================
est_es <- df %>%
  mutate(rel_time = if_else(first_compute > 0, year - first_compute, -1000L))
es_mod <- feols(growth_pct ~ i(rel_time, ref = -1) | unit_id + year,
                data = est_es, cluster = ~iso3)
es_coef <- coef(es_mod); es_se <- se(es_mod)
es_periods <- as.integer(gsub("rel_time::", "", names(es_coef)))
es_df <- data.frame(rel_time = es_periods,
                    estimate = as.numeric(es_coef),
                    se = as.numeric(es_se)) %>%
  mutate(ci_lower = estimate - 1.96 * se,
         ci_upper = estimate + 1.96 * se) %>%
  filter(between(rel_time, -5, 5))

p_es <- ggplot(es_df, aes(x = rel_time, y = estimate)) +
  geom_rect(aes(xmin = -0.5, xmax = 0.5, ymin = -Inf, ymax = Inf),
            fill = "grey90", alpha = 0.4) +
  geom_linerange(aes(ymin = ci_lower, ymax = ci_upper),
                 linewidth = 1.3, color = COLOR_ESTIMATE) +
  geom_point(size = 2.8, color = COLOR_ESTIMATE) +
  geom_hline(yintercept = 0, linetype = "dashed", linewidth = 0.4) +
  geom_vline(xintercept = -1, linetype = "dotted", linewidth = 0.4) +
  scale_x_continuous(breaks = seq(-5, 5, 1)) +
  labs(x = "距首次进入 TOP500 的年数", y = "系数：GDP 增长率（百分点）",
       caption = sprintf("注：双向固定效应（国家 + 年份），标准误在国家层面聚类。参考期：t = -1。灰色区域为处理发生时点。%d 个国家中 44 个为处理组。",
                         n_distinct(est_es$iso3)))

ggsave("reports/did_diagnostics/event_study_twfe.pdf", p_es,
       width = 8, height = 4.8, device = cairo_pdf)
ggsave("outputs/figures/event_study_twfe.png", p_es,
       width = 8, height = 4.8, dpi = 300)

# =====================================================================
# 图3: 平行趋势诊断（仅处理前期）
# =====================================================================
pre_periods <- es_df %>% filter(rel_time < -1)
post_periods <- es_df %>% filter(rel_time >= 0)
max_pre <- max(abs(pre_periods$estimate), na.rm = TRUE)
post_avg <- mean(post_periods$estimate[post_periods$rel_time %in% 0:3], na.rm = TRUE)
ratio_val <- max_pre / (abs(post_avg) + 1e-10)

p_pretrend <- ggplot(es_df %>% filter(rel_time <= 0), aes(x = rel_time, y = estimate)) +
  geom_hline(yintercept = 0, linetype = "dashed", linewidth = 0.4) +
  geom_linerange(aes(ymin = ci_lower, ymax = ci_upper),
                 linewidth = 1.8, color = COLOR_ESTIMATE) +
  geom_point(size = 3.5, color = COLOR_ESTIMATE) +
  geom_vline(xintercept = -1, linetype = "dotted", linewidth = 0.4) +
  scale_x_continuous(breaks = unique(es_df$rel_time[es_df$rel_time <= 0])) +
  labs(x = "距首次进入 TOP500 的年数", y = "系数：GDP 增长率（百分点）",
       caption = sprintf("注：仅显示处理前各期。处理前系数最大绝对值 = %.3f；处理后 t=0~3 均值 = %.3f；比值 = %.2f。参考期：t = -1。",
                         max_pre, post_avg, ratio_val))

ggsave("reports/did_diagnostics/pretrend_diagnostic.pdf", p_pretrend,
       width = 7.5, height = 4.8, device = cairo_pdf)
ggsave("outputs/figures/pretrend_diagnostic.png", p_pretrend,
       width = 7.5, height = 4.8, dpi = 300)

# =====================================================================
# 图4: 处理状态热力图
# =====================================================================
iso_order <- df %>%
  distinct(iso3, first_compute) %>%
  arrange(first_compute, iso3) %>%
  pull(iso3)

df_h <- df %>% mutate(iso3 = factor(iso3, levels = iso_order))

# Only show the 44 treated countries + annotate the never-treated
treated_isos <- df_h %>%
  filter(treated_binary == 1) %>%
  pull(iso3) %>%
  unique()

df_h_plot <- df_h %>% filter(iso3 %in% treated_isos)

p_heat <- ggplot(df_h_plot, aes(x = year, y = iso3, fill = factor(treated_binary))) +
  geom_tile(color = "white", linewidth = 0.15) +
  scale_fill_manual(
    values = c("0" = "#F7F7F7", "1" = COLOR_ESTIMATE),
    labels = c("0" = "未进入 TOP500", "1" = "已进入 TOP500"),
    name = "") +
  scale_x_continuous(breaks = 2015:2023, expand = c(0, 0)) +
  scale_y_discrete(limits = rev) +
  labs(x = "年份", y = "国家（按首次进入 TOP500 年份排序）",
       caption = sprintf("注：仅显示曾进入 TOP500 的 44 个处理组国家。另有 141 个从未进入的国家，因始终为 0 故不展示。%d 个国家中 35 个在首年即进入 TOP500。",
                         sum(df_h_plot$treated_binary > 0 & df_h_plot$year == df_h_plot$first_compute, na.rm = TRUE))) +
  theme_minimal(base_size = 11, base_family = "sans") +
  theme(
    panel.grid = element_blank(),
    axis.text.y = element_text(size = 5.5, hjust = 1, family = "sans"),
    axis.title = element_text(size = 11),
    axis.text.x = element_text(size = 10),
    legend.position = "bottom",
    legend.title = element_blank(),
    legend.text = element_text(size = 9),
    plot.caption = element_text(size = 8.5, hjust = 0, color = "grey40",
                                margin = margin(t = 10)),
    plot.margin = margin(12, 12, 8, 12)
  )

ggsave("reports/did_diagnostics/treatment_heatmap.pdf", p_heat,
       width = 8.5, height = 11, device = cairo_pdf)
ggsave("outputs/figures/treatment_heatmap.png", p_heat,
       width = 8.5, height = 11, dpi = 300)

# =====================================================================
# 图5: 计算能力分布（双面板）
# =====================================================================
p_hist <- ggplot(df %>% filter(log_total_rmax > 0), aes(x = log_total_rmax)) +
  geom_histogram(bins = 45, fill = COLOR_ESTIMATE, alpha = 0.8, color = "white", linewidth = 0.2) +
  geom_vline(aes(xintercept = mean(log_total_rmax, na.rm = TRUE)),
             linetype = "dashed", color = COLOR_REFERENCE, linewidth = 0.8) +
  annotate("text", x = mean(df$log_total_rmax[df$log_total_rmax > 0], na.rm = TRUE) + 0.3,
           y = Inf, label = sprintf("均值 = %.2f", mean(df$log_total_rmax[df$log_total_rmax > 0], na.rm = TRUE)),
           vjust = 2, size = 3.5, color = COLOR_REFERENCE) +
  labs(x = "log(Total Rmax，GFlops)", y = "国家-年份观测数")

top12 <- df %>%
  filter(log_total_rmax > 0) %>%
  group_by(iso3) %>%
  summarise(total_rmax = sum(log_total_rmax, na.rm = TRUE), .groups = "drop") %>%
  slice_max(total_rmax, n = 12) %>%
  pull(iso3)

df_top <- df %>%
  filter(iso3 %in% top12, year >= 2015) %>%
  group_by(iso3) %>%
  mutate(label_pos = if_else(year == max(year), log_total_rmax, NA_real_)) %>%
  ungroup()

p_top <- ggplot(df_top, aes(x = year, y = log_total_rmax, color = iso3, group = iso3)) +
  geom_line(linewidth = 0.9) +
  geom_point(size = 1.5) +
  scale_color_viridis_d(option = "D", end = 0.9) +
  # Direct labeling at line ends
  ggrepel::geom_text_repel(
    data = df_top %>% filter(!is.na(label_pos)),
    aes(label = iso3),
    hjust = -0.2, size = 3.2, direction = "y",
    segment.color = "grey80", segment.size = 0.2,
    show.legend = FALSE) +
  labs(x = "年份", y = "log(Total Rmax，GFlops)") +
  theme(legend.position = "none") +
  coord_cartesian(xlim = c(2015, 2025))

p_compute <- grid.arrange(
  p_hist, p_top, ncol = 2,
  bottom = grid::textGrob(
    sprintf("注：左图为 log 计算能力分布（非零观测：%d 个，覆盖 %d 个国家）。右图为前 12 名国家轨迹。数据来源：TOP500。",
            sum(df$log_total_rmax > 0), n_distinct(df$iso3[df$log_total_rmax > 0])),
    x = 0.02, hjust = 0,
    gp = grid::gpar(fontsize = 8.5, col = "grey40")))

ggsave("reports/did_diagnostics/compute_distribution.pdf", p_compute,
       width = 12, height = 5.5, device = cairo_pdf)
ggsave("outputs/figures/compute_distribution.png", p_compute,
       width = 12, height = 5.5, dpi = 300)

# =====================================================================
# 图6: 安慰剂检验——二元随机化推断
# =====================================================================
set.seed(42); n_rep <- 2000
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
       caption = "注：随机打乱各国首次进入 TOP500 的年份后重估处理效应。红色竖线为真实估计值。p 值为 |安慰剂| ≥ |真实值| 的比例。")

ggsave("reports/did_diagnostics/placebo_randomization.pdf", p_pl,
       width = 7, height = 5, device = cairo_pdf)
ggsave("outputs/figures/placebo_randomization.png", p_pl,
       width = 7, height = 5, dpi = 300)

# =====================================================================
# 图7: 安慰剂检验——连续处理
# =====================================================================
set.seed(43); n_rep_c <- 2000
formula_cont <- as.formula(paste("growth_pct ~ log_total_rmax +",
                                  paste(controls_base, collapse = " + "),
                                  "| unit_id + year"))
est_cc <- df[complete.cases(df[, c("growth_pct", "log_total_rmax", controls_base)]), ]
true_cont <- feols(formula_cont, data = est_cc, cluster = ~iso3)
tcc <- coef(true_cont)["log_total_rmax"]
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
       caption = "注：在年份内随机打乱 log(Total Rmax) 后重估连续处理效应。红色竖线为真实估计值。控制变量同主回归。")

ggsave("reports/did_diagnostics/placebo_continuous.pdf", p_cp,
       width = 7, height = 5, device = cairo_pdf)
ggsave("outputs/figures/placebo_continuous.png", p_cp,
       width = 7, height = 5, dpi = 300)

# =====================================================================
# 图8: 系数稳定性
# =====================================================================
m_raw  <- feols(growth_pct ~ log_total_rmax | unit_id + year, data = est_cc, cluster = ~iso3)
m_hc   <- feols(growth_pct ~ log_total_rmax + pwt_human_capital_index_lag1 | unit_id + year,
                data = est_cc, cluster = ~iso3)
m_inv  <- feols(growth_pct ~ log_total_rmax + pwt_human_capital_index_lag1 + pwt_investment_share_lag1 | unit_id + year,
                data = est_cc, cluster = ~iso3)
m_full <- true_cont

stab <- data.frame(
  model = rev(c("仅固定效应", "+\u00a0人力资本", "+\u00a0投资率", "+\u00a0TFP + 贸易")),
  coef  = c(coef(m_raw)["log_total_rmax"], coef(m_hc)["log_total_rmax"],
            coef(m_inv)["log_total_rmax"], coef(m_full)["log_total_rmax"]),
  se    = c(se(m_raw)["log_total_rmax"], se(m_hc)["log_total_rmax"],
            se(m_inv)["log_total_rmax"], se(m_full)["log_total_rmax"])
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
       caption = sprintf("注：逐步加入控制变量。全部包含国家与年份固定效应，标准误在国家层面聚类。N = %d，%d 个国家。",
                         nobs(m_full), length(unique(est_cc$iso3))))

ggsave("reports/did_diagnostics/coef_stability.pdf", p_stab,
       width = 7.5, height = 3.5, device = cairo_pdf)
ggsave("outputs/figures/coef_stability.png", p_stab,
       width = 7.5, height = 3.5, dpi = 300)

# =====================================================================
# 图9: 完整回归表（text）
# =====================================================================
etable(m_raw, m_hc, m_inv, m_full, cluster = ~iso3,
       headers = c("仅固定效应", "+ 人力资本", "+ 投资率", "+ TFP+贸易"),
       file = "reports/did_diagnostics/regression_etable.txt")

# =====================================================================
# 诊断摘要
# =====================================================================
cat("\n====== 诊断摘要 ======\n")
cat(sprintf("面板：%d 个国家 × %d 年 = %d 个观测（平衡面板）\n",
            n_distinct(df$iso3), n_distinct(df$year), nrow(df)))
cat(sprintf("连续处理（log_total_rmax）：系数=%.4f（标准误=%.4f，p=%.4f）\n",
            tcc, se(true_cont)["log_total_rmax"], pvalue(true_cont)["log_total_rmax"]))
cat(sprintf("二元处理（treated_binary）：系数=%.4f（p=%.4f）\n",
            true_coef, pvalue(true_mod)["treated_binary"]))
cat(sprintf("二元安慰剂 p=%.4f，连续安慰剂 p=%.4f\n", placebo_pval, cpval))
cat(sprintf("平行趋势：处理前 max|系数|=%.4f，处理后均值=%.4f，比值=%.2f\n",
            max_pre, post_avg, ratio_val))
cat(sprintf("N=%d，R²=%.3f，调整组内 R²=%.3f\n",
            nobs(true_cont), r2(true_cont), r2(true_cont, "war2")))
cat("\n完成。\n")

showtext_auto(FALSE)
