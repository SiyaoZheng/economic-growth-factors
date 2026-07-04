---
title: Cover Letter — AI算力扩张与经济增长：跨国面板证据
date: 2026-07-04
boundary: author-facing draft scaffold — final prose must be reviewed and adjusted by the author
---

# Cover Letter 段落骨架

以下是 cover letter 的段落骨架。每段标注了 **purpose**（目的）、**evidence**（使用的证据）、**claim slot**（需要作者填充的声称位置）、**risks**（风险）。按照 academic-writing-scaffold 的边界：不写成文段落，提供骨架供 Adrian 自己写。

---

## 段落1: 投稿说明

| 维度 | 内容 |
|---|---|
| **purpose** | 向编辑说明投稿目标，声明论文未一稿多投、全体作者知情同意 |
| **evidence** | —（投稿程序说明，无需 evidence） |
| **claim_slot** | ① 论文标题；② 投稿期刊名称（目标:《管理世界》级别）；③ 全部作者已阅读并同意投稿；④ 未一稿多投声明 |
| **template_suggestion** | "尊敬的编辑：我们郑重向贵刊投稿《论文标题》。本文从未投往其他刊物，所有作者已阅读并同意投稿。" |
| **risks** | 标题需要最终确认（目前代码与报告中使用 'AI算力扩张与经济增长：跨国面板证据'）；作者名单需确认 |

---

## 段落2: 研究动机——为什么这个问题重要？

| 维度 | 内容 |
|---|---|
| **purpose** | 在 2-3 句话内回答：① 世界发生了什么变化？② 为什么经济学家需要回答这个问题？③ 现有文献缺什么？ |
| **evidence** | `synth_001` (AI as GPT)；`synth_005` (测量 gap: 现有文献只用专利)；`LF14` (0 篇已发表研究使用算力测量 AI) |
| **claim_slot** | "自 2015 年以来，全球超算算力增长了 15.7 倍（TOP500 数据），AI 被普遍预期为一种通用目的技术（GPT）。然而，现有跨国实证文献全部依赖 AI 专利或职业暴露度作为 AI 能力的代理，尚无研究直接使用算力基础设施数据来检验 AI 与经济增长的关系。" |
| **evidence_support** | 算力增长倍数来自 `compute_capacity_feasibility.md`（391→6137 PFlops, 2015-2023）；GPT 定位来自 Brynjolfsson 2017 + Acemoglu 2025；测量 gap 在 literature matrix 中确认 |
| **risks** | ① 不要把 'AI 是 GPT' 说成定论——审稿人会觉得过度声称；② 15.7 倍是全球总算力，不代表 AI 专用算力；③ 不要用 'transformative'/'revolutionary' 等浮夸形容词；④ 管理世界偏好问题导向的开头——可以用发展中国家的数据基础设施差距作为叙事钩子 |
| **author_decision** | 是否把发展中国家的算力鸿沟作为开头钩子？（本研究的核心关切之一是：141/185 国零算力） |

---

## 段落3: 研究问题与主要发现

| 维度 | 内容 |
|---|---|
| **purpose** | 一句话说清研究问题 + 一句话给出核心结果 |
| **evidence** | `E1`: log_rmax coef = −0.062, SE = 0.033, p = 0.066；`E2`: 系数跨 4 个嵌套模型稳定（−0.077 → −0.062）；`E3`: placebo test p = 0.001 |
| **claim_slot** | "我们的核心问题是：国家层面的算力扩张是否促进了经济增长？利用 2015-2023 年 120 国面板数据，我们发现 log(总算力) 与年度 GDP 增长率之间呈负向关联（β = −0.062, SE = 0.033, p = 0.066），且该关联在加入控制变量后保持稳定。安慰剂置换检验拒绝零效应（p = 0.001）。" |
| **evidence_support** | 系数来自 DID diagnostics report (full controls column)；稳定性来自 coef_stability；安慰剂来自 placebo_continuous |
| **risks** | ① 这个 '核心结果' 是**负向关联**——这是文章最可能需要解释的地方。Cover letter 中不应回避，但也不应让编辑觉得 '文章没有发现正效应所以无贡献'；② p = 0.066 在 0.05 边缘——不要说 'statistically significant'（严格不等于 significant at 5%）；③ 负号的解释边界必须在信中或正文中说明（内生性？Brynjolfsson productivity paradox？发展中国家零算力拖累？） |
| **author_decision** | 如何在 cover letter 中框定这个负向结果？选项：(a) 如实证中呈现——直接报告为关联性证据；(b) 强调这不是一个 'AI 伤害增长' 的结论——它是测量、内生性、样本构成共同作用的结果；(c) 将负号框定为 'first empirical documentation of a puzzle'——即 '为什么算力增长与经济增长没有正相关？' |

---

## 段落4: 数据与识别策略

| 维度 | 内容 |
|---|---|
| **purpose** | 让编辑信任数据质量和识别策略的严谨性 |
| **evidence** | `DF1-D10`（panel_summary.json）；`synth_005`（TOP500 作为 AI 能力代理的论证）；`DF5`（TWFE + 国家聚类 SE）|
| **claim_slot** | "我们构建了 1960-2023 年 185 国跨国-年份面板，合并了 PWT 11.0 增长数据、TOP500 超算数据（1993-2025, 65 期）、和 Maddison 交叉验证来源。算力变量为 log(一国总算力, GFlops)，控制变量全部滞后一期，所有回归包含国家固定效应和年份固定效应，标准误在国家层面聚类。" |
| **evidence_support** | 面板维度来自 panel_summary.json；TOP500 数据获取和聚合在 compute_capacity_feasibility.md 中详述；滞后和聚类来自 AGENTS.md 1.1 和 1.2 节 |
| **risks** | ① 不要过度强调 'AI 算力'——TOP500 是通用超算，这是 reviewer R1 已指出的问题；② 不要只说 '控制了国家 FE' 而不提内生性——cover letter 应诚实地说明这是关联性证据而非因果识别；③ 如果现在没有 QoG/V-Dem 数据（还在计划中），不要说 '控制了制度质量' |
| **author_decision** | 如何称呼算力变量？① 'AI 算力 (TOP500 proxy)' 还是 ② '算力基础设施 (TOP500 代理)'？前者声称更强，后者更安全 |

---

## 段落5: 稳健性——为什么这个结果不是巧合？

| 维度 | 内容 |
|---|---|
| **purpose** | 展示信号不是数据挖掘的产物——增加编辑对结果可信度的判断 |
| **evidence** | `E2`: 系数稳定性（4 nested models: −0.077 → −0.062）；`E3`: 安慰剂 p = 0.001；table1_main_effect: 排除中国后人力资本系数 −2.401***（稳健）；排除 OECD 后系数 −2.659**（稳健）；排除极端值后 −2.227**（稳健）；DID diagnostics: pre-trend flat（虽弱统计功效）；coef stability plot |
| **claim_slot** | "我们对核心结果进行了多项稳健性检验：(1) 控制变量逐步加入 4 个嵌套模型，算力系数保持稳定（−0.077 到 −0.062）；(2) 2000 次随机置换检验拒绝零效应（p = 0.001）；(3) 排除中国、排除高收入 OECD 国家、排除极端增长观测后，主要结论不变。" |
| **evidence_support** | 稳定性来自 coef_stability 诊断；安慰剂来自 placebo_continuous；稳健性检查来自 table1_main_effect（columns 2-4） |
| **risks** | ① 目前稳健性通过 table1（传统增长控制变量表）体现，而非算力变量的专用稳健性；② table2 的交互项不显著——不要在 cover letter 中声称 '渠道被识别'；③ pre-trends 统计功效弱——不要说过度自信于 parallel trends |
| **author_decision** | 是否需要再跑一组算力变量的专用稳健性？（如：仅 44 国有算力国家、5 年窗口增长、Maddison 来源替代）如果目前没有，cover letter 应注明 '稳健性基于传统增长控制变量框架' |

---

## 段落6: 本研究在文献中的贡献定位

| 维度 | 内容 |
|---|---|
| **purpose** | 向编辑解释为什么这篇文章应该发表在目标期刊——即贡献是什么 |
| **evidence** | `LF14`（无文献使用算力→增长）；`synth_005`（测量创新: 专利 → 算力）；`LF15`（发展中国家证据空白）；literature matrix 确认 gap；中文视角: 谢伟丽 2025（工业技术经济）和蔡跃洲 2019（数量经济技术经济研究）是仅有的相关中文研究 |
| **claim_slot** | "本文的贡献有三：(1) 首次将TOP500超算数据作为AI能力的跨国代理，突破了现有文献仅依赖AI专利的测量惯习；(2) 首次在跨国面板层面检验算力基础设施与经济增长的关联，尤其在141个发展中国家零算力的背景下提供了新的实证事实；(3) 对Acemoglu-Restrepo任务模型的两个渠道（自动化替代 vs 新任务创造）进行了异质性分析的初步探索（交互项模式识别，非因果渠道检验）。" |
| **evidence_support** | 测量 gap 确证于 literature matrix 和 literature_theory_synthesis.csv；发展中国家 gap 确证于 literature_open_questions；渠道分析来自 table2 但交互项不显著——贡献声索需降级 |
| **risks** | ① '首次' 声称需要在该领域的文献搜索中确证——目前 literature matrix 中 22 篇已确证无算力研究，但仍有可能遗漏发表中的 working paper；② 贡献 3 需要降级：交互项不显著（β_automation=−0.006, SE=0.010; β_newtask=−0.005, SE=0.007），不要声称找到了渠道效应；③ 不要用过度营销的语言——管理世界审稿人反感 '填补空白' 式贡献声索 |
| **author_decision** | 贡献声索优先顺序？可选组合：(a) 测量创新为首要贡献；(b) 实证事实（尤其是在发展中经济体的发现）为首要贡献；(c) 理论对话（回应 Acemoglu 0.53% 预期）为首要贡献？这个顺序决定了 cover letter 的 narrative 结构 |

---

# Claim Ledger — Cover Letter

以下是 cover letter 中每个声称对应的证据和风险审计。

| claim_id | claim_text_or_slot | claim_type | evidence_path | support_level | risk | author_boundary |
|---|---|---|---|---|---|---|
| CC-1 | 全球算力 2015-2023 增长 15.7 倍 | design_fact | compute_capacity_feasibility.md | strong | 这是总算力不是AI专用算力 | scaffold_only |
| CC-2 | 无已发表研究使用TOP500算力作为AI能力代理 | literature_fact | literature_matrix.csv (22篇确证); LF14 | strong | 可能存在遗漏的working paper | scaffold_only |
| CC-3 | log_rmax → growth_annual: β=−0.062, SE=0.033, p=0.066 | estimate | DID diagnostics report | partial | TWFE不建立因果; p>0.05 | scaffold_only |
| CC-4 | 系数跨4个模型稳定(−0.077→−0.062) | diagnostic | coef_stability plot | strong | — | scaffold_only |
| CC-5 | Placebo test p=0.001 | diagnostic | placebo_continuous | strong | 排除零效应但不排除内生性 | scaffold_only |
| CC-6 | 算力是比专利更直接的AI基础设施测量 | interpretation | synth_005; LF14 | partial | TOP500捕捉通用超算;需作者决定声称边界 | needs_author_decision |
| CC-7 | 首次在跨国面板中检验算力→增长 | contribution | literature_matrix; LF14; LF15 | partial | '首次'声称需作者自行确证 | needs_author_decision |
| CC-8 | 自动化 vs 新任务渠道异质性分析 | interpretation | table2_channel.html; synth_002+003 | weak | 交互项不显著;代理变量间接 | needs_author_decision |
| CC-9 | 发展中国家算力鸿沟: 141/185国零算力 | design_fact | panel_summary.json; synth_007 | strong | — | scaffold_only |
| CC-10 | 排除中国/OECD/极端值后结果稳健 | diagnostic | table1_main_effect.html (col 2-4) | strong | 这是传统增长变量表的稳健性,非算力变量专用 | scaffold_only |
| CC-11 | 面板含国家+年份FE, SE在国家层聚类 | design_fact | AGENTS.md 1.1; panel_summary.json | strong | — | scaffold_only |
| CC-12 | 控制变量全部滞后一期 | design_fact | AGENTS.md 1.1 | strong | — | scaffold_only |

---

# Author Decisions — 必须先决定再写 cover letter

以下是 Adrian 需要在**写 cover letter 终稿前**决定的 6 个 blocking 问题：

## Blocking decisions

### B1. 算力变量的声称边界
- 选项 A: "AI算力（TOP500代理）" — 声称更强，管理世界关注度更高，但审稿人会质疑（TOP500包含非AI超算）
- 选项 B: "算力基础设施（TOP500数据）" — 更安全，但缺乏AI标签可能降低选题吸引力
- 选项 C: "以TOP500超算度量的算力能力" — 中立措辞

### B2. 负向结果的 narrative 框架
- 选项 A: 如实报告为关联性证据——不声称因果，不解释负号（最安全）
- 选项 B: 框定为"第一个记录此关联的实证研究"——负号本身是发现而非缺陷
- 选项 C: 强调稳健性和plausible机制——承认内生性但展示结果不是巧合

### B3. 贡献声索的优先顺序
- 选项 A: 测量创新为首位（首次用算力替代专利）
- 选项 B: 实证事实为首位（发现→报告→解释负向关联）
- 选项 C: 理论对话为首位（回应Acemoglu-Restrepo的任务模型——回应Acemoglu 0.53%）

### B4. 投稿期刊名称
- 需要确认明确的目标期刊（"管理世界"/"经济研究"/其他）

### B5. 作者名单
- 需要确认全部作者姓名和单位

### B6. 论文标题
- 当前项目中使用的是"AI算力扩张与经济增长：跨国面板证据"，需要确认这是最终标题

---

# 建议的 Cover Letter 中文结构

如果 Adrian 偏好中文 cover letter，建议按以下结构组织（管理世界投稿信风格）：

1. **投稿声明**（一句话：投稿 + 未一稿多投 + 作者知情同意）
2. **问题重要性**（2-3句：全球算力扩张 → 增长影响未知 → 文献缺口）
3. **研究设计与主要发现**（3-4句：185国面板 + TOP500 + TWFE → 负向关联 → 稳健性）
4. **贡献**（2-3句：测量创新 + 跨国实证 + 理论对话）
5. **研究设计与数据严谨性**（2-3句：面板构建 + FE + 聚类 + 滞后 + 无填补/插值）
6. **结尾**（1-2句：期待审阅 + 联系方式）
