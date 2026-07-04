# Literature Open Questions

Generated: 2026-07-04 | Updated: 2026-07-04 (theory synthesis) | Project: AI算力与经济增长 (R1)

## Handoff Summary

literature-matrix skill 已完成 Step -1 到 Step 5 全流程，输出交付如下：

| 交付物 | 路径 | 状态 |
|---|---|---|
| 候选文献发现 | `docs/literature_candidate_discovery.csv` | ✅ 37条, 验证通过 |
| 文献矩阵 | `docs/literature_matrix.csv` | ✅ 22条, 验证通过 |
| 筛选日志 | `docs/literature_screening_log.md` | ✅ |
| 搜索策略 | `docs/search_queries.md` | ✅ 15个层级 |
| 理论合成 | `docs/literature_theory_synthesis.csv` | ✅ 7条(2机制+1概念+1边界+1测量+1竞争+1范围) |
| 竞争解释 | `docs/theory_rival_map.csv` | ✅ 3条 |
| 范围条件 | `docs/theory_scope_map.csv` | ✅ 3条 |
| 交互浏览页面 | `reports/literature_matrix_report.html` | ✅ 37张卡片, 可筛选/搜索 |

## Evidence Clusters

| 聚类 | 论文数 | 核心主张 |
|---|---|---|
| **概念层: AI as GPT → growth** | 4 | AI专利→增长效应为正但量级小; Acemoglu(2025): 10年TFP效应~0.53% |
| **机制: 自动化替代渠道** | 4 | 自动化替代劳动→短期资本回报↑但劳动份额↓; 净增长效应取决于新任务补偿速度 |
| **机制: 新任务恢复渠道** | 3 | AI创造新任务→恢复劳动需求→TFP↑; 前提是人力资本门槛 |
| **边界: OECD vs 发展中** | 3 | AI增长效应在发达经济体更强; 发展中国家面临数据/技能/制度三重约束 |
| **测量: 专利 vs 算力** | 4 | 现有文献全用AI专利/暴露度; 算力是更直接的投入测量 |
| **竞争: 反向因果** | 2 | 增长→算力投资的因果方向不可忽视; 当前FE设计仅缓解时不变混淆 |
| **范围: 零算力+TOP500本质** | 2 | 141国零算力; TOP500捕捉通用算力非AI专用算力 |

## Unresolved Researcher Decisions (ordered by urgency)

### Blocking: must decide before next analysis step

1. **算力测量的外部有效性:** TOP500捕捉的是通用超算而非AI专用算力。我们声称'算力是AI能力的代理'是否合理？如果reviewer指出TOP500包括大量非AI系统(天气预报、核模拟)，如何回应？(scope_003)

2. **零算力国家的处理:** 主分析是否限制在44国有TOP500出现的国家？如果141个零算力国家占样本76%，log_total_rmax的识别完全依赖有-无对比而非算力强度。(synth_007)

3. **渠道代理变量:** 接受`wdi_industry_value_added_gdp`(自动化)和`pwt_human_capital_index`(新任务)的代理策略吗？新任务渠道的代理尤其薄弱——人力资本≠新任务创造。(synth_003)

### Important: should decide before writing

4. **内生性策略:** 是否寻找外生冲击做IV/DID？目前TWFE仅提供关联性证据。候选IV: submarine cable landings, cloud region launches, 历史CS院系数量。(synth_006)

5. **中文文献的定位:** 仅2篇中文核心期刊候选(蔡跃洲2019数量经济技术经济研究、谢伟丽2025工业技术经济)。需要在管理世界/经济研究层面补充搜索吗？

### Can defer:不影响核心分析

6. **是否需要补充AI专利数据做交叉验证?** (synth_005)

7. **AI使用意图调查(如OECD AI surveys)作为AI采用的补充测量?**

## Next Skill Route

**推荐路由: `methods-reviewer`** — 将目前的识别策略、渠道代理、内生性担忧交给methods-reviewer做设计审计。在此之后由`study-design-builder`调整研究设计声明，再回到实证工作。

备选: 如果Adrian认为直接跑更多回归比设计审计更优先，则路由到 `research-analysis-runner` 继续运行Gonzales-style FE + GMM对比。

## Literature Gaps

- **无算力→增长的直接实证:** 没有任何已发表研究使用TOP500或算力基础设施作为国家层面AI能力的测量
- **Post-ChatGPT证据稀缺:** 仅Verschuere & Cameron (2026)等2-3篇工作论文覆盖2022-2024
- **无跨国渠道分解:** 自动化vs新任务渠道在跨国面板上的操作化无实证先例
- **发展中经济体被系统性忽略:** 绝大多数研究聚焦OECD/G20/EU

## Claim Boundaries

- 本研究不声称TOP500完美测量AI算力——它测量的是高端超算，可能遗漏云算力和边缘设备
- 交互项不声称因果渠道——仅作为异质性分析的模式识别
- 2015-2023面板太短，无法检测长滞后效应(Brynjolfsson productivity paradox)

