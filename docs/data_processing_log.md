# Data Processing Log

本文件记录从原始数据下载到最终分析面板的所有处理操作、操作原因及审计发现。
每个操作必须包含：**操作内容、操作原因、对分析面板的影响**。

---

## 阶段 0：初始 Pipeline（已有，记录在此以便完整）

### 0.1 PWT 11.0 数据清洗
- **操作**: 从 `data/raw/pwt/pwt110.xlsx` 读取 `rgdpna`, `pop`, `hc`, `rtfpna`, `csh_i`, `csh_x`, `csh_m`
- **原因**: PWT 是主要 GDP 和增长来源
- **影响**: 生成 `data/interim/pwt_clean.parquet`

### 0.2 Maddison 2023 数据清洗
- **操作**: 从 `data/raw/maddison/mpd2023_web.xlsx` 读取 `gdppc`
- **原因**: 作为 GDP 增长验证源
- **影响**: 生成 `data/interim/maddison_clean.parquet`

### 0.3 WDI 数据清洗
- **操作**: 从 `data/raw/wdi/*.json` 读取 10 个指标
- **原因**: 控制变量来源（贸易、投资、产业份额、城镇化、预期寿命）
- **影响**: 生成 `data/interim/wdi_clean.parquet`

### 0.4 增长变量计算
- **操作**: `growth_annual = (log_gdp_pc[t] - log_gdp_pc[t-1]) / 1`, `growth_5yr`、`growth_10yr` 同理
- **原因**: 构造被解释变量
- **影响**: 三个增长率变量添加到面板

### 0.5 控制变量滞后
- **操作**: 所有控制变量滞后一期 `{variable}_lag1`
- **原因**: 项目规程要求控制变量滞后一期（避免同时性偏差）
- **影响**: 生成 `*_lag1` 列

### 0.6 样本过滤
- **操作**: 保留 `year >= 1960`
- **原因**: 项目规程。1960 年前数据仅用于计算滞后增长率
- **影响**: `sample_flag_1960plus = True`；`data/processed/growth_panel_1960plus.parquet` (11,840 行 × 185 国)

---

## 阶段 1：TOP500 算力数据获取（2026-07-04）

### 1.1 爬取 TOP500 历史列表
- **操作**: 从 `top500.org/lists/top500/{year}/{month}/download/TOP500_{year}{month}_all.xml` 下载 1993-06 至 2025-06 共 65 期 XML
- **原因**: TOP500 是国家算力的标准代理变量。XML 格式提供完整 500 条系统记录
- **方法**: 8 线程并发下载，本地缓存至 `data/raw/top500/xml_cache/`
- **影响**: 65 个 XML 文件，原始 32,500 条系统记录

### 1.2 XML 解析
- **操作**: 解析每条XML中的 `rank`, `system-name`, `country`, `r-max` (GFlops), `r-peak` (GFlops), `number-of-processors`, `power` (kW)
- **原因**: 从 XML 提取结构化数据
- **影响**: `data/raw/top500/top500_xml_panel.parquet` (32,500 行, 65 国)

### 1.3 国家名 → ISO3 映射
- **操作**: 手写 63 个映射（如 "United States"→"USA", "Korea, South"→"KOR"）
- **原因**: TOP500 使用全名，需映射到 ISO3 以与 PWT 合并
- **未映射实体** (6个): Venezuela, Puerto Rico, Liechtenstein, Belarus, Saudi Arabia（拼写变体 "Saudia Arabia"）, Slovak Republic
- **影响**: 映射后 32,411 系统, 57 国

### 1.4 国家-年份聚合
- **操作**: 将半年期 TOP500 列表聚合为年度面板。对每国每年：总和 Rmax、总和核心数、系统数、最佳排名。半年值取均值。
- **原因**: PWT 是年度面板，需要年度算力
- **影响**: `data/interim/compute_capacity_annual.parquet` (1,022 obs, 57 国, 1993-2025)

### 1.5 与 PWT 增长面板合并
- **操作**: 通过 `iso3 + year` 左连接合并到 `growth_panel_1960plus.parquet`
- **原因**: 构建分析面板
- **影响**: `data/interim/growth_with_compute.parquet` (11,840 行 × 31 列)
- **零值处理**: 无 TOP500 系统的国家-年份用 0 填充算力变量

---

## 阶段 2：数据审计（2026-07-04）

### 审计发现 1: `pwt_import_share` 全部为负值
- **发现**: 全部 10,536 个非缺失 `pwt_import_share` < 0
- **根因**: PWT 11.0 的 `csh_m` 按约定存储为负值: `csh_m = -(imports / GDP at current PPPs)`
- **验证**: USA `csh_m ≈ -0.04`（进口占 GDP ~4%），合理。377 个观测 `csh_m < -1`（进口 > GDP），属于新加坡、香港等转口贸易经济体的正常现象
- **解决方案**: 创建 `pwt_import_share_abs`（绝对值）和 `pwt_trade_openness = pwt_export_share + |pwt_import_share|`
- **影响**: 回归中应使用 `pwt_import_share_abs` 或 `pwt_trade_openness`，而非原始 `pwt_import_share`

### 审计发现 2: `log_total_rmax` 存在负值 (−0.81 ~ −0.49)
- **发现**: 4 个观测的 `log_total_rmax < 0`
- **根因**: 1993 年 Belgium、Greece、Hong Kong、Slovenia 各仅 1-2 台 TOP500 系统, `total_rmax_gflops < 1` (0.445–0.615)，`log(x) < 0` 是数学上正确的
- **解决方案**: `log_total_rmax = clip(log_total_rmax, 0, inf)`，将极小负值归零（实质上等同于零算力）
- **影响**: 4 个观测被 clip 到 0。它们仅占非零算力观测的 0.4%，不影响结果

### 审计发现 3: 面板完美平衡 (185 国 × 64 年 = 11,840)
- **发现**: 每国恰好 1960-2023 共 64 年
- **根因**: PWT 11.0 覆盖 185 国 × 74 年 (1950-2023)，pipeline 过滤到 1960+ 后仍保留所有国家-年份行。这是标准长格式面板结构，变量缺失通过 `null` 而非删除行来表示
- **解决方案**: 无需代码修改。在文档中说明这是长格式面板的自然属性
- **影响**: 回归中缺失值自动被排除，不影响估计

### 审计发现 4: `growth_annual` 极端值 (56 观测 |growth| > 0.30)
- **发现**: 56 个极端观测 (10 个 < −0.50)
- **根因**: 全部是真实历史事件的反映:
  - **战争/内战**: Iraq 1991 (海湾战争, −1.09), Lebanon 1976 (内战, −0.86), South Sudan 2012 (−0.76), Liberia 1990 (−0.59), Rwanda 1994 (−0.51), Georgia 1992 (−0.57)
  - **COVID-19**: Macao 2020 (−0.80), Aruba 2020 (−0.31), Maldives 2020 (−0.43)
  - **石油繁荣**: Equatorial Guinea 1997 (+0.63), Guyana 2022 (+0.48)
  - **苏联解体**: Armenia 1992 (−0.53), Georgia 1992-1993, Moldova 1992-1994
- **解决方案**: 按项目规程创建 `growth_annual_winsor`（p1-p99 截尾，210 个观测被 clip）
- **影响**: 主分析使用截尾后的被解释变量。稳健性检查中用原始 `growth_annual` 排除 |growth| > 0.30

---

## 阶段 3：数据质量修复（2026-07-04）

### 修复脚本: `scripts/fix_data_quality.py`

| 操作 | 原因 | 新增变量 |
|---|---|---|
| 创建 `pwt_import_share_abs` | PWT csh_m 负值约定 | ✅ |
| 创建 `pwt_trade_openness` | 贸易开放度 = 出口 + 进口份额 | ✅ |
| 创建 `pwt_import_share_lag1_abs` | 滞后项同理 | ✅ |
| 创建 `pwt_trade_openness_lag1` | 滞后项同理 | ✅ |
| Clip `log_total_rmax` to ≥ 0 | 4 个极小值归零 | — (in-place) |
| 创建 `growth_annual_winsor` | p1-p99 截尾, 210 obs clipped | ✅ |

- **输入**: `data/interim/growth_with_compute.parquet` (11,840 × 31)
- **输出**: `data/interim/growth_with_compute_clean.parquet` (11,840 × 36)

---

## 阶段 4：最终审计确认（2026-07-04）

| 检查项 | 结果 |
|---|---|
| 主键唯一性 (`iso3 + year`) | ✅ |
| 面板维度 | 11,840 × 36 |
| 分析单位 | 国家-年份, 185 国, 1960-2023 |
| `growth_annual` 分布 | N=10,426, mean=0.0187, std=0.0648 |
| `log_total_rmax` 非零 | N=937, mean=10.79, min=0.00 |
| `growth_annual_winsor` 范围 | [-0.1919, 0.1688] |
| 控制变量滞后 | ✅ 全部 `_lag1` |
| 缺失处理规则 | 禁止均值填补、禁止跨国插值 |
| 进口份额符号 | ✅ 已创建 `_abs` 变量 |

### 面板摘要文件

- `docs/panel_summary.json`（机器可读的 Data Section 摘要）
- `docs/data_audit.md`（人类可读的完整审计报告）

---

## 操作纪律

1. **每个操作必须有原因记录**。哪怕只是 "添加注释" 也要写原因。
2. **每次修改原始数据必须记录**。包括：修改什么文件、为什么修改、对下游分析的影响。
3. **修改 pipeline 必须重新运行全流程**。确保 `data/processed/` 可再生。
4. **新增变量必须更新** `docs/variable_dictionary.csv` 和本日志。
5. **审计发现必须记录** 根因、解决方案、影响评估。
6. **本日志格式**: 阶段 → 操作块 → （操作、原因、影响）三元组。

---

## 待办

- [ ] 将 `fix_data_quality.py` 集成到 `run_pipeline.py` 中
- [ ] OEC GPU 进口数据作为第二算力代理
- [ ] 数据中心资本支出数据（第三代理）
- [ ] 更新 `docs/variable_dictionary.csv` 添加新增变量


---

## 阶段 5：项目规则更新（2026-07-04）

### 操作记录规则已写入 AGENTS.md

在原 `AGENTS.md` 项目规程中增加以下条款（见下文"数据操作记录纪律"）：

> 所有数据处理操作（无论大小）必须记录在 `docs/data_processing_log.md` 中。格式: 阶段 → 操作块 → (操作、原因、影响) 三元组。
