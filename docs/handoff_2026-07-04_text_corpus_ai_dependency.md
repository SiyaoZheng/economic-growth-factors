# Handoff：Text-as-Data 分析演示 —— 各国经济对 AI 依赖度

**日期**：2026-07-04  
**任务**：为课堂演示快速搜集 Wikipedia 经济词条语料，用关键词命中率和词向量（Sentence-BERT）两种方法构建「AI 依赖度」跨国指标，撰写 LaTeX 分析报告。  
**状态**：✅ Pipeline 可复现，PDF 报告已生成，所有文件就位。

---

## 一、已完成的工作

### 1. 语料下载
- **脚本**：`scripts/preprocess_text_corpus.py` 内含 Wikipedia API 抓取逻辑（实际数据通过临时 Python heredoc 抓取）
- **语料**：30 国「Economy of X」Wikipedia 词条导言（英文）
- **原始文件**：`data/raw/text_corpus/economy_corpus.jsonl`（30条），`economy_corpus.csv`
- **数据来源**：requests 直连 `https://en.wikipedia.org/w/api.php`，每国一次请求，sleep 0.3s

### 2. 文本预处理
- **脚本**：`scripts/preprocess_text_corpus.py`
- **步骤**：分句 → 分词+小写 → 去停用词 → 词形还原 → 过滤
- **输出文件**：
  - `data/processed/text_corpus/corpus_sentences.jsonl`（588条句子，含 tokens）
  - `data/processed/text_corpus/corpus_summary.csv`（文档级统计）
  - `data/processed/text_corpus/corpus_token_counts.jsonl`（文档级 token 频率）
- **报告**：`reports/text_preprocessing_report.md`

### 3. 关键词命中率基准
- **脚本**：`scripts/ai_dependency_keyword.py`
- **方法**：7 类 AI 关键词（artificial_intelligence, machine_learning, deep_learning, ai_related, data_science, digital_tech, internet_platform），逐文档计命中数和命中率
- **结果**：整体命中率仅 0.3%，命中 token 集中在 `data`, `mining`, `digital`, `semiconductor` 等；19/30 国家命中为 0。关键词方法在语料过小时严重受限。
- **输出**：`reports/ai_dependency_keyword.csv`, `reports/ai_dependency_keyword.md`

### 4. 词向量方法（主要结果）
- **脚本**：`scripts/ai_dependency_embedding.py`
- **模型**：Sentence-BERT `all-MiniLM-L6-v2`（384维，自动下载到 HF cache）
- **方法**：
  - 23 个 AI 锚定短语，覆盖 4 个维度（AI核心7条、经济转型5条、劳动力4条、基础设施7条）
  - 锚定短语编码 → 取均值归一化 = AI 概念向量
  - 588 句逐一编码 → 余弦相似度 → 按国家聚合（mean/median/max/std/P75/P90/high_ratio）
- **输出文件**：
  - `data/processed/text_corpus/corpus_sentences_with_ai_sim.jsonl`（句子级 + `ai_similarity` 字段）
  - `reports/ai_dependency_embedding.csv`（30国完整排名）
  - `reports/ai_dependency_embedding.md`（Markdown 报告）

### 5. LaTeX 分析报告
- **源文件**：`reports/ai_dependency_report.tex`（xelatex 编译）
- **编译命令**：在 `reports/` 目录执行 `xelatex -interaction=nonstopmode ai_dependency_report.tex` 三次
- **输出**：`reports/ai_dependency_report.pdf`（6页，213KB）
- **报告内容**：引言、数据与预处理、方法（锚定短语表 + 维度相关性验证）、30国排名表、分组箱线图对比、Top-10/Bottom-5/四维度例句定性验证、讨论（中国第一名合理性、新兴vs发达分化）、方法局限、结论

---

## 二、关键数值结果速查

| 指标 | 数值 |
|------|------|
| 30国均值范围 | 0.105（沙特）～ 0.258（中国） |
| Top-5 国家 | 中国 0.258, 南非 0.247, 印度 0.237, 印尼 0.231, 韩国 0.229 |
| Bottom-5 国家 | 沙特 0.105, 智利 0.141, 俄罗斯 0.147, 德国 0.149, 瑞士 0.152 |
| Top-5 组 >0.3 占比 | 21.2% |
| Bottom-5 组 >0.3 占比 | 1.2% |
| 维度间相关系数范围 | 0.52 ～ 0.65 |
| 最高分单句 | China: 0.5464（高科技制造转型） |
| 最低分单句 | Netherlands: -0.0312（财政盈余） |

---

## 三、文件索引

```
scripts/
  preprocess_text_corpus.py         ← 预处理 pipeline
  ai_dependency_keyword.py          ← 关键词命中率分析
  ai_dependency_embedding.py        ← 词向量 AI 依赖度分析（主要脚本）

data/raw/text_corpus/
  economy_corpus.jsonl              ← 30国原始 Wikipedia 导言
  economy_corpus.csv                ← 同上（CSV版）

data/processed/text_corpus/
  corpus_sentences.jsonl            ← 句子级预处理结果（含 tokens）
  corpus_sentences_with_ai_sim.jsonl ← 句子级 + ai_similarity 字段
  corpus_summary.csv                ← 文档级统计
  corpus_token_counts.jsonl         ← 文档级 token 频率

reports/
  text_preprocessing_report.md      ← 预处理报告
  ai_dependency_keyword.md / .csv   ← 关键词命中率报告
  ai_dependency_embedding.md / .csv ← 词向量方法报告
  ai_dependency_report.tex          ← LaTeX 源文件
  ai_dependency_report.pdf          ← 最终 PDF（6页）
```

---

## 四、继续工作的方式

### 如果要重新跑整个 pipeline
```bash
cd /Users/siyaozheng/Documents/经济增长因素研究
python3 scripts/preprocess_text_corpus.py       # 1. 预处理
python3 scripts/ai_dependency_keyword.py         # 2. 关键词（可选）
python3 scripts/ai_dependency_embedding.py       # 3. 词向量（核心）
cd reports && xelatex -interaction=nonstopmode ai_dependency_report.tex  # 4. 编译（×3）
```

### 如果要扩展语料
- 修改 `scripts/preprocess_text_corpus.py` 中的国家列表或下载逻辑
- 或在 `data/raw/text_corpus/economy_corpus.jsonl` 中手动追加更多文档
- 重新运行预处理 + embedding 脚本

### 如果要改进指标
关心的几个方向：
- 加权聚合（tf-idf / 位置权重 / 句子长度加权）
- 更多锚定短语（或者用外部词表如 AI 政策文书等）
- 用全文而非导言（但 Wikipedia 全文会很大，需要管理 token 量）
- 添加非英语 Wikipedia 版本（中文、阿拉伯语等）
- 与结构化指标（R&D 支出、ICT 出口占比、专利数）做相关性验证

### 如果要用于课堂
- PDF 可直接放映（6页，表格和例句都已排版好）
- 可以额外生成 beamer 版幻灯片
- 数据在 `reports/ai_dependency_embedding.csv` 中，可导入 Stata/R 画图

---

## 五、踩坑备忘

1. **Wikipedia API 分页/超时**：直接 `requests` + `per_page=30000` 策略（本 task 中只抓了导言，每国1次请求，无分页问题）
2. **gensim 编译失败**：numpy 2.x 移除了 `numpy.distutils`，gensim 无法 `pip install`。改用 `sentence-transformers`（已安装并运行成功）
3. **pdflatex 不支持中文**：改为 xelatex + `ctex` / `xeCJK` 包
4. **LaTeX 字体缺失**：pdflatex 模式下 `unkai30` 字体导致编译失败；切换到 xelatex + macOS 系统字体（Songti SC, Heiti SC）解决
5. **关键词方法无效**：30文档×平均387词太小，关键词命中率仅0.3%。词向量方法利用语义相似度解决了稀疏性问题。
6. **apply_patch 不可用**：本 session 中 `apply_patch` 返回 `unsupported call`，所有文件编辑通过 `cat << 'EOF'` heredoc 完成
</HANDE>
echo "Handoff written"