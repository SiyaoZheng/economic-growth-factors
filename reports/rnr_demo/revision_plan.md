# 返修计划

**日期**：2026-07-04（演示）  
**审稿人**：2 位，共 13 项原子请求  
**目标**：分 4 阶段完成返修

---

## 阶段一：数据与模型修正（3-5 天）

| 优先级 | 评论 | 行动 | 负责人 |
|---|---|---|---|
| P1 | R1.2: 移除 pwt_tfp_lag1 | 修改 `run_analysis.R`，含/不含 TFP 双列 | agent |
| P1 | R2.3: 添加交互项主效应 | 修改交互模型公式 | agent |
| P2 | R1.4: 使用 pwt_import_share_abs | 修改变量名 | agent |
| P3 | R2.6: set.seed(42) | 添加一行代码 | agent |

## 阶段二：推断与规范（2-4 天）

| 优先级 | 评论 | 行动 | 负责人 |
|---|---|---|---|
| P1 | R1.3: 报告 wild cluster bootstrap p 值 | 安装 fwildclusterboot；运行 bootstrap；更新表格注释 | agent |
| P2 | R1.5: 缺失诊断 | 添加 missdiagnose 步骤到 `run_analysis.R` | agent |
| P2 | R2.4: 表格规范 | 更新 modelsummary notes/gof | agent |

## 阶段三：稳健性与替代度量（2-3 天）

| 优先级 | 评论 | 行动 | 负责人 |
|---|---|---|---|
| P2 | R1.7: Maddison 替代因变量 | 添加以 maddison_growth_annual 为 DV 的模型 | agent |
| P2 | R2.5: 三项稳健性 | 排除 OECD、排除极端值 |growth|>0.30、5年窗口 | agent |

## 阶段四：设计与文字（作者主导，4-7 天）

| 优先级 | 评论 | 行动 | 负责人 |
|---|---|---|---|
| P1 | R1.1: DID 设计重写 | 连续设定为主；二元 DID 附录；重写第3节 | agent → author |
| P1 | R2.2: 测量范围声明 | 在第2节添加声明 | author |
| P1 | R1.6: 更新文献综述 | 搜索并定位 Autor & Salomons 2024, Brynjolfsson et al. 2025 | agent → author |
| P1 | R2.1: 渠道 vs 异质性决策 | 等待作者决定 | author |

---

## 开放决策

| ID | 问题 | 影响 |
|---|---|---|
| R2.1 | 找新代理（ICT 服务出口等）还是降级为异质性？ | 决定正文第 4 节的全部叙事 |
| R1.1 | 二元 DID 彻底删除还是保留在附录？ | 决定事件研究图的出场位置 |

## 返修后的文件清单变更

- `scripts/run_analysis.R`：更新控制变量、公式、表格笔记、缺失诊断、稳健性
- `docs/variable_dictionary.csv`：无变化（pwt_import_share_abs 已存在）
- `docs/literature_matrix.csv`：新增 2+ 条目
- `reports/`：新增 wild-bootstrap 输出、稳健性回归输出
- 手稿：第 1-4 节修订、附录更新