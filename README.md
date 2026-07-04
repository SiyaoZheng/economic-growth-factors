# 各国经济增长影响因素研究

构建 1960 年起的跨国-年份面板数据，研究各国经济增长的关联因素。目标期刊：《管理世界》级别。

## 目录结构

```
data/                  # 数据（不纳入版本控制）
├── raw/               #   原始数据（只读）
│   ├── pwt/           #     Penn World Table 11.0
│   ├── maddison/      #     Maddison Project Database 2023
│   ├── wdi/           #     World Bank WDI JSON
│   └── top500/        #     TOP500 HPC XML + raw JSON/parquet
├── interim/           #   中间数据（清洗后、merge 前）
└── processed/         #   最终分析面板

docs/                  # 项目文档、变量字典、文献矩阵、研究设计
scripts/               # 所有分析脚本（Python + R）
outputs/               # 所有输出（不纳入版本控制）
├── figures/           #   图（DID 诊断图，png + pdf）
├── tables/            #   回归表格（HTML）
├── data_checks/       #   数据验证报告
└── writing/           #   写作稿、审稿回复、演示
```

## 一键运行

```bash
# 完整管线（跳过下载，仅数据面板 + 回归表格 + DID 诊断图）
python scripts/orchestrator.py

# 含下载
python scripts/orchestrator.py --download

# 仅某一部分
python scripts/orchestrator.py --data-only    # 数据面板 + 验证
python scripts/orchestrator.py --table-only   # 回归表格 Table 1 + Table 2
python scripts/orchestrator.py --did-only     # DID 诊断图
```

## 运行依赖

Python (polars, requests, openpyxl, pyarrow) + R (arrow, fixest, modelsummary, tinytable, dplyr, ggplot2, gridExtra)。

Python 依赖见 `requirements.txt`。
