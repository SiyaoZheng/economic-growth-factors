#!/usr/bin/env python3
"""
文本预处理：对 Wikipedia 语料做分句、分词、去停用词、词形还原，
输出干净的 tokenized 面板数据集。
"""
import json
import csv
import re
from pathlib import Path

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ---------------------------------------------------------------------------
# 路径
# ---------------------------------------------------------------------------
RAW_DIR = Path("data/raw/text_corpus")
PROCESSED_DIR = Path("data/processed/text_corpus")
REPORTS_DIR = Path("reports")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 加载原始语料
# ---------------------------------------------------------------------------
with open(RAW_DIR / "economy_corpus.jsonl", "r", encoding="utf-8") as f:
    raw_docs = [json.loads(line) for line in f]

print(f"Loaded {len(raw_docs)} documents.")

# ---------------------------------------------------------------------------
# Step 1: 分句
# ---------------------------------------------------------------------------
all_sentences = []
for doc in raw_docs:
    sentences = sent_tokenize(doc["text"], language="english")
    for sent in sentences:
        all_sentences.append({
            "country": doc["country"],
            "page_title": doc["page_title"],
            "sentence": sent.strip(),
        })

print(f"Segmented into {len(all_sentences)} sentences.")

# ---------------------------------------------------------------------------
# Step 2: 分词 + 小写
# ---------------------------------------------------------------------------
STOP_WORDS = set(stopwords.words("english"))
# 额外停用词：Wikipedia 摘要常见噪音
EXTRA_STOP = {"also", "one", "may", "since", "however", "much", "well",
              "around", "among", "like", "per", "within", "due", "along",
              "e.g.", "i.e.", "etc.", "namely"}
STOP_WORDS.update(EXTRA_STOP)

LEMMATIZER = WordNetLemmatizer()

def clean_and_tokenize(text):
    """小写、分词、去标点/纯数字token、去停用词、词形还原"""
    tokens = word_tokenize(text.lower())
    cleaned = []
    for t in tokens:
        # 去掉纯标点或纯数字
        if not re.search(r"[a-z]", t):
            continue
        if t in STOP_WORDS:
            continue
        if len(t) <= 2:
            continue
        cleaned.append(LEMMATIZER.lemmatize(t))
    return cleaned

for entry in all_sentences:
    entry["tokens"] = clean_and_tokenize(entry["sentence"])

# ---------------------------------------------------------------------------
# Step 3: 过滤空句子
# ---------------------------------------------------------------------------
sentences_nonempty = [e for e in all_sentences if len(e["tokens"]) >= 3]
removed = len(all_sentences) - len(sentences_nonempty)
print(f"Removed {removed} short/empty sentences; {len(sentences_nonempty)} remain.")

# ---------------------------------------------------------------------------
# Step 4: 聚合到文档级别
# ---------------------------------------------------------------------------
from collections import Counter

doc_stats = []
for doc in raw_docs:
    doc_sentences = [e for e in sentences_nonempty if e["country"] == doc["country"]]
    all_tokens = sum((e["tokens"] for e in doc_sentences), [])
    token_counts = Counter(all_tokens)

    doc_stats.append({
        "country": doc["country"],
        "page_title": doc["page_title"],
        "raw_chars": len(doc["text"]),
        "raw_words": len(doc["text"].split()),
        "sentence_count": len(doc_sentences),
        "token_count": len(all_tokens),
        "unique_token_count": len(token_counts),
        "token_counter": token_counts,
    })

print(f"Aggregated to {len(doc_stats)} documents.")

# ---------------------------------------------------------------------------
# Step 5: 输出
# ---------------------------------------------------------------------------
# 文档级输出（CSV，不含 token_counter 列）
summary_fields = ["country", "page_title", "raw_chars", "raw_words",
                  "sentence_count", "token_count", "unique_token_count"]
with open(PROCESSED_DIR / "corpus_summary.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=summary_fields)
    writer.writeheader()
    for d in doc_stats:
        writer.writerow({k: d[k] for k in summary_fields})

# 文档级 token_counter 存为 JSONL（用于后续分析）
with open(PROCESSED_DIR / "corpus_token_counts.jsonl", "w", encoding="utf-8") as f:
    for d in doc_stats:
        record = {k: d[k] for k in summary_fields}
        record["token_counter"] = dict(d["token_counter"])
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

# 句子级输出
with open(PROCESSED_DIR / "corpus_sentences.jsonl", "w", encoding="utf-8") as f:
    for e in sentences_nonempty:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------------------
# 验证报告
# ---------------------------------------------------------------------------
total_tokens = sum(d["token_count"] for d in doc_stats)
total_unique = len(set.union(*(set(d["token_counter"].keys()) for d in doc_stats)))
avg_tokens_per_doc = total_tokens / len(doc_stats)
avg_unique_per_doc = sum(d["unique_token_count"] for d in doc_stats) / len(doc_stats)

report = f"""# 文本预处理报告

**生成时间**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 语料概览

| 指标 | 数值 |
|------|------|
| 原始文档数 | {len(raw_docs)} |
| 总分句数 | {len(all_sentences)} |
| 有效分句数 (≥3 tokens) | {len(sentences_nonempty)} |
| 总 token 数 | {total_tokens:,} |
| 总唯一 token 数 | {total_unique:,} |
| 平均 token 数/文档 | {avg_tokens_per_doc:,.0f} |
| 平均唯一 token 数/文档 | {avg_unique_per_doc:,.0f} |

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
"""

with open(REPORTS_DIR / "text_preprocessing_report.md", "w", encoding="utf-8") as f:
    f.write(report)

print("\n" + report)
print(f"\nFiles saved to {PROCESSED_DIR}/ and {REPORTS_DIR}/")
