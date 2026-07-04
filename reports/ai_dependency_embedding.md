# AI依赖度词向量分析报告

**生成时间**: 2026-07-04 17:00:10
**模型**: `all-MiniLM-L6-v2` (384维)

## 方法说明

1. 构建 25 个 AI 锚点短语（覆盖 AI 技术、数字经济、高技能劳动力、数字基础设施四个维度）
2. 用 sentence-transformers 编码所有锚点短语 → 取均值 → 归一化 = AI 概念向量
3. 对 588 个句子逐一编码，计算与 AI 概念向量的余弦相似度
4. 按国家聚合：均值、中位数、最大值、标准差、P75、P90、高相似度句子占比

## AI 锚点短语

- artificial intelligence and machine learning technologies
- deep learning neural networks and AI research
- robotics and intelligent automation systems
- advanced algorithms and data-driven decision making
- automated manufacturing and smart factories
- AI-powered software and digital platforms
- semiconductor chips and AI computing hardware
- digital economy and technology-driven growth
- innovation in high-tech industries
- knowledge economy and research development
- technology exports and intellectual property
- startup ecosystem and venture capital in tech
- digital transformation of traditional industries
- investment in research and development R&D
- highly skilled technology workforce
- STEM education and technical training
- automation replacing routine jobs
- digital skills and computer literacy
- internet connectivity and digital infrastructure
- cloud computing and data centers
- broadband access and mobile technology
- e-government and digital public services
- fintech and digital financial services

## 各国家 AI 依赖度排名（按均值余弦相似度降序）

| 排名 | 国家 | 句子数 | Mean | Median | Max | Std | P75 | P90 | High(AI>0.3) |
|------|------|--------|------|--------|-----|-----|-----|-----|--------------|
| 1 | China | 24 | 0.2578 | 0.2331 | 0.5464 | 0.0866 | 0.2879 | 0.3488 | 0.250 |
| 2 | South Africa | 14 | 0.2471 | 0.2372 | 0.4079 | 0.1036 | 0.2958 | 0.4021 | 0.286 |
| 3 | India | 26 | 0.2368 | 0.2334 | 0.4285 | 0.0772 | 0.2770 | 0.3244 | 0.154 |
| 4 | Indonesia | 13 | 0.2311 | 0.2324 | 0.3752 | 0.0743 | 0.2613 | 0.3421 | 0.231 |
| 5 | South Korea | 22 | 0.2294 | 0.2183 | 0.4539 | 0.0946 | 0.2840 | 0.3362 | 0.182 |
| 6 | United States | 28 | 0.2194 | 0.2129 | 0.4071 | 0.0814 | 0.2615 | 0.3456 | 0.179 |
| 7 | United Kingdom | 26 | 0.2183 | 0.2185 | 0.4331 | 0.0746 | 0.2602 | 0.2880 | 0.077 |
| 8 | Turkey | 16 | 0.2133 | 0.1839 | 0.4604 | 0.0952 | 0.2367 | 0.3372 | 0.125 |
| 9 | Japan | 21 | 0.2109 | 0.2145 | 0.3234 | 0.0534 | 0.2369 | 0.2701 | 0.095 |
| 10 | Singapore | 9 | 0.2107 | 0.2146 | 0.2656 | 0.0425 | 0.2371 | 0.2566 | 0.000 |
| 11 | Vietnam | 13 | 0.2101 | 0.2106 | 0.3108 | 0.0828 | 0.2665 | 0.2978 | 0.077 |
| 12 | Egypt | 16 | 0.2032 | 0.2013 | 0.2796 | 0.0533 | 0.2541 | 0.2704 | 0.000 |
| 13 | Ethiopia | 24 | 0.1975 | 0.1877 | 0.3685 | 0.0858 | 0.2631 | 0.3033 | 0.125 |
| 14 | Brazil | 22 | 0.1944 | 0.2040 | 0.4565 | 0.0864 | 0.2311 | 0.2629 | 0.045 |
| 15 | France | 22 | 0.1906 | 0.1801 | 0.3328 | 0.0601 | 0.2335 | 0.2510 | 0.045 |
| 16 | Nigeria | 12 | 0.1889 | 0.1851 | 0.3264 | 0.0793 | 0.2667 | 0.2842 | 0.083 |
| 17 | Bangladesh | 23 | 0.1879 | 0.1959 | 0.3374 | 0.0769 | 0.2434 | 0.2823 | 0.043 |
| 18 | Thailand | 19 | 0.1879 | 0.1725 | 0.5218 | 0.0999 | 0.2228 | 0.2676 | 0.053 |
| 19 | Italy | 30 | 0.1871 | 0.1624 | 0.3552 | 0.0766 | 0.2207 | 0.3124 | 0.133 |
| 20 | Poland | 17 | 0.1741 | 0.1417 | 0.3508 | 0.0765 | 0.2332 | 0.2553 | 0.059 |
| 21 | Australia | 18 | 0.1692 | 0.1694 | 0.2930 | 0.0590 | 0.1896 | 0.2382 | 0.000 |
| 22 | Mexico | 24 | 0.1674 | 0.1412 | 0.3707 | 0.0877 | 0.2195 | 0.2940 | 0.125 |
| 23 | Canada | 34 | 0.1654 | 0.1496 | 0.3312 | 0.0823 | 0.2106 | 0.2841 | 0.088 |
| 24 | Argentina | 8 | 0.1538 | 0.1367 | 0.2374 | 0.0690 | 0.2358 | 0.2370 | 0.000 |
| 25 | Netherlands | 26 | 0.1533 | 0.1479 | 0.4129 | 0.1067 | 0.2060 | 0.2761 | 0.077 |
| 26 | Switzerland | 6 | 0.1521 | 0.1308 | 0.2274 | 0.0525 | 0.1990 | 0.2242 | 0.000 |
| 27 | Germany | 29 | 0.1490 | 0.1440 | 0.3341 | 0.0708 | 0.2002 | 0.2297 | 0.035 |
| 28 | Russia | 18 | 0.1470 | 0.1500 | 0.2791 | 0.0693 | 0.1960 | 0.2259 | 0.000 |
| 29 | Chile | 18 | 0.1407 | 0.1308 | 0.2804 | 0.0639 | 0.1715 | 0.2355 | 0.000 |
| 30 | Saudi Arabia | 10 | 0.1047 | 0.0940 | 0.2436 | 0.0706 | 0.1331 | 0.2015 | 0.000 |

## 整体分布统计

| 指标 | 数值 |
|------|------|
| 句子总数 | 588 |
| 相似度均值 | 0.1917 |
| 相似度中位数 | 0.1878 |
| 相似度标准差 | 0.0861 |
| 最小/最大 | -0.0312 / 0.5464 |
| 高相似度(>0.3)句子占比 | 9.35% |

### Top-10 最接近 AI 概念的句子

| 国家 | 相似度 | 句子 |
|------|--------|------|
| China | 0.5464 | Manufacturing has been transitioning toward high-tech industries such as electric vehicles, renewable energy, telecommun... |
| Thailand | 0.5218 | Telecommunications and trade in services are emerging as centers of industrial expansion and economic competitiveness. |
| Turkey | 0.4604 | First established in 2000, many technoparks were pioneered by Turkish universities, now hosting over 1,600 R&D centers t... |
| Brazil | 0.4565 | From a colony focused on primary sector goods (sugar, gold and cotton), Brazil managed to create a diversified industria... |
| South Korea | 0.4539 | Additionally, economic growth is increasingly concentrated in a small number of tech-related companies, with smaller bus... |
| United Kingdom | 0.4331 | The United Kingdom's technology sector has an enterprise value of US$1.2 trillion, with fintech, health technology, and ... |
| India | 0.4285 | India's digital economy was estimated to be 11.7% of GDP, with its total value expected to surpass US$1 trillion by 2029... |
| Netherlands | 0.4129 | Many of the world's largest tech companies are based in its capital Amsterdam or have established their European headqua... |
| India | 0.4096 | The government plays a major role in sectors like supercomputing, space and shipping but private participation is growin... |
| South Africa | 0.4079 | The city is home to hundreds of tech firms, and is referred to as the "Startup Capital of Africa". |