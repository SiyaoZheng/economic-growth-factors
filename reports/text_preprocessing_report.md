# 文本预处理报告

**生成时间**: 2026-07-04 16:55:16

## 语料概览

| 指标 | 数值 |
|------|------|
| 原始文档数 | 30 |
| 总分句数 | 590 |
| 有效分句数 (≥3 tokens) | 588 |
| 总 token 数 | 6,437 |
| 总唯一 token 数 | 1,735 |
| 平均 token 数/文档 | 215 |
| 平均唯一 token 数/文档 | 147 |

## 预处理步骤

1. **分句**: NLTK `sent_tokenize`（英语）
2. **分词 + 小写**: NLTK `word_tokenize` → `.lower()`
3. **去停用词**: NLTK English stopwords + 常见低信息词（also, however, etc.）
4. **词形还原**: NLTK `WordNetLemmatizer`
5. **过滤**: 去掉纯标点/纯数字 token、长度 ≤2 的 token、token 数 <3 的句子

## 输出文件

| 文件 | 内容 |
|------|------|
| `data/processed/text_corpus/corpus_summary.csv` | 文档级统计摘要 |
| `data/processed/text_corpus/corpus_token_counts.jsonl` | 文档级 token 计数 |
| `data/processed/text_corpus/corpus_sentences.jsonl` | 句子级 token 序列 |
