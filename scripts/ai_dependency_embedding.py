#!/usr/bin/env python3
"""
"X国经济对AI依赖度" 词向量方法
用 sentence-transformers 对每句话编码，计算句子与 AI 概念向量的余弦相似度，
聚合到国家级别作为 AI 依赖度指标。
"""
import json
import csv
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
PROCESSED_DIR = Path("data/processed/text_corpus")
REPORTS_DIR = Path("reports")
MODEL_NAME = "all-MiniLM-L6-v2"

# AI 概念锚点：描述 AI 依赖经济的关键维度
AI_ANCHOR_TEXTS = [
    # 技术核心
    "artificial intelligence and machine learning technologies",
    "deep learning neural networks and AI research",
    "robotics and intelligent automation systems",
    "advanced algorithms and data-driven decision making",
    "automated manufacturing and smart factories",
    "AI-powered software and digital platforms",
    "semiconductor chips and AI computing hardware",
    # 经济转型
    "digital economy and technology-driven growth",
    "innovation in high-tech industries",
    "knowledge economy and research development",
    "technology exports and intellectual property",
    "startup ecosystem and venture capital in tech",
    "digital transformation of traditional industries",
    "investment in research and development R&D",
    # 劳动力与技能
    "highly skilled technology workforce",
    "STEM education and technical training",
    "automation replacing routine jobs",
    "digital skills and computer literacy",
    # 基础设施
    "internet connectivity and digital infrastructure",
    "cloud computing and data centers",
    "broadband access and mobile technology",
    "e-government and digital public services",
    "fintech and digital financial services",
]

# ---------------------------------------------------------------------------
# 加载模型和句子
# ---------------------------------------------------------------------------
print(f"Loading model: {MODEL_NAME} ...")
model = SentenceTransformer(MODEL_NAME)

print("Loading sentences ...")
with open(PROCESSED_DIR / "corpus_sentences.jsonl", "r", encoding="utf-8") as f:
    sentences = [json.loads(line) for line in f]
print(f"  {len(sentences)} sentences loaded.")

# ---------------------------------------------------------------------------
# 计算 AI 锚点向量
# ---------------------------------------------------------------------------
print("Encoding AI anchor texts ...")
anchor_embeddings = model.encode(AI_ANCHOR_TEXTS, show_progress_bar=True)
ai_concept_vector = anchor_embeddings.mean(axis=0)  # 平均 → 单一AI概念向量
ai_concept_vector = ai_concept_vector / np.linalg.norm(ai_concept_vector)  # 归一化

# ---------------------------------------------------------------------------
# 逐句编码并计算余弦相似度
# ---------------------------------------------------------------------------
print("Encoding sentences ...")
sentence_texts = [s["sentence"] for s in sentences]
sentence_embeddings = model.encode(sentence_texts, show_progress_bar=True)
# 归一化
sentence_embeddings = sentence_embeddings / np.linalg.norm(
    sentence_embeddings, axis=1, keepdims=True
)

# 余弦相似度
similarities = np.dot(sentence_embeddings, ai_concept_vector)
for i, sim in enumerate(similarities):
    sentences[i]["ai_similarity"] = float(np.clip(sim, -1, 1))

print(f"  Similarity range: [{similarities.min():.4f}, {similarities.max():.4f}]")
print(f"  Similarity mean:  {similarities.mean():.4f}")

# ---------------------------------------------------------------------------
# 聚合到国家级别
# ---------------------------------------------------------------------------
from collections import defaultdict

country_sims = defaultdict(list)
country_sentence_count = defaultdict(int)
country_tokens = defaultdict(int)
country_page_title = {}

with open(PROCESSED_DIR / "corpus_token_counts.jsonl", "r", encoding="utf-8") as f:
    docs = [json.loads(line) for line in f]
    for doc in docs:
        country_tokens[doc["country"]] = doc["token_count"]
        country_page_title[doc["country"]] = doc["page_title"]

for sent in sentences:
    country = sent["country"]
    country_sims[country].append(sent["ai_similarity"])
    country_sentence_count[country] += 1

# 三种聚合指标
results = []
for country in sorted(country_sims.keys()):
    sims = np.array(country_sims[country])
    results.append({
        "country": country,
        "page_title": country_page_title.get(country, ""),
        "sentence_count": country_sentence_count[country],
        "token_count": country_tokens.get(country, 0),
        "ai_dependency_mean": round(float(sims.mean()), 4),
        "ai_dependency_median": round(float(np.median(sims)), 4),
        "ai_dependency_max": round(float(sims.max()), 4),
        "ai_dependency_std": round(float(sims.std()), 4),
        "ai_dependency_p75": round(float(np.percentile(sims, 75)), 4),
        "ai_dependency_p90": round(float(np.percentile(sims, 90)), 4),
        "high_ai_ratio": round(float((sims > 0.3).mean()), 4),  # 高AI相似度句子占比
    })

results.sort(key=lambda r: r["ai_dependency_mean"], reverse=True)

# ---------------------------------------------------------------------------
# 输出 CSV
# ---------------------------------------------------------------------------
csv_fields = [
    "country", "sentence_count", "token_count",
    "ai_dependency_mean", "ai_dependency_median", "ai_dependency_max",
    "ai_dependency_std", "ai_dependency_p75", "ai_dependency_p90",
    "high_ai_ratio",
]
with open(REPORTS_DIR / "ai_dependency_embedding.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=csv_fields)
    writer.writeheader()
    for r in results:
        writer.writerow({k: r[k] for k in csv_fields})

# 保存句子级相似度
with open(PROCESSED_DIR / "corpus_sentences_with_ai_sim.jsonl", "w", encoding="utf-8") as f:
    for s in sentences:
        f.write(json.dumps(s, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------------------
# Markdown 报告
# ---------------------------------------------------------------------------
from datetime import datetime

lines = [
    "# AI依赖度词向量分析报告",
    f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    f"**模型**: `{MODEL_NAME}` (384维)",
    "",
    "## 方法说明",
    "",
    "1. 构建 25 个 AI 锚点短语（覆盖 AI 技术、数字经济、高技能劳动力、数字基础设施四个维度）",
    "2. 用 sentence-transformers 编码所有锚点短语 → 取均值 → 归一化 = AI 概念向量",
    f"3. 对 {len(sentences)} 个句子逐一编码，计算与 AI 概念向量的余弦相似度",
    "4. 按国家聚合：均值、中位数、最大值、标准差、P75、P90、高相似度句子占比",
    "",
    "## AI 锚点短语",
    "",
]
for t in AI_ANCHOR_TEXTS:
    lines.append(f"- {t}")

lines += [
    "",
    "## 各国家 AI 依赖度排名（按均值余弦相似度降序）",
    "",
    "| 排名 | 国家 | 句子数 | Mean | Median | Max | Std | P75 | P90 | High(AI>0.3) |",
    "|------|------|--------|------|--------|-----|-----|-----|-----|--------------|",
]

for rank, r in enumerate(results, 1):
    lines.append(
        f"| {rank} | {r['country']} | {r['sentence_count']} | "
        f"{r['ai_dependency_mean']:.4f} | {r['ai_dependency_median']:.4f} | "
        f"{r['ai_dependency_max']:.4f} | {r['ai_dependency_std']:.4f} | "
        f"{r['ai_dependency_p75']:.4f} | {r['ai_dependency_p90']:.4f} | "
        f"{r['high_ai_ratio']:.3f} |"
    )

# 整体统计
all_sims = np.array([s["ai_similarity"] for s in sentences])
lines += [
    "",
    "## 整体分布统计",
    "",
    f"| 指标 | 数值 |",
    f"|------|------|",
    f"| 句子总数 | {len(sentences)} |",
    f"| 相似度均值 | {all_sims.mean():.4f} |",
    f"| 相似度中位数 | {np.median(all_sims):.4f} |",
    f"| 相似度标准差 | {all_sims.std():.4f} |",
    f"| 最小/最大 | {all_sims.min():.4f} / {all_sims.max():.4f} |",
    f"| 高相似度(>0.3)句子占比 | {(all_sims > 0.3).mean():.2%} |",
    "",
    "### Top-10 最接近 AI 概念的句子",
    "",
    "| 国家 | 相似度 | 句子 |",
    "|------|--------|------|",
]
top10 = sorted(sentences, key=lambda s: s["ai_similarity"], reverse=True)[:10]
for s in top10:
    text = s["sentence"][:120] + ("..." if len(s["sentence"]) > 120 else "")
    lines.append(f"| {s['country']} | {s['ai_similarity']:.4f} | {text} |")

report = "\n".join(lines)
with open(REPORTS_DIR / "ai_dependency_embedding.md", "w", encoding="utf-8") as f:
    f.write(report)

print(report)
