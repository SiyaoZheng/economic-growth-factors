# Research Starter Packet: AI 算力与经济增长

**生成日期**: 2026-07-04
**下游路由**: `research-data-builder` → 算力数据可行性报告 → pipeline 接入

---

## Research Question（暂定）

**人工智能算力基础设施的扩张是否促进了国家经济增长？若是，通过"自动化替代"还是"新任务创造"渠道？**

理论锚点：任务型模型（Acemoglu & Restrepo 2018, 2019）。AI 是一种通用技术（GPT），可以替代部分工作任务（自动化渠道），同时也能创造出劳动具有比较优势的新任务（新任务/恢复渠道）。**算力是 AI 能力的操作化代理变量**，国家间算力差异反映 AI 采用强度的差异。

---

## Materials Inventory

### 可使用材料

| 材料 | 状态 |
|---|---|
| PWT 11.0 增长面板 (1960-2023, 185国) | ✅ pipeline已完成 |
| WDI 控制变量（贸易、投资、产业份额、城镇化、预期寿命） | ✅ pipeline已完成 |
| Maddison 验证来源 | ✅ pipeline已完成 |
| 项目 pipeline (`scripts/run_pipeline.py`) | ✅ 可重用 |

### 待获取材料

| 材料 | 用途 | 获取难度 |
|---|---|---|
| TOP500 超算排名 (top500.org) | 国家算力：`log_sum_rmax`、核心数、系统数 | 低：公开 JSON/CSV |
| OEC / COMTRADE 海关 HS 8471/8473 | 商业算力进口流量 | 中：OEC API 有速率限制 |
| Statista / 数据中心资本支出 | 数据中心投资代理 | 高：付费（探索公开替代） |

---

## 自动化 vs 新任务渠道的操作化

任务型模型的两个渠道不可直接观测，本研究的操作化策略如下：

### 理论逻辑

| 渠道 | 机制 | 对增长的预期净效应 |
|---|---|---|
| **自动化渠道** | AI 替代 routine/cognitive 任务 → 劳动份额下降、资本回报上升 | 短期正（资本深化）、长期取决于新任务补偿速度 |
| **新任务渠道** | AI 创造劳动具有比较优势的新任务 → 恢复劳动需求、扩大生产可能性边界 | 正（TFP 提升 + 劳动需求恢复） |

### 跨国面板上的代理变量

现有 pipeline 中已有以下变量可用于渠道代理：

| 变量 | 已有？ | 代理的渠道 | 逻辑 |
|---|---|---|---|
| `wdi_industry_value_added_gdp_lag1` | ✅ | **自动化暴露度** | 制造业/工业 routine 任务密度高，AI 替代弹性大 |
| `pwt_human_capital_index_lag1` | ✅ | **新任务暴露度** | 高人力资本 = 更高技能劳动力 = 更易创造和吸收新任务 |
| `wdi_services_value_added_gdp_lag1` | ✅ | **新任务暴露度** | ICT/知识密集型服务业是新任务的集中领域 |

### 回归设定（渠道分解）

主回归：

```
growth_annual = β₁·compute_capacity_lag1
              + β₂·compute_capacity_lag1 × automation_exposure_lag1
              + β₃·compute_capacity_lag1 × newtask_exposure_lag1
              + γ·controls_lag1 + country_FE + year_FE + ε
```

- `automation_exposure` = `wdi_industry_value_added_gdp`（制造业增加值占 GDP 比重）
- `newtask_exposure` = `pwt_human_capital_index` 或 `wdi_services_value_added_gdp`
- 关键诊断：**β₂（自动化）vs β₃（新任务）的相对大小和符号**。如果 β₃ > β₂，说明新任务渠道主导；如果 β₂ 为负，说明自动化渠道对增长的净效应可能为负。

### 边界条件（不声称的）

- 不声称渠道代理变量精确测量了任务层面的机制（那是微观数据的任务）
- 不声称交互项系数的因果解释（交互项在 FE 设定下仍然面临内生性）
- 渠道分解仅作为异质性分析的模式识别，而非因果中介

---

## Route Cards

三条候选路线，R1 为首选。

### R1（首选）：AI 算力与增长——跨国面板 + 渠道异质性

| 维度 | 内容 |
|---|---|
| 研究问题 | AI 算力扩张是否促进增长？自动化 vs 新任务渠道哪个主导？ |
| 研究类型 | 因果识别（先做 FE 关联，后找外生冲击） |
| 分析单位 | 国家-年份，2015-2023 |
| 被解释变量 | `growth_annual` / `growth_5yr` |
| 核心解释变量 | `compute_capacity`（三个来源：TOP500 / OEC GPU / 数据中心投资） |
| 渠道变量 | `wdi_industry_value_added_gdp`（自动化）、`pwt_human_capital_index`（新任务） |
| 识别策略 | 双向 FE + 国家聚类 SE；后续寻找外生冲击做 DID |
| 三步走 | ① 算力数据可行性 → ② 主效应 → ③ 渠道交互项 |
| **first_action** | 爬取 TOP500 + 检查 OEC GPU 覆盖 → 算力数据可行性报告 |
| **failure_signal** | 三源合并覆盖 < 40 国且集中在 OECD |
| **feasibility_status** | `try_now` |

### R2：AI 任务暴露度与增长——职业结构渠道

| 维度 | 内容 |
|---|---|
| 研究问题 | AI 职业暴露度 × 国家职业结构是否解释增长差异？ |
| 核心解释变量 | Felten AIOE Bartik instrument |
| **first_action** | 下载 Felten AIOE + ILO 就业样本 |
| **failure_signal** | ILO 发展中国家 < 60 国 |
| **feasibility_status** | `needs_material` |

### R3：AI 投资与行业 TFP——渠道分解

| 维度 | 内容 |
|---|---|
| 研究问题 | 算力是否通过特定行业 TFP 促进总体增长？ |
| 分析单位 | 国家-行业-年份 |
| 核心解释变量 | 国家算力 × 行业 AI 暴露度 |
| **first_action** | 检查 EU KLEMS/PWT 行业 TFP 覆盖 |
| **failure_signal** | 覆盖 < 30 国或 2019 年后无数据 |
| **feasibility_status** | `needs_material` |

详见 `docs/research_route_cards.csv`。

---

## Minimum Viable Study

**R1 三步走的第一步：算力数据可行性报告。**

产出：
- TOP500 历年国家总算力趋势
- OEC GPU 进口国家-年份覆盖矩阵
- 两个来源交叉覆盖
- 与 PWT 增长面板 merge 后的 sample loss

MVS 不声称：
- 不声称因果效应
- 不声称渠道分解结果
- 不声称识别策略有效性

---

## Stop Reason

在算力数据源的存在性和覆盖面确认之前，不能进入回归模型构建。这是数据先行，不是设计不足。

---

## Researcher Decision Needed

1. ✅ 算力代理变量：三个都做（已确认）
2. ✅ 时间边界：2015 年起（已确认）
3. ✅ 中国包含在样本中（已确认）
4. 🔴 渠道分解的代理变量是否接受现行方案？（`wdi_industry_value_added_gdp` + `pwt_human_capital_index`）
5. 🔴 如果算力三源合并后覆盖国家不足 40，是否接受仅以 OECD 或中高收入国家为样本？还是退回描述性研究？

---

## Handoff Prompt

```text
使用 $research-data-builder，路由 R1。

目标：从 TOP500 超算数据库和 OEC 海关数据构建 AI 算力国家-年份面板。

第一步行动：
1. 从 top500.org 爬取历年 TOP500 列表，提取每个系统的国家、年份、Rmax (TFlop/s)、核心数
2. 在国家-年份层面聚合：log_sum_rmax、系统数（extensive margin）、平均每系统算力（intensive margin）
3. 检查 OEC API (HS 8471/8473) 获取国家-年份 GPU/计算设备进口额
4. 探索公开数据中心资本支出数据
5. 生成算力数据可行性报告：覆盖国家数、年份范围、缺失模式、与 PWT 增长面板 merge 后的 sample loss
6. 优先 TOP500，因为数据最易获取

输出：`docs/compute_capacity_feasibility.md`
下游文件：`data/interim/compute_capacity_panel.parquet`

不要构建回归模型。不要声称因果关系。
如果算力三源合并后覆盖 < 40 国，报告作为 stop reason。
```

---

## Next Skill Route

`research-data-builder` → 算力数据可行性报告
