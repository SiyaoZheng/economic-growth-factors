# 项目规程：各国经济增长影响因素研究
> **⚠️ tool_disabled**: This agent runs on DeepSeek, which is NOT a multimodal model. The `view_image` tool will always fail. Do NOT use `view_image` under any circumstances. If you need to inspect an image, describe it to the user and ask them to describe what they see.

本项目构建 1960 年起的跨国-年份面板数据，研究各国经济增长的关联因素。

**目标期刊**：《管理世界》级别。所有实证工作必须经得起国内顶级期刊的审稿标准。

---

## 一、研究设计纪律

### 1.1 核心识别策略

- 所有面板回归必须包含**国家固定效应**和**年份固定效应**，除非有明确的理论理由豁免。
- 标准误必须**在国家层面聚类**（cluster at country level）。
- 控制变量必须**滞后一期**（lagged one year），已在 pipeline 中实现为 `{variable}_lag1`。
- 任何变量不得使用**未来值**构建当期回归量。

### 1.2 数据规范

- `iso3 + year` 是唯一合并键。不允许模糊匹配。
- 无法安全映射到 ISO3 的实体必须在 `country_crosswalk.csv` 中显式处理，**禁止静默映射**。
- **禁止均值填补**（no mean imputation）。
- **禁止跨国插值**（no cross-country interpolation）。
- 只有来源文件明确标记为估计值的可以前向填充（如 Barro-Lee 五年期数据在五年窗口内 forward-fill）。
- `data/raw/` 中的原始文件是只读的。所有变换通过 pipeline 脚本完成。
- ⚠️ **禁止直接或间接修改原始数据文件**。如果需要修改原始数据（包括但不限于修正编码错误、补充缺失的源文件字段、修改 Excel/CSV/JSON 中的值），必须停下来向我确认。我的确认将包括：修改什么文件、为什么修改、修改后对分析结果的影响。

### 1.3 样本规则

- 最终分析面板保留 `year >= 1960` 的行。
- 1960 年之前的数据仅用于计算 1960 年起的滞后增长率（pipeline 中 `LAG_BUFFER_START_YEAR = 1950`）。

---

## 二、可复现性标准

### 2.1 Pipeline 规范

- 数据下载、处理、验证必须通过 `scripts/run_pipeline.py` 一步运行。
- 每个处理步骤必须在 `scripts/*.py` 中显式编码——**禁止手动在 Excel/Stata 中修改数据**。
- 每次修改 pipeline 后必须重新运行 `run_pipeline.py`，确保 `data/processed/` 中的输出可再生。

### 2.2 版本控制

- 自动快照每 15 分钟运行一次（见 `docs/git_automation.md`）。
- `.gitignore` 中 `data/raw/*`、`data/interim/*`、`data/processed/*` 被忽略——所有输出必须可重现，不纳入版本库。
- 提交信息格式：`autosnapshot: YYYY-MM-DD HH:MM`。
- 不允许 `git commit --amend` 或 `git rebase` 改写已推送的历史。

### 2.3 计算环境

- Python 依赖列在 `requirements.txt` 中。新增依赖必须同时更新该文件。
- 数据处理用 **Polars**（不是 pandas），以保证性能和内存可控。

---

## 三、分析标准

### 3.1 回归报告规范

所有回归表格必须报告：

1. 系数和聚类标准误（或置信区间）
2. 观测数 N
3. 国家数（或聚类数）
4. R²（组内/总体）
5. 固定效应层级（国家 + 年份）
6. 因变量均值（便于评估经济显著性）

### 3.2 结果稳健性

以下稳健性检查必须至少覆盖主要结果：

- 排除中国（验证结果是否由单一国家驱动）
- 排除高收入 OECD 国家（聚焦发展中国家）
- 不同因变量构造（年增长 / 5 年 / 10 年窗口）
- 不同增长来源（PWT vs Maddison vs WDI）
- 极值增长观测排除（`|growth_annual| > 0.30`）

### 3.3 来源交叉验证

- 对 `growth_annual`（PWT 来源）与 `wdi_gdp_growth_annual_pct` 和 `maddison_growth_annual` 做相关系数报告。
- 差异 `> 0.10 log points` 的观测必须审查原因。pipeline 已将此类写入 `reports/source_consistency.csv`。

---

## 四、文档纪律

### 4.1 所有新变量的添加流程

1. 更新 `docs/variable_dictionary.csv`（概念、来源、单位、覆盖年份、变换规则、滞后规则、缺失处理）。
2. 更新 `docs/data_inventory.md`（来源 provenance、角色、状态）。
3. 在 pipeline 中实现下载和处理。
4. 重新运行 `validate_outputs.py`，检查覆盖率变化。
5. 重新生成 `docs/data_inventory.md` 中的统计摘要。

### 4.2 禁止的行为

- 不允许写代码时用单字母变量名（如 `x`、`df`、`y`）。
- 不允许在数据分析代码中添加不必要的内联注释——代码自解释优先。
- 不允许使用 `set_index()` 或 `reset_index()`——Polars 不支持这些，用原生的 select/filter/with_columns。
- 不允许在论文写作或分析中使用 Excel/Stata 手动操作数据；所有数据变换必须通过 Python pipeline 追溯。

---

## 五、沟通与协作

- 我是计算社会科学研究者 Adrian（Siyao Zheng），你可以用中文或英文与我交流。
- 在引入新数据源、新变量、新分析方法前，先向我确认研究设计选择。
- 如果 pipeline 运行结果不符合预期，展示证据（覆盖率、相关系数、极端值）后我们再讨论原因。
- 所有外部事实、库文档、方法建议应当有可验证的来源，不要凭空给出。

---

## 六、数据来源索引（已有）

| 来源 | 版本 | 角色 | 状态 |
|---|---|---|---|
| Penn World Table | 11.0 | 主要 GDP、人口、人力资本、TFP、投资和贸易份额 | ✅ 已完成 |
| Maddison Project Database | 2023 | GDP per capita 验证来源 | ✅ 已完成 |
| World Development Indicators | 当前 API | 官方增长、人口、贸易、投资、部门份额、城市化、预期寿命 | ✅ 已完成 |
| V-Dem | v16 | 民主、制度、政治竞争、行政约束 | 📋 计划中 |
| QoG Standard Time-Series | — | 治理、腐败、国家能力、政体指标 | 📋 计划中 |
| CEPII GeoDist | — | 距离、内陆国、语言、边界、殖民关系 | 📋 计划中 |
| Barro-Lee | — | 教育成就与就学结构 | 📋 计划中 |
| UN WPP | 2024 | 年龄结构、人口、预期寿命 | 📋 计划中 |


## 七、对 AI Agent 的坑位警示

以下是根据本项目中 agent 多次踩坑总结的操作纪律，每次 pipeline 修改前务必温习。

### 7.1 Pipeline 运行：只跑必要的步骤

- `scripts/run_pipeline.py` 会先调用 `download_data.py`，而本项目网速慢、WDI API 经常超时。**如果需要重新构建面板但不需要重新下载数据，务必直接运行 `build_panels.py` 而不是 `run_pipeline.py`**。除非 Adrian 明确要求重新下载，否则只改 `build_panels.py` 并直接运行它。
- 同理，改了 `validate_outputs.py` 只跑它，不要重跑整个 pipeline。

### 7.2 WDI 数据获取：用最大的 `per_page` 避免分页超时

- WDI API 分页请求会导致连接池超时（每页一次 TCP 握手 + SSL + 传输），在网速差的环境下极易失败。
- **一次性下载时设 `per_page=30000`**（远大于 indicator 实际记录数），避免分页。
- 如果 API 仍然超时，考虑用 `wbdata` 库（但它的 `date` 参数格式不同，需要手动过滤年份）。
- `build_panels.py` 的 `clean_wdi()` 和 `require_raw_inputs()` **已经做了容错**：缺失的 WDI indicator 文件会打印警告并跳过，不会中断整个 pipeline。如果某个 WDI 指标的 raw JSON 不在 `data/raw/wdi/` 下，pipeline 会自动跳过它。不要因为一两个缺失指标让整个面板构建失败。
- 缺失的指标需要在 `docs/variable_dictionary.csv` 中将状态标为 `blocked`，并在 `docs/data_inventory.md` 中注明原因。

### 7.3 Polars API 陷阱

- `pl.Series` 没有 `.height` 属性，用 `.len()`。
- 不要用 `reset_index()` 或 `set_index()`——Polars 不支持 pandas 风格的索引操作。
- 使用 `pl.read_parquet()` 而非 pandas 的 `read_parquet()`。
- `df[col].null_count()` 返回的是 `int`，不需要 `.len()`。

### 7.4 面板合并：不要破坏主键唯一性

- `iso3 + year` 是唯一主键。合并 WDI、Maddison 到 PWT 后，**务必检查是否有 duplicated keys**。
- 如果某个 merge 引入了重复行（如 WDI 中同一国家-年份有多个 `country_wdi` 变体），在 pivot 后检查行数是否与 PWT 基准一致。

### 7.5 `apply_patch` 命令格式

- 使用 `*** Begin Patch` / `*** End Patch` 包裹。
- 每行 patch 不额外加反引号或其他包裹符号。
- 如果多次尝试 `apply_patch` 失败，直接用 Python heredoc (`python3 << 'PYEOF'`) 编辑文件——简单可靠。

### 7.6 工具选择

- 使用 `rg`（ripgrep）而非 `grep` 做文本搜索。
- 网页审计报告直接用 Python 生成 HTML——polars 读数据、`html.escape()` 处理转义、字符串拼接输出，不需要外部报告库。
- 如果需要从 World Bank API 下载数据，优先用 `requests` + `per_page=30000`，备选 `wbdata` 库。不要用 `download_data.py` 的默认分页设置（`per_page=500` 在慢网下会超时）。
- WDI 的 indicator code 末尾 `.ZS` 表示 percent of total，`.KD.ZG` 表示 constant-price growth rate——不要在变量字典里写错单位。

### 7.7 验证报告完整性

- `validate_outputs.py` 会生成以下所有报告文件，缺一不可：
  - `reports/validation_report.md`
  - `reports/extreme_growth_annual.csv`
  - `reports/source_consistency.csv`
  - `reports/output_hashes.json`
  - `reports/coverage_report.html`
  - `reports/coverage_table.csv`
- 每次修改 pipeline 后，必须确认以上 6 个文件全部存在且时间戳更新。

### 7.8 R/ggplot2 图表输出规范

- **双重格式**：每张图必须同时输出 PDF（矢量，`device = cairo_pdf`）和 PNG（`dpi = 300`），分别存到 `reports/did_diagnostics/` 和 `outputs/figures/`。
- `run_did_diagnostics.R` 和 `run_did_placebo_only.R` 共用同名 PNG 输出路径，不要同时运行两个脚本。
- **中文字体**：所有轴标签、图注、direct labeling 必须用中文，通过 `showtext` + `font_add("heiti", "/System/Library/Fonts/STHeiti Light.ttc")` 实现。
- **AER 规范**：参照 `docs/AER_figure_guidelines.md`，去掉 title/subtitle，用 caption 传递信息；用 direct labeling 替代 legend；颜色用 ColorBrewer Dark2（`#1B9E77`、`#D95F02`、`#377EB8`、`#E41A1C`）；主题用 `theme_minimal` + 浅灰网格线。
- **热力图**：`axis.text.y` 字体不小于 5.5pt，画布不小于 8.5×11 英寸；热力图独立 theme 必须带 `base_family = "sans"`，否则中文字体渲染缺失。
- **R 脚本编辑**：`apply_patch` 不可用时，直接用 `python3 << 'PYEOF'` 读-改-写 R 脚本。

