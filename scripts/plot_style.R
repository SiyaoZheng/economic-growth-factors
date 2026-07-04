# =============================================================================
# plot_style.R — 统一绘图样式配置
# 所有绘图脚本 source 此文件以保持视觉一致性
# =============================================================================

library(ggplot2)

# ---- 颜色系统 ---------------------------------------------------------------
# 主色调：蓝/红/灰
PRIMARY_BLUE   <- "#1565C0"   # 主色：系数线、直方图、热力图 treated
SECONDARY_BLUE <- "#2196F3"   # 辅蓝：趋势图 "Ever in TOP500" 组
ORANGE         <- "#FF9800"   # 橙色：趋势图 "Never in TOP500" 组
WARNING_RED    <- "#D32F2F"   # 警示红：真值竖线
BG_LIGHT       <- "#F5F5F5"   # 浅灰：热力图 untreated 格子
SHADOW_GREY    <- "grey90"    # 暗灰：事件研究 treatment onset 阴影
ANNOTATION_RED <- "darkred"   # 注释红：vline 示例文字

# ---- 全局 ggplot 主题 -------------------------------------------------------
theme_set(theme_minimal(base_size = 13))

# ---- ggsave 输出统一参数 ----------------------------------------------------
GGSAVE_DEFAULTS <- list(
  dpi        = 300,
  bg         = "white",
  create.dir = TRUE
)

# 快捷包装函数：统一 dpi 和背景
save_figure <- function(filename, plot, width = 10, height = 6, ...) {
  args <- c(list(filename = filename, plot = plot, width = width, height = height),
            GGSAVE_DEFAULTS)
  if (...length() > 0) {
    args <- modifyList(args, list(...))
  }
  do.call(ggsave, args)
}

# ---- 常用图形几何参数 -------------------------------------------------------
GEOM_LINE_LW     <- 1.3   # 主趋势线宽
GEOM_RIBBON_ALPHA <- 0.15 # 置信带透明度
GEOM_POINT_SIZE  <- 2.5   # scatter 点大小
GEOM_PT_LARGE    <- 3.0   # 大号点
GEOM_PT_XLARGE   <- 3.5   # 超大号点
GEOM_LINERANGE_LW <- 1.2  # linerange 线宽
GEOM_LINERANGE_LW_WIDE <- 1.5  # 宽 linerange
GEOM_HIST_ALPHA  <- 0.75  # 直方图透明度
GEOM_HIST_BINS   <- 50    # 直方图 bin 数
GEOM_HIST_BINS_LARGE <- 40  # 大数据直方图 bin 数
GEOM_TILE_LW     <- 0.08  # 热力图格子线宽
GEOM_VLINE_LW    <- 0.8   # 参考线宽
GEOM_TRUE_VLINE_LW <- 1.5 # 真值参考线宽

# ---- 图形输出尺寸规范 -------------------------------------------------------
FIGURE_SIZES <- list(
  standard    = list(width = 10, height = 6),
  narrow      = list(width = 9,  height = 4.5),
  square      = list(width = 8,  height = 6),
  wide        = list(width = 14, height = 6),
  heatmap     = list(width = 12, height = 10)
)

# ---- 颜色 palettes ----------------------------------------------------------
COLOR_TREND_MAP <- c(
  "Ever in TOP500 (N=44)"    = SECONDARY_BLUE,
  "Never in TOP500 (N=141)"  = ORANGE
)

FILL_TREND_MAP <- c(
  "Ever in TOP500 (N=44)"    = SECONDARY_BLUE,
  "Never in TOP500 (N=141)"  = ORANGE
)

COLOR_HEATMAP_MAP <- c(
  "0" = BG_LIGHT,
  "1" = PRIMARY_BLUE
)

HEATMAP_LABELS <- c(
  "0" = "No TOP500",
  "1" = "In TOP500"
)

cat("✓ plot_style.R loaded: theme_minimal(base_size=13), dpi=300, bg=white\n")
