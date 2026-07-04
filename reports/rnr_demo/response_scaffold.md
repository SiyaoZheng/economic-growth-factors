# 逐条回复脚手架（演示）

> ⚠️ 本文件是**作者可填充的脚手架**，不是最终提交版回复信。作者需将每个 `[author fills]` 槽位替换为最终措辞。

---

## 审稿人1

### R1.1：DID 识别基础薄弱（始终处理者 35/44）

```
Reviewer concern: 35/44 countries always-treated; only 9 late entrants provide identification
Author position: [author states agreement level — e.g. "同意审稿人判断：二元 DID 在本场景下识别变异过薄"]
Change made:
  - 已将连续 log_total_rmax 设为主设定（正文第3.1节）
  - 二元 DID 保留在附录 A，标注为"诊断性/探索性"
  - 事件研究图移至附录图 A2，附注"基于 9 个后期加入者的 pre-trend 不应被视为因果平行趋势证据"
Manuscript location: 正文 §3.1, 附录 A
Evidence/output: reports/did_diagnostics_report.html; 事件研究图 A2
Boundary to state: 连续处理变量的识别不依赖平行趋势假设，但需要条件独立性假设；当前控制变量设置 [author fills specific assumption]
Risk note: 不要声称二元 DID 的 pre-trend test 证明了平行趋势
```

### R1.2：pwt_tfp_lag1 是坏控制

```
Reviewer concern: TFP 是 GDP 的索洛剩余，如果算力影响 GDP，TFP 是后处理变量
Author position: [author fills — e.g. "接受此批评：TFP 从主设定移除"]
Change made:
  - 从主设定移除 pwt_tfp_lag1
  - 添加辅助列（含 TFP）以验证系数稳定性
Manuscript location: 表1 列(2)-(3)
Evidence/output: 重新运行的 run_analysis.R 输出
Boundary to state: 如果移除 TFP 后系数显著变化，需要讨论原因
```

### R1.3：聚类数不足（44 clusters）

```
Reviewer concern: <50 个聚类使 cluster-robust SE 向下偏误
Author position: [author fills]
Change made: 对主系数运行 wild cluster bootstrap（fwildclusterboot）；在表1注释报告中 bootstrap p 值
Manuscript location: 表1 注释
Evidence/output: bootstrap p 值输出
Boundary to state: Wild bootstrap 是补救措施而非彻底解决方案；仍应承认聚类有限
```

### R1.4：进口份额变量符号

```
Reviewer concern: PWT csh_m 取负值，系数符号难以解读
Author position: 已修正
Change made: 回归中使用 pwt_import_share_lag1_abs；添加脚注："PWT 的 csh_m 定义为 -(imports/GDP)，本文取绝对值使之直观为进口占比。"
Manuscript location: 表1 注释
Evidence/output: 重新运行的 run_analysis.R
```

### R1.5：样本损耗 35% 未报告

```
Reviewer concern: 从 1665 到 1080 的损耗未经诊断
Author position: [author fills]
Change made: 在 run_analysis.R 中增加 missingness diagnostics：报告各变量缺失 N、保留/剔除样本主要变量均值比较
Manuscript location: 附录 C
Evidence/output: missdiagnose 输出
Boundary to state: 如果丢失样本系统性更穷/更小，需要讨论外推边界
```

### R1.6：文献更新

```
Reviewer concern: 缺少 Autor & Salomons (2024) 和 Brynjolfsson et al. (2025)
Author position: [author fills]
Change made:
  - 检索并定位两篇文献的核心发现
  - 更新 §1-2 的文献综述段落
  - 在 §5 讨论本文与上述文献的对话点
Manuscript location: §1-2, §5
Evidence/output: 更新的 literature_matrix.csv；修改后的手稿段落
Boundary to state: 如新文献发现与本文方向不一致，不要隐瞒
```

### R1.7：Maddison 替代增长度量

```
Reviewer concern: 仅使用 PWT 增长率
Author position: 接受——已有 maddison_growth_annual
Change made: 添加以 maddison_growth_annual 为 DV 的稳健性表 A3
Manuscript location: 附录表 A3
Evidence/output: 重新运行的稳健性回归
Boundary to state: 对 source_consistency.csv 中差异 >0.10 log points 的观测进行审查并说明原因
```

---

## 审稿人2

### R2.1：新任务渠道代理太间接 ⚠️ 等待作者决策

```
Reviewer concern: pwt_human_capital_index 不是新任务创造的特异性代理
Author position: [author fills — 选择 A 或 B]
  A: 接受——寻找更直接代理（建议：ICT service exports %、high-tech patent share、startup formation rate）
  B: 部分接受——降级"渠道分解"为"异质性分析"，移除因果机制用语
Change made: [depends on decision]
Manuscript location: §4
Evidence/output: [depends on decision]
Boundary to state: [depends on decision]
```

### R2.2：测量范围声明

```
Reviewer concern: 141 个国家 TOP500 算力为零——这是测量零还是真实零？
Author position: 接受——这是测量零，不是真实零
Change made: 在 §2 添加范围声明：
  "本文的 TOP500 指标测量的是国家级超级计算基础设施，属于前沿 AI 算力的一个子集。
   许多发展中国家通过云计算服务（AWS、Azure、Google Cloud）使用 AI 但并不拥有超算系统。
   因此本文结果应解读为高端算力基础设施的经济效应，而非 AI 采纳的总效应。"
Manuscript location: §2（数据/测量）
```

### R2.3：交互项缺少主效应

```
Reviewer concern: 交互模型缺产业结构份额主效应
Author position: 接受——添加主效应
Change made: 在交互模型公式中添加 wdi_industry_value_added_gdp 和 wdi_services_value_added_gdp
Manuscript location: 表2
Evidence/output: 重新运行 run_analysis.R
Boundary to state: 在 FE 模型中，这些主效应的变异来源应说明
```

### R2.4：表格报告规范

```
Reviewer concern: 表1 缺少聚类数、国别数、DV 均值
Author position: 接受——这是期刊标准要求
Change made: 在 modelsummary notes 和 gof_map 中添加：
  - Number of clusters: 44
  - Number of countries: 185
  - DV mean: [value]
  - FE: country + year
Manuscript location: 表1 注释
```

### R2.5：三项稳健性检查

```
Reviewer concern: 排除 OECD、排除极端增长、5 年窗口
Author position: 接受
Change made:
  - Appendix Table A4: 排除高收入 OECD 国家
  - Appendix Table A5: 排除 |growth_annual| > 0.30
  - Appendix Table A6: 以 growth_5yr 为 DV
Manuscript location: 附录表 A4-A6
Evidence/output: 重新运行的稳健性子程序
Boundary to state: 如结果方向或显著性变化，需要在正文中讨论
```

### R2.6：set.seed()

```
Reviewer concern: R 脚本缺少随机种子
Author position: 接受——惯常可复现性要求
Change made: 在 scripts/run_analysis.R 第 1 行添加 set.seed(42)
Manuscript location: scripts/run_analysis.R:1
```

---

## 最终审计清单

- [ ] 所有 `accept` 项都有 `done_evidence`
- [ ] R2.1 的作者决策已完成
- [ ] 手稿每一处修订都对应一个 revision_matrix 行
- [ ] `confidentiality_status` 全部为 `redacted`（演示用）
- [ ] 表格/附录编号已根据实际手稿更新
- [ ] 没有一条回复声称分析存在而实际不存在
- [ ] 没有一条回复越俎代庖替作者做策略性判断