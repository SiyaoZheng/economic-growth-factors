#!/usr/bin/env python3
"""
"X国经济对AI依赖度" 关键词命中率分析
基于预处理后的 token 计数数据。
"""
import json
import csv
from pathlib import Path
from collections import Counter

# ---------------------------------------------------------------------------
AI_KEYWORDS = {
    "artificial_intelligence": [
        "artificial", "intelligence", "intelligent",
    ],
    "machine_learning": [
        "machine", "learning", "learner",
    ],
    "deep_learning": [
        "deep", "learning", "neural",
    ],
    "ai_related": [
        "robot", "robotic", "robotics", "automation", "automated",
        "algorithm", "algorithmic",
    ],
    "data_science": [
        "data", "big", "analytic", "analytics", "mining",
    ],
    "digital_tech": [
        "digital", "digitization", "digitisation", "digitalization",
        "software", "computing", "compute", "computer",
        "chip", "semiconductor", "processor",
    ],
    "internet_platform": [
        "internet", "online", "platform", "e-commerce", "ecommerce",
        "fintech", "fintech",
    ],
}

# ---------------------------------------------------------------------------
PROCESSED_DIR = Path("data/processed/text_corpus")
REPORTS_DIR = Path("reports")

# 加载 token counts
with open(PROCESSED_DIR / "corpus_token_counts.jsonl", "r", encoding="utf-8") as f:
    docs = [json.loads(line) for line in f]

# 展平关键词集合 & 每个 token 对应哪些类别
token_to_categories = {}
all_ai_tokens = set()
for category, tokens in AI_KEYWORDS.items():
    for t in tokens:
        all_ai_tokens.add(t)
        token_to_categories.setdefault(t, []).append(category)

# ---------------------------------------------------------------------------
# 逐文档计算命中率
# ---------------------------------------------------------------------------
results = []
for doc in docs:
    token_counter = Counter(doc["token_counter"])
    total_tokens = doc["token_count"]
    
    # 各类别命中数
    category_hits = {}
    for cat, keywords in AI_KEYWORDS.items():
        hits = sum(token_counter.get(kw, 0) for kw in keywords)
        category_hits[cat] = hits
    
    # AI 总命中（unique token 级别）
    ai_tokens_found = [t for t in all_ai_tokens if token_counter.get(t, 0) > 0]
    ai_hit_count = sum(token_counter.get(t, 0) for t in all_ai_tokens)
    ai_hit_unique = len(ai_tokens_found)
    
    # 找出每个命中 token 的类别
    hit_details = {}
    for t in ai_tokens_found:
        hit_details[t] = token_to_categories.get(t, ["unknown"])
    
    results.append({
        "country": doc["country"],
        "total_tokens": total_tokens,
        "ai_hit_count": ai_hit_count,
        "ai_hit_unique": ai_hit_unique,
        "ai_hit_rate": round(ai_hit_count / total_tokens * 100, 2) if total_tokens > 0 else 0,
        "ai_hit_unique_rate": round(ai_hit_unique / total_tokens * 100, 2) if total_tokens > 0 else 0,
        **{f"hit_{cat}": category_hits[cat] for cat in AI_KEYWORDS},
        "hit_tokens": ai_tokens_found,
        "hit_categories": hit_details,
    })

# ---------------------------------------------------------------------------
# 排序 & 输出 CSV
# ---------------------------------------------------------------------------
results.sort(key=lambda r: r["ai_hit_rate"], reverse=True)

csv_fields = ["country", "total_tokens", "ai_hit_count", "ai_hit_unique",
              "ai_hit_rate", "ai_hit_unique_rate"]
csv_fields += [f"hit_{cat}" for cat in AI_KEYWORDS]

with open(REPORTS_DIR / "ai_dependency_keyword.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=csv_fields)
    writer.writeheader()
    for r in results:
        writer.writerow({k: r[k] for k in csv_fields})

# ---------------------------------------------------------------------------
# Markdown 报告
# ---------------------------------------------------------------------------
report_lines = [
    "# AI依赖度关键词命中率报告",
    f"\n**生成时间**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    "",
    "## 关键词分类",
    "",
    "| 类别 | 关键词 |",
    "|------|--------|",
]
for cat, tokens in AI_KEYWORDS.items():
    report_lines.append(f"| {cat} | {', '.join(tokens)} |")

report_lines += [
    "",
    "## 各国家AI关键词命中率（按命中率降序）",
    "",
    "| 排名 | 国家 | 总token | AI命中 | AI命中率(%) | 唯一命中 | 各类别命中 |",
    "|------|------|---------|--------|-------------|----------|------------|",
]

for rank, r in enumerate(results, 1):
    cat_str = " / ".join(f"{cat}={r[f'hit_{cat}']}" for cat in AI_KEYWORDS if r[f"hit_{cat}"] > 0)
    report_lines.append(
        f"| {rank} | {r['country']} | {r['total_tokens']} | {r['ai_hit_count']} | "
        f"{r['ai_hit_rate']} | {r['ai_hit_unique']} | {cat_str} |"
    )

report_lines += [
    "",
    "## 整体统计",
    "",
]
total_tokens_all = sum(r["total_tokens"] for r in results)
total_hits_all = sum(r["ai_hit_count"] for r in results)
avg_rate = sum(r["ai_hit_rate"] for r in results) / len(results)

# 全局关键词频率
global_counter = Counter()
for doc in docs:
    for token, count in doc["token_counter"].items():
        if token in all_ai_tokens:
            global_counter[token] += count

report_lines += [
    f"- 总token数: {total_tokens_all:,}",
    f"- 总AI关键词命中数: {total_hits_all:,}",
    f"- 整体命中率: {round(total_hits_all/total_tokens_all*100, 2)}%",
    f"- 各国平均命中率: {round(avg_rate, 2)}%",
    "",
    "### Top-20 AI 相关关键词频率",
    "",
    "| Token | 频率 | 类别 |",
    "|-------|------|------|",
]
for token, count in global_counter.most_common(20):
    cats = ", ".join(token_to_categories.get(token, []))
    report_lines.append(f"| {token} | {count} | {cats} |")

report = "\n".join(report_lines)

with open(REPORTS_DIR / "ai_dependency_keyword.md", "w", encoding="utf-8") as f:
    f.write(report)

print(report)
