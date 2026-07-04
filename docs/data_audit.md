# Data Audit: growth_with_compute.parquet

**审计日期**: 2026-07-04  
**审计目的**: 供独立第三方学者复刻分析结果所需的全部数据信息  
**文件**: `data/interim/growth_with_compute.parquet` (1.14 MB)

---

## 1. 分析单位与主键

| 属性 | 值 |
|---|---|
| 分析单位 | 国家-年份 |
| 主键 | `iso3` + `year` |
| 主键唯一性 | ✅ 无重复 |
| 行数 | 11,840 |
| 列数 | 31 |

## 2. 时空覆盖

| 属性 | 值 |
|---|---|
| 时间范围 | 1960–2023 |
| 国家数 | 185 (全部有 ISO 3166-1 alpha-3 编码) |
| 国家名一致性 | ✅ 每个 ISO3 码恰好对应一个国名 |
| 面板平衡性 | 每国 64 年 × 185 国 = 11,840，完美平衡 |
| 分析样本标识 | `sample_flag_1960plus == True`：全部 11,840 行 |

> ⚠️ 面板平衡不意味着所有变量都完整。多国在 1960 年前无 GDP 数据（PWT 覆盖从实体独立年份开始）。`growth_annual` 等被解释变量仍有 11.9% 缺失。

## 3. 变量清单与缺失比例

| 变量 | 类型 | 非缺失 | 缺失 | 缺失% | Min | Max | 备注 |
|---|---|---|---|---|---|---|---|
| `iso3` | String | 11,840 | 0 | 0.0% | — | — | ISO3 码 |
| `country` | String | 11,840 | 0 | 0.0% | — | — | 国名 |
| `year` | Int32 | 11,840 | 0 | 0.0% | 1960 | 2023 | 年份 |
| `source_outcome` | String | 11,840 | 0 | 0.0% | — | — | 主结果来源标签 |
| `gdp_pc` | Float64 | 10,536 | 1,304 | 11.0% | 164.38 | 203,016.79 | PWT rgdpna/pop |
| `log_gdp_pc` | Float64 | 10,536 | 1,304 | 11.0% | 5.10 | 12.22 | ln(gdp_pc) |
| `growth_annual` | Float64 | 10,426 | 1,414 | 11.9% | −1.09 | 0.65 | **被解释变量** |
| `growth_5yr` | Float64 | 9,970 | 1,870 | 15.8% | −0.36 | 0.29 | 5年均值 |
| `growth_10yr` | Float64 | 9,351 | 2,489 | 21.0% | −0.19 | 0.21 | 10年均值 |
| `population` | Float64 | 10,536 | 1,304 | 11.0% | 4,420 | 1.44B | PWT pop |
| `sample_flag_1960plus` | Boolean | 11,840 | 0 | 0.0% | — | — | 全True |
| `maddison_gdp_pc` | Float64 | 9,840 | 2,000 | 16.9% | 377.58 | 160,051.24 | Maddison验证源 |
| `maddison_growth_annual` | Float64 | 9,809 | 2,031 | 17.2% | −0.95 | 0.72 | 验证源 |
| `maddison_growth_5yr` | Float64 | 9,744 | 2,096 | 17.7% | −0.40 | 0.31 | 验证源 |
| `maddison_growth_10yr` | Float64 | 9,666 | 2,174 | 18.4% | −0.22 | 0.24 | 验证源 |
| `pwt_human_capital_index` | Float64 | 8,574 | 3,266 | 27.6% | 1.01 | 3.99 | PWT hc |
| `pwt_tfp` | Float64 | 6,668 | 5,172 | 43.7% | 0.17 | 10.72 | PWT rtfpna |
| `pwt_investment_share` | Float64 | 10,536 | 1,304 | 11.0% | −0.10 | 96.72 | PWT csh_i |
| `pwt_export_share` | Float64 | 10,536 | 1,304 | 11.0% | 0.00 | 82.77 | PWT csh_x |
| `pwt_import_share` | Float64 | 10,536 | 1,304 | 11.0% | −1,167.04 | −0.00 | **PWT csh_m (负值约定)** |
| `pwt_human_capital_index_lag1` | Float64 | 8,429 | 3,411 | 28.8% | 1.01 | 3.94 | 滞后一期 |
| `pwt_tfp_lag1` | Float64 | 6,548 | 5,292 | 44.7% | 0.17 | 10.72 | 滞后一期 |
| `pwt_investment_share_lag1` | Float64 | 10,351 | 1,489 | 12.6% | −0.10 | 96.72 | 滞后一期 |
| `pwt_export_share_lag1` | Float64 | 10,351 | 1,489 | 12.6% | 0.00 | 82.77 | 滞后一期 |
| `pwt_import_share_lag1` | Float64 | 10,351 | 1,489 | 12.6% | −1,167.04 | −0.00 | 滞后一期 |
| `total_rmax_gflops` | Float64 | 11,840 | 0 | 0.0% | 0.00 | 3.06B | TOP500 国家总算力 |
| `total_rmax_pflops` | Float64 | 11,840 | 0 | 0.0% | 0.00 | 3,063.30 | 同上, PFlops |
| `log_total_rmax` | Float64 | 11,840 | 0 | 0.0% | −0.81 | 21.82 | **核心解释变量** |
| `n_top500_systems` | UInt32 | 11,840 | 0 | 0.0% | 0 | 608 | **核心解释变量** |
| `total_cores` | Float64 | 941 | 10,899 | 92.1% | 1 | 35,662,880 | 仅TOP500国家有值 |
| `best_rank` | Int32 | 941 | 10,899 | 92.1% | 1 | 500 | 仅TOP500国家有值 |

## 4. 核心变量分布

### 被解释变量: growth_annual

| 统计量 | 值 |
|---|---|
| N | 10,426 |
| Mean | 0.0187 |
| Std | 0.0648 |
| Min | −1.0929 (Iraq, 1991) |
| Max | 0.6462 |
| \|growth\| > 0.30 | 56 obs (33 国) |
| growth < −0.50 | 10 obs |

### 核心解释变量: log_total_rmax (非零值)

| 统计量 | 值 |
|---|---|
| N (非零) | 937 |
| Mean | 10.79 |
| Std | 5.04 |
| Min | 0.01 |
| P25 | 6.71 |
| P50 | 11.32 |
| P75 | 15.01 |
| Max | 21.82 |
| 零值观测 (无TOP500系统) | 10,903 |

## 5. 已知数据特性与审稿应对

### 5.1 PWT 进口份额符号约定

`pwt_import_share` (PWT 的 `csh_m`) 全部为负值。这是 PWT 的标准约定：`csh_m = −(M / GDP)`。在回归中取绝对值或使用 `csh_x + |csh_m|` 得到贸易开放度。

### 5.2 极端增长值

56 个观测 \|growth_annual\| > 0.30，集中在战乱/冲突国家 (Iraq, Lebanon, Liberia, South Sudan) 和石油小国 (Equatorial Guinea)。根据项目规程，应在稳健性检查中排除这些观测。

### 5.3 零算力观测的识别含义

10,903 个观测中 `log_total_rmax` 取零。这反映发展中国家无 TOP500 系统。在 FE 设定中，零变化国家不贡献 within-estimator 的识别。建议：① 主样本限制为至少有一次 TOP500 出现的 57 国；② 辅助分析保留全样本。

### 5.4 缺失模式

- `pwt_tfp` (43.7% 缺失) 和 `pwt_human_capital_index` (27.6% 缺失) 覆盖率较低。使用这些变量会显著减少回归样本。
- `total_cores` 和 `best_rank` 缺失 92.1%，仅对 TOP500 国家有值。这不是错误，是设计如此。

## 6. 数据溯源

| 来源 | 文件 | 版本 |
|---|---|---|
| Penn World Table | `data/raw/pwt/pwt110.xlsx` | 11.0 |
| Maddison Project | `data/raw/maddison/mpd2023_web.xlsx` | 2023 |
| TOP500 | `data/raw/top500/top500_xml_panel.parquet` | 1993–2025 (65 期) |
| WDI | `data/raw/wdi/*.json` | 当前 API 快照 |

**处理脚本**: `scripts/build_panels.py`  
**合并键**: `iso3 + year`（严格等值连接）  
**缺失处理规则**: 禁止均值填补、禁止跨国插值；仅有原始来源标记为估计值的允许前向填充  
**滞后规则**: 所有控制变量滞后一期（`{variable}_lag1`）

## 7. 复刻所需的最低信息

独立第三方学者复刻本面板需要：

1. 从 Dataverse 下载 PWT 11.0 (`doi:10.34894/FABVLR`) 和 Maddison 2023 (`doi:10.34894/INZBF2`)
2. 从 top500.org 下载各期 XML 文件（URL 模式：`https://top500.org/lists/top500/{year}/{month}/download/TOP500_{year}{month}_all.xml`）
3. 运行 `scripts/run_pipeline.py` 生成 `growth_panel_1960plus.parquet`
4. 运行 `scripts/merge_compute.py`（待添加）将 TOP500 数据合并到增长面板
5. 确认主键唯一、面板维度 (11,840 × 31)、变量缺失比例与本审计报告一致
