# AER 图表规范与经济学数据可视化最佳实践

> 整理时间：2026-07-04
> 目标期刊：《管理世界》级别（对标 AER 标准）

---

## 一、AER 官方图表规范

来源：AEA Style Guide (https://www.aeaweb.org/journals/aer/style-guide)

### 1.1 图文件格式
- **必须提供矢量图**：vector PDF、EPS、AI、WMF 或 PPT。
- 如字体中有变量（斜体）或矩阵/向量（粗体），字体必须嵌入。
- 多面板图：用字母标记各面板（Figure1a.pdf, Figure1b.pdf, ...）。

### 1.2 图注与来源说明
- 来源注释放在图的其他注释之后。
- 来源的完整引用列入参考文献。

### 1.3 表格规范（配套要求）
- 纵向（portrait）排版，不超过 9 列（含行标题）。
- 仅使用水平线和额外空白来区分，**不使用底纹/颜色填充**。
- 列标题不缩写。
- 用 Panel A, Panel B 区分表的子部分。
- 小数前面加 0（0.357 而非 .357）。
- 表注用小写字母（a, b, c），**不用星号表示显著性**，标准误用括号报告。
- 来源注释排在最后。

---

## 二、Schwabish (2014): "An Economist's Guide to Visualizing Data" (JEP)

Jonathan Schwabish 在 Journal of Economic Perspectives 发表的经典指南，至今仍是经济学数据可视化的必读文献。

### 2.1 三大核心原则
1. **展示数据**（Show the data）：让读者看到数据本身，而不仅仅是摘要统计量。
2. **减少杂乱**（Reduce the clutter）：去除不必要的网格线、边框、装饰元素。
3. **整合文本与图表**（Integrate the text and the graph）：图表标题、注释、标签应帮助读者直接理解关键信息，而不必反复回看正文。

### 2.2 图表设计十项指南
1. **选择正确的图表类型**：
   - 趋势 → 折线图（line chart）
   - 分布 → 直方图/密度图（histogram/density）
   - 比较 → 条形图（bar chart），且**条形图基线必须为0**
   - 关系 → 散点图（scatter plot）
2. **避免双 y 轴**：容易误导读者，优先用分面（facet）或索引化（indexed）。
3. **去除 chartjunk**：去掉不必要的 3D 效果、阴影、渐变背景、装饰性元素。
4. **使用直接标签**：尽可能将标签直接放在数据系列旁边，而不是用图例（legend）。
5. **颜色要有目的性**：
   - 使用调和的颜色方案（qualitative 用于分类，sequential/diverging 用于连续变量）
   - 避免默认的 ggplot2/R 鲜艳颜色
   - 考虑色盲友好（推荐 viridis 或 ColorBrewer）
   - 不要在彩色背景上叠加透明元素
6. **标注要清晰**：轴标签、刻度标签字体大小应足够大（不小于正文大小）。
7. **坐标轴范围要合理**：除条形图外，不强制包含0；但应让数据占据图表主要区域。
8. **分面优于多线叠加**：超过 3-4 条线在同一图中难以区分，考虑分面。
9. **标题要传递信息**：使用陈述性/结论性标题（"Treatment increases growth by 2.3pp"）而非描述性标题（"Growth by treatment status"）。
10. **表格也是可视化**：注意对齐、小数点位数、使用微缩图（sparklines）嵌入表格。

### 2.3 报告/演示用图与论文用图的区别
- **论文用图**：可以有更多细节、更小的字体、更多的注释文字。读者会近距离仔细阅读。
- **演示/幻灯片用图**：极简化，字体更大，核心信息一条。

---

## 三、Kieran Healy: "Data Visualization: A Practical Introduction" (socviz.co)

### 3.1 核心哲学
- **"感知规则"优先**：理解人类视觉系统如何解码图形属性（Cleveland & McGill 的感知准确性排序：位置 > 长度 > 角度/斜率 > 面积 > 体积 > 颜色饱和度/色相）。
- **优雅胜过花哨**：好的学术图表是"elegant"而非"flashy"——清晰、准确、克制。

### 3.2 实践建议
1. **一律用矢量输出**：ggsave 设置 `device = cairo_pdf` 或直接 `.pdf`，避免 `.png` 锯齿。
2. **字体嵌入**：学术期刊要求字体可嵌入 PDF，使用 `extrafont` 或系统字体。
3. **主题选择**：`theme_minimal()` 或 `theme_bw()` 是好的起点，去掉顶部和右侧边框。
4. **不要用默认颜色**：R 默认调色板（尤其是 base R 的色板）饱和度太高，不适合学术发表。
5. **图注（caption）先行**：Healy 建议把关键信息放在 caption 而非 title 中（与 Schwabish 略有不同——取决于读者阅读习惯）。

---

## 四、Gelman 与经济学家博客圈的共识

### 4.1 Andrew Gelman (Columbia 统计系)
- **不要 smooth 掉有趣的 variance**：事件研究图中的置信区间很重要，不要只画平滑曲线。
- **用 direct labeling** 替代 legend：尤其在多线图中，把国家名/变量名直接标注在线旁边。
- **y 轴标签要明确**：不要写 "GDP"，写 "GDP per capita growth (annual, %)"。

### 4.2 经济学术圈共识（多位经济学家博客总结）
- **事件研究法图的"行业标准"**：
  - x 轴：相对时间（-5 到 +5 或类似）
  - y 轴：系数 + 置信区间
  - 基准期（t=-1）用虚线标记
  - 处理发生点用灰色阴影区域或竖直线标记
  - 不要标题，用 caption 解释
- **系数图（coefplot）**：
  - 竖线表示点估计 + 置信区间
  - 0 线用虚线
  - 按大小排列，不要按字母
  - 分组用标签区分（如"Controls"和"Variables of interest"）
- **散点图/binscatter**：
  - 用 binned scatter 代替 raw scatter 以避免过度绘图
  - 添加线性拟合线和置信带
  - 标注斜率系数和标准误

---

## 五、具体图表类型的规范

### 5.1 折线图（Trends / Event Study）
- 2-3 条线为宜，超过 4 条考虑分面
- 每条线用可区分的颜色（ColorBrewer Set1 或 viridis）
- 置信带用半透明填充，透明度 0.15-0.3
- 关键事件用竖虚线标记
- x 轴标签不旋转或 45° 旋转
- 直接标注曲线（direct labeling）优于图例

### 5.2 柱状图/条形图
- **基线必须为 0**（这是铁律）
- 条形宽度 > 间距宽度
- 纵向条形图横轴标签若太长可 45° 旋转
- 用水平条形图可能是更好的选择（尤其标签长时）

### 5.3 热力图
- 颜色梯度从浅到深（sequential palette）
- 标注缺失值为灰色或白色
- y 轴排序要有意义（不是字母序）
- 网格线细且浅色

### 5.4 直方图/分布图
- bin 数量用 Freedman-Diaconis 或 Scott 规则，或固定 30-50 bins
- 叠加核密度曲线时，y 轴改为 density 而非 count
- 关键阈值用竖线标注
- 颜色用单一色系（如蓝色），不要多色

### 5.5 系数稳定性图（Coefplot）
- 水平排列，不用垂直（除非横向空间不足）
- 0 参考线必须清晰
- 模型名在 y 轴（靠左）
- 点估计 + 1.96 SE 线段
- 可加入参考区间（如 ±0.05 的灰色带）表示"经济显著性"

---

## 六、R/ggplot2 学术图表最佳实现

### 6.1 推荐的 ggplot2 theme 设置
```r
theme_aej <- theme_minimal(base_size = 11) +
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major = element_line(linewidth = 0.2, color = "grey85"),
    axis.title = element_text(size = 10),
    axis.text  = element_text(size = 9),
    plot.caption = element_text(size = 8, hjust = 0, color = "grey40"),
    legend.position = "bottom",
    legend.title = element_blank(),
    plot.title = element_blank(),      # 不在图上放标题
    plot.subtitle = element_blank()    # 用 caption 代替
  )
```

### 6.2 输出设置
```r
ggsave("figure.pdf", plot, 
       width = 7, height = 5,  # 黄金比例 ≈ 1.4:1 或 1.6:1
       device = cairo_pdf,
       dpi = 300)
```

### 6.3 字体
- 推荐：Palatino, Computer Modern (LaTeX 默认), 或 Times New Roman
- 中文论文：宋体/仿宋 + 英文字体混排

### 6.4 颜色调色板
```r
# 定性（分类变量，如不同国家组）
library(RColorBrewer)
display.brewer.pal(8, "Set1")    # 鲜艳分类
display.brewer.pal(8, "Dark2")   # 沉稳分类
display.brewer.pal(8, "Set2")    # 柔和分类（推荐学术用）

# 连续/发散
scale_fill_viridis_c(option = "viridis")   # 色盲友好
scale_fill_distiller(palette = "RdBu")     # 发散（正负值）
```

---

## 七、对本项目的直接应用清单

对照我们的 `scripts/run_did_diagnostics.R` 当前产出：

### 当前问题
1. **raw_trends.pdf**: 
   - 2 条线，OK
   - 置信带，OK ✓
   - 缺少 direct labeling → 应把图例放在图内/直接标注在线的末端
   - y 轴标签是英文 → 中文论文应为中文
   - 有图例但无直接标签
2. **event_study_twfe.pdf**:
   - 标准事件研究规范 ✓
   - 缺少 meaningful caption
   - y 轴标签、x 轴标签应为中文
3. **pretrend_diagnostic.pdf**:
   - x 轴只有处理前期，OK
   - 缺少说明文字
4. **treatment_heatmap.pdf**:
   - 排序正确 ✓
   - y 轴国家缩写太小（3.5pt）
   - 缺少有信息量的 caption
5. **compute_distribution.pdf**:
   - 双面板布局 OK
   - 颜色使用 OK
6. **placebo_*.pdf**:
   - 直方图规范 ✓
   - 缺少直接标注（p 值应直接标注在图上而非仅在 subtitle）
7. **coef_stability.pdf**:
   - 水平 coefplot ✓
   - 0 参考线 ✓
   - 中文标签 OK

### 需要统一的改进
1. 全部中文化（轴标签、图注、变量名）
2. 去除所有 title/subtitle（已完成 ✓）
3. 添加有信息量的 caption（数据来源、方法、N 等）
4. 用 direct labeling 替代 legend
5. 统一颜色方案
6. 字体大小统一
7. 输出格式确认（PDF 矢量图 ✓）

