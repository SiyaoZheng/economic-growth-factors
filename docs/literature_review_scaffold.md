# Literature Review Scaffold: AI 算力与经济增长

Generated: 2026-07-04 | Skill: academic-writing-scaffold

**Hard boundary:** This is an author-facing scaffold. Do NOT fill with final prose.
The author writes every paragraph in their own voice with their own judgment.

---

## Section Architecture: Debate-Cluster Structure

按争论群组织, 非按论文列表. 论文 = evidence slots within each cluster.

---

### Cluster 1: AI 是一种真正的通用目的技术 (GPT) 吗？

| element | content |
|---|---|
| **cluster_claim** | AI 是一种 GPT，其增长效应通过资本深化、TFP 提升、劳动力替代三条路径传导 |
| **supporting_papers** | Brynjolfsson et al. (2017, NBER) — GPT 框架; Acemoglu (2025, Economic Policy) — AI 宏观校准 0.53% TFP; Gonzales (2023) — 跨国 AI 专利→增长; Damioli et al. (2021) — AI 专利→劳动生产率 |
| **what_cluster_identifies_well** | AI 作为 GPT 的理论共识几乎完整; 实证方向(正向)在多个独立来源中一致 |
| **what_remains_unresolved** | 量级争议巨大: Acemoglu 0.53% vs 产业界预期 >1% vs Filippucci et al. (2024, OECD) 的中间估计. 'GPT' 标签本身是否过度承诺? (rival_003: AI 可能只是普通自动化浪潮) |
| **how_project_enters** | 使用算力(TOP500)而非专利作为 AI 能力的操作化—直接测量基础设施投入而非创新产出. 检验算力→增长的效应量级是否 > Acemoglu 0.53% 的专利估计 |
| **citation_gaps** | Brynjolfsson GPT 原文献的完整提取; Gonzales (2023) 全文而非 abstract; Damioli (2021) 效应量级的具体数字 |
| **risk** | 不要声称'AI 是 GPT 已成定论'—这在审稿人看来是证据不足的过度声称 |
| **author_decision** | 本研究在 GPT 框架中的定位: (a) 算力是 GPT 基础设施, (b) 还是保守地称之为'技术能力代理'？ Acemoglu 的 0.53% 是否需要作为本研究的基准预期? |

---

### Cluster 2: 自动化替代 vs 新任务创造 — 渠道之争

| element | content |
|---|---|
| **cluster_claim** | AI 对增长的净效应取决于自动化替代(劳动份额下降)和新任务创造(劳动需求恢复)的相对速度 |
| **supporting_papers** | Acemoglu & Restrepo (2019, JEP) — 任务模型框架; Acemoglu & Restrepo (2018, AER) — 竞赛模型校准; Restrepo (2024, NBER) — 自动化综述; Acemoglu et al. (2020, AEA P&P) — 法国企业机器人证据 |
| **what_cluster_identifies_well** | 理论框架成熟: actor → action → mediating condition → outcome 的因果链清晰. 微观证据(法国企业)支持替代效应 |
| **what_remains_unresolved** | 跨国面板上的渠道分解无实证先例. 竞争对手(synth_006: 反向因果)和替代解释(rival_001: SBTC vs task-replacement)未决. Acemoglu 框架聚焦劳动份额, 但本研究聚焦 GDP 增长 |
| **how_project_enters** | 用交互项进行渠道异质性分析: log_total_rmax × industry_share (自动化暴露度) vs log_total_rmax × human_capital (新任务暴露度). 注意: 我们声称的是'异质性模式识别'而非'因果渠道检验' |
| **citation_gaps** | Restrepo (2024, NBER) 的完整检索; Acemoglu & Restrepo (2018, AER) 的具体校准参数; 需要中文自动化研究(如蔡跃洲 2019)的完整提取 |
| **risk** | 不要把交互项写成'渠道检验'—审稿人会指出交互项在 FE 下不是因果渠道. 不要说'人力资本' 精确测量'新任务创造' |
| **author_decision** | 接受工业份额 + 人力资本的代理策略吗? 新任务渠道若无更好的操作化, 是否降级为'探索性分析'? SBTC 替代解释(rival_001)值得在文中讨论吗? |

---

### Cluster 3: AI 增长效应的边界条件 — 谁受益？

| element | content |
|---|---|
| **cluster_claim** | AI 的增长效应在发达经济体更强; 发展中国家面临数据基础设施不足、技能短缺、制度薄弱三重约束 |
| **supporting_papers** | Gonzales (2023) — advanced economies benefit more; Damioli et al. (2021) — mainly OECD; Georgieff & Hyee (2022) — heterogeneous employment effects; Drago et al. (2025) — macro drivers of AI adoption |
| **what_cluster_identifies_well** | 异质性方向一致: 发达经济体受益更多. 可能的机制: ICT 基础设施(scope_001) 和人力资本(scope_002) 的门槛效应 |
| **what_remains_unresolved** | 是门槛(非线性)还是渐变(线性交互)? 是否应纳入制度质量 (rival_002: QoG 遗漏变量)? 中国/印度/巴西等非 OECD 但有大算力的国家是否遵循不同模式? |
| **how_project_enters** | 排除 OECD 稳健性检查. 零算力国家 (141/185) 的处理本身就是边界讨论的核心—这些国家是'未采用者'还是'以其他方式使用 AI'? |
| **citation_gaps** | Gonzales (2023) 的异质性结果表; Damioli (2021) 的样本组成; 需要发展中国家 AI 采用的数据(World Bank Digital Adoption Index?) |
| **risk** | 不要把'AI 只能富国受益'写成政策结论—这超出了本研究的设计范围. 不要说'制度约束' 如果没有 QoG 数据 |
| **author_decision** | 向《管理世界》读者: 这个 cluster 是否应加入中国/发展中国家视角的叙事? 是否补充中文文献中关于数字鸿沟的研究? |

---

### Cluster 4: 测量问题 — 我们真的在测量 AI 吗？

| element | content |
|---|---|
| **cluster_claim** | 现有文献全用 AI 专利或职业暴露度; TOP500 算力提供更直接的 AI 基础设施投入测量, 但本质上是通用超算测量 |
| **supporting_papers** | Gonzales (2023) — AI 专利; Damioli (2021) — AI 专利; Verschuere & Cameron (2026) — AI exposure; Georgieff & Hyee (2022) — AI exposure |
| **what_cluster_identifies_well** | 专利=创新产出; 算力=基础设施投入. 两种测量应相关但不完全重合. 算力比专利更接近'AI 能力'的经济学定义 |
| **what_remains_unresolved** | TOP500 包括大量非 AI 系统(天气预报, 核模拟)(scope_003). 2015 年前的算力是否可视为 AI 算力? 云算力和边缘设备不可见 |
| **how_project_enters** | 本研究是第一个使用 TOP500 算力作为 AI 能力代理的跨国面板研究. 这一'首次'需要文献证据支撑. 需要明确声明'TOP500 测量的不是 AI 专用算力'以及这意味着什么 |
| **citation_gaps** | 确认是否有已发表研究使用计算基础设施作为国家 AI 能力代理. 若有, 引用; 若无, 声明 gap |
| **risk** | 不要说'AI 算力'如果实际测量的是'通用超算'. 声明测量误差方向(低估 AI 算力)比隐瞒好 |
| **author_decision** | 论文中使用'AI 算力'还是'算力基础设施'? 是否补充 AI 专利数据做交叉验证? 是否需要单独一节讨论测量策略? |

---

## Paragraph Skeleton

| P# | purpose | claim_slot | evidence_to_use | risks | author_task |
|---|---|---|---|---|---|
| LR-P1 | 开场: 定位 AI 宏观效应的研究意义 | AI 作为 GPT 的理论共识 + 量级争议 | Cluster 1 | 避免'AI will transform everything'风格 | 写出一个具体而非空泛的开头; 建议用 Acemoglu 0.53% 作为钩子 |
| LR-P2 | 第一个争论: AI 是 GPT 还是普通自动化? | GPT 假说的支持证据 + Acemoglu 0.53% 的保守估计 | LF1, LF2, LF3, LF4 + rival_003 | 不要声称 GPT 已成定论 | 决定在这个争论中本研究站在哪一边; 用 'the jury is still out' 比 'it is now clear' 更安全 |
| LR-P3 | 过渡句: 即使接受 GPT 假说, 效应通过什么渠道实现? | 提出渠道问题 | — | 不要写成列清单 | 用 1-2 句自然过渡到下一段 |
| LR-P4 | 第二个争论: 自动化 vs 新任务渠道 | 任务模型框架 + 自动化替代证据(宏观+微观) + 新任务补偿逻辑 | LF5-LF9, synth_002, synth_003 | 不要把交互项写成渠道检验 | 重点写'为什么渠道分解重要' 而非 '我们怎么做'; 渠道分解的操作化留在实证策略部分 |
| LR-P5 | 第三个争论: 谁受益? 异质性/边界 | 发达 vs 发展中国家的异质性证据 + 门槛假说 | LF10-LF12, synth_004, scope_001, scope_002 | 不要说没有数据支持的边界声称 | 决定是否在此处引入'中国作为非 OECD 大算力国家'的叙事钩子 |
| LR-P6 | 测量 gap: 现有文献全部用专利, 无算力 | 专利 vs 算力测量的对比 + 本研究的贡献点 | synth_005, scope_003 | 不要把 gap 吹成 revolution | 确切声明: 本研究是第一个使用 TOP500 算力作为 AI 能力代理的跨国实证; 但 TOP500 的局限需在此段或脚注中说明 |
| LR-P7 | 收束: 总结文献缺口, 引出本研究的研究问题 | 三个 gap 总结: (1) 无算力→增长实证; (2) 无渠道分解; (3) 发展中经济体空白 | open_questions.md | 不要过度承诺: '填补 gap' 比 '解决 gap' 更准确 | 写简短收束, 直接过渡到研究假说或实证策略 |

---

## Citation Status Summary

| paper | matrix status | citation-ready? | action |
|---|---|---|---|
| Acemoglu & Restrepo (2019, JEP) | verified_primary | ✅ yes (abstract) | 建议打开全文确认任务框架精确表述 |
| Acemoglu & Restrepo (2018, AER) | verified_primary | ✅ yes (abstract) | 提取具体校准参数 |
| Acemoglu (2025, Economic Policy) | verified_primary | ✅ yes (abstract) | 提取 0.53% 的精确假设和置信区间 |
| Acemoglu et al. (2020, AEA P&P) | verified_primary | ✅ yes (abstract) | 提取 firm-level 效应量级 |
| Restrepo (2024, NBER) | verified_primary | ✅ yes (abstract) | 打开全文确认综述覆盖范围 |
| Gonzales (2023) | needs_primary_source | ⚠️ not yet | 必须打开全文提取异质性结果 |
| Damioli et al. (2021) | needs_primary_source | ⚠️ not yet | 必须打开全文确认效应量级 |
| Georgieff & Hyee (2022) | needs_primary_source | ⚠️ not yet | 打开全文确认就业效应的国家覆盖 |
| Verschuere & Cameron (2026) | needs_primary_source | ⚠️ not yet | 打开 SSRN 全文 |
| Nguyen (2026) | needs_primary_source | ⚠️ not yet | 打开 SSRN 全文确认 DID 设计 |
| Filippucci et al. (2024, OECD) | needs_primary_source | ⚠️ not yet | 打开 OECD 报告 |
| 蔡跃洲, 陈楠 (2019) | secondary_only | ❌ 未验证 | 需按数量经济技术经济研究定位并打开全文 |
| 谢伟丽, 邹淑青 (2025) | needs_primary_source | ⚠️ not yet | 确认是否直接测量增长 |

---

## Author Pre-Writing Decisions (prioritized)

**必须在写文献综述前决定 (blocking):**

1. **算力测量声称:** 论文中用 'AI 算力 (TOP500)' 还是 '算力基础设施 (TOP500)'? 前者声称更强但可质疑 (scope_003).
2. **核心 narrative:** 本研究的主要贡献声称是什么? (a) 首次用算力替代专利测量 AI, (b) 首次做跨国渠道分解, (c) 两者都是?
3. **中国的定位:** 《管理世界》读者期待中国视角. 在文献综述中如何定位中国/非 OECD 国家的 AI 增长效应?

**应在写文献综述前决定 (important):**

4. **35 篇 'needs_primary_source' 候选文献:** 先升级哪些到 verified? 至少 Gonzales (2023), Damioli (2021), Filippucci (2024), Verschuere (2026) 四篇必须在引用前验证.
5. **中文文献补充搜索:** 是否需要 serpapi/perplexity 搜索管理世界/经济研究/中国工业经济中关于 AI 与增长的实证研究?
6. **Acemoglu 0.53% 的定位:** 作为基准预期 (null) 还是作为被挑战的目标 (alternative)?

---

## Next Skill Route Suggestion

`literature-matrix` — 升级 4 篇核心文献到 verified_primary 并提取全文矩阵行
或
`ask_author` — 先回答上述 6 个 blocking/important decisions, 再写文献综述草稿