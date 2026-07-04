# Evidence Inventory: AI 算力与经济增长

Generated: 2026-07-04 | Skill: academic-writing-scaffold | Boundary: scaffold only — author writes final prose

---

## 1. Design Facts

| # | fact | evidence_path | status |
|---|---:|---|---|
| DF1 | 面板单位: 国家-年份 (iso3 + year) | `scripts/build_panels.py; docs/panel_summary.json` | ✅ verified |
| DF2 | 被解释变量: growth_annual (PWT 11.0 log GDP per capita growth) | `data/processed/growth_panel_1960plus.parquet` | ✅ verified |
| DF3 | 核心解释变量: log_total_rmax (TOP500 超算总 Rmax, TFlop/s 对数) | `data/processed/growth_panel_1960plus.parquet` | ✅ verified |
| DF4 | 样本边界: year >= 1960; 滞后缓冲 1950+ | `scripts/build_panels.py; LAG_BUFFER_START_YEAR=1950` | ✅ verified |
| DF5 | 识别策略: 双向固定效应 (country FE + year FE) + 国家聚类 SE | `scripts/run_did_diagnostics.R` | ✅ verified |
| DF6 | 面板维度: 185 国, 1960-2023; 实际分析样本 120 国 × 2015-2023 (complete cases) | `reports/did_diagnostics_report.html` | ✅ verified |
| DF7 | TOP500 覆盖: 44 国曾出现; 141 国零算力 (log_total_rmax = 0) | `data/processed/growth_panel_1960plus.parquet` | ✅ verified |
| DF8 | 控制变量全部滞后一期 (lag1) | `scripts/build_panels.py` | ✅ verified |
| DF9 | 无均值填补, 无跨国插值 | `scripts/build_panels.py; docs/variable_dictionary.csv` | ✅ verified |
| DF10 | growth_annual 在 p1/p99 缩尾处理 (210 obs) | `docs/panel_summary.json` | ✅ verified |

## 2. Core Empirical Estimates

| # | estimate | evidence_path | support_level | interpretation_boundary |
|---|---:|---|---|---|
| E1 | log_total_rmax → growth_annual: β = −0.062 (SE = 0.033, p = 0.066) | `reports/did_diagnostics_report.html, Full controls column` | partial | TWFE 不确立因果; 负号可能与反向因果或样本构成有关 |
| E2 | 系数跨模型稳健: −0.077 (bare FE) → −0.062 (full controls) | `reports/did_diagnostics_report.html, Coefficient stability` | strong | 方向始终为负, 加入控制变量不消除 |
| E3 | Placebo test: p = 0.001 (2000 permutations) | `reports/did_diagnostics/placebo_continuous.png` | strong | 零效应可被拒绝; 但不能排除内生性 |
| E4 | 出口份额 (pwt_export_share): β = −12.82 (SE = 4.85, p < 0.01) | `reports/did_diagnostics_report.html` | partial | 贸易结构可能与算力共线 |
| E5 | TFP: β = −14.48 (SE = 2.24, p < 0.001) | `reports/did_diagnostics_report.html` | partial | TFP 与算力可能同时被增长内生决定 |
| E6 | DID 设计: 非清洁 staggered (35/44 always-treated) | `reports/did_diagnostics_report.html` | weak | 二元 DID 不可行; 连续处理型 TWFE 为主要策略 |

## 3. Literature Facts (from verified primary sources)

| # | fact | source | verification |
|---|---:|---|---|
| LF1 | Acemoglu & Restrepo (2019): 自动化替代劳动, 新任务恢复劳动需求; 长期增长取决于两者竞赛 | JEP 33.2.3 | verified_primary | abstract only |
| LF2 | Acemoglu & Restrepo (2018, AER): 校准模型显示技术可降低劳动份额和就业, 除非新任务创造足够快 | AER 2018 | verified_primary | abstract only |
| LF3 | Acemoglu (2025): AI 将使 TFP 在 10 年内提高 ~0.53% — 宏观效应微小 | Economic Policy 2025 / NBER WP 32487 | verified_primary | abstract only |
| LF4 | Gonzales (2023): AI 专利对增长效应为正但量级小; 在发达经济体更稳健 | J. Econ. Struct. 2023 | needs_primary_source | abstract from Google Scholar |
| LF5 | Damioli et al. (2021): AI 专利对劳动生产率有正向效应 (513 citations) | Eurasian Bus. Rev. 2021 | needs_primary_source | abstract from Google Scholar |
| LF6 | Georgieff & Hyee (2022): AI 就业效应跨国证据 (223 citations) | Frontiers in AI 2022 | needs_primary_source | abstract from Google Scholar |
| LF7 | Restrepo (2024): 自动化综述 — 自动化减少就业和劳动份额, 但效应被新任务部分抵消 | NBER WP 2024 | verified_primary | abstract only |
| LF8 | Acemoglu et al. (2020): 法国企业级机器人采用 → 劳动份额下降, 竞争对手就业损失 | AEA P&P 2020 | verified_primary | abstract only |
| LF9 | Acemoglu & Restrepo (2018, JHC): 低技能自动化增加不平等; 高技能自动化减少不平等 | J. Human Capital 2018 | verified_primary | abstract only |
| LF10 | Verschuere & Cameron (2026): 18 经济体 post-ChatGPT, AI 生产率效应跨行业估计 | SSRN WP 2026 | needs_primary_source | abstract |
| LF11 | Nguyen (2026): staggered DID, 国家 AI 战略 → 宏观表现 | SSRN WP 2026 | needs_primary_source | abstract |
| LF12 | Filippucci et al. (2024): OECD 政策报告, 直接回应 Acemoglu (2025) 的 AI 宏观效应估计 | OECD 2024 | needs_primary_source | abstract |
| LF13 | Drago et al. (2025): ML + panel, AI 采用的宏观驱动因素 (欧洲) | Economies (MDPI) 2025 | needs_primary_source | abstract |
| LF14 | 现有文献全部使用 AI 专利或职业暴露度作为 AI 代理; 无任何已发表研究使用 TOP500 或算力基础设施测量 AI | docs/literature_theory_synthesis.csv, synth_005 | verified — gap confirmed by literature matrix |
| LF15 | AI 增长效应在发展中国家的证据稀少; 绝大多数研究聚焦 OECD/G20/EU | docs/literature_open_questions.md | verified — gap confirmed |

## 4. Interpretations (from theory synthesis — NOT author-approved)

| # | interpretation | synthesis_id | evidence basis | boundary |
|---|---:|---|---|---|
| I1 | AI 是一种通用目的技术 (GPT), 其增长效应通过资本深化、TFP 提升和劳动力替代三条路径传导 | `synth_001` | Brynjolfsson 2017; Acemoglu 2025; Gonzales 2023; Damioli 2021 | GPT 的实证增长效应量级仍存重大争议 |
| I2 | 自动化渠道: AI 算力替代 routine/cognitive 任务 → 劳动份额下降、短期资本回报上升 | `synth_002` | Acemoglu-Restrepo 核心框架 (4 篇 verified) | 工业增加值/GDP 是否为合理代理需作者裁决 |
| I3 | 新任务渠道: AI 创造劳动有比较优势的新任务 → 恢复劳动需求、TFP 提升 | `synth_003` | Acemoglu-Restrepo new-task theory (3 篇 verified) | 人力资本指数 ≠ 新任务创造; 是本研究最薄弱的操作化 |
| I4 | AI 增长效应在发达经济体更强; 发展中国家面临数据/技能/制度三重约束 | `synth_004` | Gonzales 2023; Damioli 2021; Georgieff 2022 | 如果非 OECD 子样本效应不显著, 需决定叙事方向 |
| I5 | TOP500 算力是 AI 能力的更直接投入测量 (vs 专利/暴露度) | `synth_005` | 文献矩阵 + 零算力→增长实证 gap | TOP500 包含非 AI 超算; 需作者决定是否声称'AI 算力' |
| I6 | 反向因果威胁: GDP↑ → 算力投资↑, 而非算力 → 增长 | `synth_006` | Drago 2025; Brynjolfsson 2017 productivity paradox | 当前 TWFE 仅缓解时不变混淆; 需 IV/DID |
| I7 | 零算力国家 (141/185) 的算力效应识别依赖有-无对比, 而非算力强度 | `synth_007` | panel_summary.json | log_total_rmax N_nonzero=937 | 主分析是否限制在 44 国有 TOP500 存在的国家? |

## 5. Key Uncertainties (unresolved author decisions)

1. **算力测量的外部有效性 (scope_003):** TOP500 捕捉通用超算, 非 AI 专用. 我们声称'AI 能力代理' 是否合理?
2. **零算力国家的处理 (synth_007):** 主分析限 44 国还是含 141 零算力国家?
3. **渠道代理变量 (synth_003):** 接受 wdi_industry_value_added_gdp 和 pwt_human_capital_index?
4. **内生性策略 (synth_006):** 是否找外生冲击做 IV/DID? 候选: submarine cables, cloud regions, 历史 CS 院系数
5. **中文文献定位:** 仅 2 篇候选; 需在管理世界/经济研究层面补充搜索?
6. **AI 专利交叉验证 (synth_005):** 是否补充 AI 专利数据做代理变量对比?