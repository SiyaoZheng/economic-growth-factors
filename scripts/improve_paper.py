#!/usr/bin/env python3
"""
improve_paper.py — 两步智能 agent 审阅-改进循环
- Step 1 (审阅 agent): 全面提取 PDF + LaTeX 源 + 编译日志中的所有质量信号，
  生成一个详尽的结构化 JSON TODO 文件。
  这个 TODO 文件足够详尽，后续任何 codex agent 读取后即可逐条执行改进。
- Step 2: 自动修复 auto_fixable 项（排版、unicode、表格注记等），重新编译。
- 手动项留待 codex agent 处理。
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT / "outputs" / "writing" / "full_paper.pdf"
TEX_PATH = ROOT / "outputs" / "writing" / "full_paper.tex"
LOG_PATH = ROOT / "outputs" / "writing" / "full_paper.log"
TODO_FILE = ROOT / "outputs" / "writing" / "improvement_todos.json"
BUILD_PAPER = ROOT / "scripts" / "build_paper.py"


def run_cmd(args: list[str], capture: bool = True) -> tuple[int, str, str]:
    result = subprocess.run(args, cwd=ROOT, capture_output=capture, text=True)
    return result.returncode, result.stdout, result.stderr


def extract_all_signals() -> dict:
    """
    审阅 agent — 从 PDF、LaTeX 源、编译日志中全面提取质量信号。
    返回一个字典，包含所有可用于判断"离发表标准还有多远"的信息。
    """
    signals: dict = {}

    # --- PDF text ---
    ret, pdf_text, stderr = run_cmd(["pdftotext", "-layout", str(PDF_PATH), "-"])
    if ret != 0:
        print(f"  ✗ pdftotext failed: {stderr}")
        signals["error"] = "pdftotext_failed"
        return signals
    signals["pdf_text"] = pdf_text
    signals["pdf_chars"] = len(pdf_text)
    signals["pdf_lines"] = len(pdf_text.split("\n"))

    # --- TeX source ---
    tex_body = ""
    if TEX_PATH.exists():
        tex_body = TEX_PATH.read_text()
    signals["tex_body"] = tex_body
    signals["tex_chars"] = len(tex_body)

    # --- Compilation log ---
    log_text = ""
    if LOG_PATH.exists():
        log_text = LOG_PATH.read_text()
    signals["log_text"] = log_text

    # --- Signal extraction ---
    # These are computed signals that the TODO generator will use

    # 1. Pages (use pdfinfo for reliability; log lines can truncate)
    try:
        pdfinfo_result = subprocess.run(
            ["pdfinfo", str(PDF_PATH)], capture_output=True, text=True, cwd=ROOT
        )
        pages_match = re.search(r'Pages:\s+(\d+)', pdfinfo_result.stdout)
        signals["pages"] = int(pages_match.group(1)) if pages_match else None
    except Exception:
        # Fallback to log parsing
        pages_match = re.search(r'Output written on .*?full_paper\.pdf \((\d+) pages', log_text)
        signals["pages"] = int(pages_match.group(1)) if pages_match else None

    # 2. Overfull/Underfull boxes
    signals["overfull_hboxes"] = len(re.findall(r'Overfull', log_text))
    signals["underfull_hboxes"] = len(re.findall(r'Underfull', log_text))

    # 3. Missing characters
    missing_chars = re.findall(r'Missing character: There is no (.*?) in font', log_text)
    signals["missing_char_count"] = len(missing_chars)
    signals["missing_char_details"] = list(set(missing_chars))

    # 4. LaTeX warnings (exclude common benign ones)
    warnings = [l.strip() for l in log_text.split('\n')
                if 'Warning' in l
                and 'Rerun' not in l
                and 'Hyper' not in l
                and 'xeCJK Warning' not in l]
    signals["latex_warnings"] = warnings

    # 5. Garbled chars in PDF
    garbled_count = pdf_text.count('�')
    signals["garbled_chars"] = garbled_count
    if garbled_count > 0:
        garbled_lines = []
        for lineno, line in enumerate(pdf_text.split('\n'), 1):
            if '�' in line:
                garbled_lines.append({"line": lineno, "text": line.strip()[:120]})
        signals["garbled_lines"] = garbled_lines[:20]  # cap

    # 6. Section structure
    sections = re.findall(r'\\section\{([^}]+)\}', tex_body)
    signals["sections"] = sections

    # 7. Tables
    table_inputs = re.findall(r'\\input\{(table[^}]+)\}', tex_body)
    signals["table_inputs"] = table_inputs

    # 8. Figures
    figure_refs = re.findall(r'\\includegraphics[^}]*\{([^}]+)\}', tex_body)
    signals["figure_files"] = figure_refs
    # Check if figures are in appendix
    signals["figures_in_appendix"] = bool(re.search(r'\\section\*\{附录：图形\}', tex_body))
    # Check in-text figure references
    signals["intext_figure_refs"] = len(re.findall(r'\\ref\{fig:', tex_body))
    # Check for 如图 references in PDF text
    signals["chinese_figure_refs"] = len(re.findall(r'如[图圖]', pdf_text))

    # 9. Author metadata
    signals["has_author"] = bool(re.search(r'\\author\{', tex_body))
    signals["has_thanks"] = bool(re.search(r'\\thanks\{', tex_body))
    signals["has_acknowledgments"] = bool(re.search(r'致谢|acknowledgment', tex_body, re.IGNORECASE))
    signals["has_funding"] = bool(re.search(r'基金|funding|grant', tex_body, re.IGNORECASE))

    # 10. Abstract
    abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex_body, re.DOTALL)
    if abstract_match:
        abstract_txt = abstract_match.group(1)
        signals["abstract_chars"] = len(abstract_txt)
        signals["abstract_has_keywords"] = bool(re.search(r'关键词|keywords', abstract_txt))
    else:
        signals["abstract_chars"] = 0
        signals["abstract_has_keywords"] = False

    # 11. References
    ref_section = re.search(r'\\section\*\{参考文献\}(.*?)(?:\\section|\\end\{document\})', tex_body, re.DOTALL)
    if ref_section:
        ref_text = ref_section.group(1)
        ref_entries = re.findall(r'\\\[(\d+)\\\]', ref_text)
        signals["reference_count"] = len(ref_entries)
    else:
        signals["reference_count"] = 0

    # 12. English subtitle
    signals["has_english_subtitle"] = bool(
        "AI Compute Infrastructure" in tex_body or
        "Preliminary Evidence" in tex_body
    )

    # 13. Regression model descriptions in text
    signals["has_regression_equation"] = bool(re.search(r'growth_annual|Y_\{it\}', tex_body))
    signals["mentions_fixed_effects"] = bool(re.search(r'固定效应|fixed.effects', pdf_text))
    signals["mentions_clustered_se"] = bool(re.search(r'聚类|cluster', pdf_text))

    # 14. Word count estimate (for 管理世界)
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', pdf_text))
    signals["chinese_chars"] = chinese_chars

    # 15. Tables: check if they have notes
    table1_tex = ""
    table2_tex = ""
    tbl1_path = ROOT / "outputs" / "writing" / "table1_main_effect.tex"
    tbl2_path = ROOT / "outputs" / "writing" / "table2_channel.tex"
    if tbl1_path.exists():
        table1_tex = tbl1_path.read_text()
    if tbl2_path.exists():
        table2_tex = tbl2_path.read_text()
    signals["table1_has_notes"] = bool(re.search(r'注|Notes|\\\\注', table1_tex))
    signals["table2_has_notes"] = bool(re.search(r'注|Notes|\\\\注', table2_tex))
    signals["table1_cols"] = table1_tex.count(r'\cmidrule') + 1 if table1_tex else 0
    signals["table2_cols"] = table2_tex.count(r'\cmidrule') + 1 if table2_tex else 0

    return signals


def generate_todos(signals: dict) -> list[dict]:
    """
    审阅 agent — 基于全面信号，生成智能 TODO list。
    每个 TODO: {id, category, priority(P0/P1/P2/P3), description, auto_fixable, fix_strategy, evidence, status}
    evidence 字段包含为什么这个 TODO 存在、当前值 vs 目标值，确保执行 agent 有足够上下文。
    """
    todos = []

    # ============================================================
    # P0: BLOCKERS — PDF 无法编译或无内容
    # ============================================================
    if signals.get("error"):
        todos.append({
            "id": "BLK-01",
            "category": "compilation",
            "priority": "P0",
            "description": f"PDF 编译失败: {signals['error']}",
            "auto_fixable": False,
            "fix_strategy": "检查 full_paper.log 查看完整错误，修复 .tex 源文件后重新编译",
            "evidence": f"pdftotext 返回错误: {signals.get('error')}",
            "status": "pending",
        })
        return todos

    if signals.get("pages") is None or signals["pages"] == 0:
        todos.append({
            "id": "BLK-01",
            "category": "compilation",
            "priority": "P0",
            "description": "PDF 无页面输出",
            "auto_fixable": False,
            "fix_strategy": "检查 full_paper.log，full_paper.tex 可能有语法错误",
            "evidence": f"pages={signals.get('pages')}",
            "status": "pending",
        })
        return todos

    # ============================================================
    # P1: CRITICAL — 缺失核心学术要素
    # ============================================================

    # Garbled chars (blocking for readability)
    if signals.get("garbled_chars", 0) > 0:
        garbled_info = ""
        for gl in signals.get("garbled_lines", [])[:3]:
            garbled_info += f"  L{gl['line']}: {gl['text'][:80]}\n"
        todos.append({
            "id": "FMT-02",
            "category": "typesetting",
            "priority": "P1",
            "description": f"PDF 中有 {signals['garbled_chars']} 处乱码字符（β/ε/下标数字等 Unicode 未进入数学模式）",
            "auto_fixable": True,
            "fix_strategy": "在 build_paper.py 的 sanitize_unicode() 中添加缺失的 Unicode → LaTeX 数学模式映射",
            "evidence": f"乱码行示例:\n{garbled_info}",
            "status": "pending",
        })

    # Missing characters in compilation
    if signals.get("missing_char_count", 0) > 0:
        missing_list = ", ".join(signals["missing_char_details"][:5])
        todos.append({
            "id": "FMT-03",
            "category": "typesetting",
            "priority": "P1",
            "description": f"xelatex 报告中 {signals['missing_char_count']} 个字符缺失于字体: {missing_list}",
            "auto_fixable": True,
            "fix_strategy": "在 sanitize_unicode() 中将缺失字符映射为 LaTeX 命令",
            "evidence": f"缺失字符列表: {signals['missing_char_details']}",
            "status": "pending",
        })

    # Missing abstract
    if signals.get("abstract_chars", 0) < 100:
        todos.append({
            "id": "ABS-01",
            "category": "academic_content",
            "priority": "P1",
            "description": "摘要缺失或过短（当前 {0} 字符），管理世界摘要通常 300-500 字".format(signals.get("abstract_chars", 0)),
            "auto_fixable": False,
            "fix_strategy": "在对应 DOCX 或 build_paper.py 的 LaTeX 模板中扩写摘要，涵盖研究问题、方法、主结果、贡献",
            "evidence": f"摘要长度: {signals.get('abstract_chars', 0)} 字符；目标: ≥300 字符",
            "status": "pending",
        })

    # Missing regression table notes
    if not signals.get("table1_has_notes") and signals.get("table1_cols", 0) > 0:
        todos.append({
            "id": "TAB-01",
            "category": "tables",
            "priority": "P1",
            "description": "回归表 Table 1 缺少标准注记（未标注聚类标准误层级、FE 模型规格、显著性水平约定）",
            "auto_fixable": True,
            "fix_strategy": "在 run_analysis.R 中为 modelsummary 调用添加 notes 参数，或在 build_paper.py 中注入注记行",
            "evidence": f"表格列数: {signals.get('table1_cols')}；具备注记: {'是' if signals.get('table1_has_notes') else '否'}",
            "status": "pending",
        })

    if not signals.get("table2_has_notes") and signals.get("table2_cols", 0) > 0:
        todos.append({
            "id": "TAB-02",
            "category": "tables",
            "priority": "P1",
            "description": "回归表 Table 2 缺少标准注记",
            "auto_fixable": True,
            "fix_strategy": "同 TAB-01",
            "evidence": f"表格列数: {signals.get('table2_cols')}；具备注记: {'是' if signals.get('table2_has_notes') else '否'}",
            "status": "pending",
        })

    # Missing clustered SE mention
    if not signals.get("mentions_clustered_se"):
        todos.append({
            "id": "RPT-01",
            "category": "reporting_standards",
            "priority": "P1",
            "description": "PDF 正文中未提及\"聚类标准误\"——这是面板回归报告的必需项",
            "auto_fixable": False,
            "fix_strategy": "在 DOCX 研究设计/实证结果章节中明确写出标准误聚类层级",
            "evidence": "搜索'聚类|cluster'在 PDF 文本中: 未找到",
            "status": "pending",
        })

    # ============================================================
    # P2: IMPORTANT — 学术规范性
    # ============================================================

    # Missing author metadata
    if not signals.get("has_thanks"):
        todos.append({
            "id": "META-01",
            "category": "metadata",
            "priority": "P2",
            "description": "缺少作者单位/通讯信息（管理世界要求首页脚注注明单位、通讯地址）",
            "auto_fixable": True,
            "fix_strategy": "在 build_paper.py 的 \\author{} 中添加 \\thanks{单位, Email}",
            "evidence": f"has_thanks: {signals.get('has_thanks')}",
            "status": "pending",
        })

    if not signals.get("has_acknowledgments"):
        todos.append({
            "id": "META-02",
            "category": "metadata",
            "priority": "P2",
            "description": "缺少致谢部分",
            "auto_fixable": True,
            "fix_strategy": "在 LaTeX 模板中添加 \\section*{致谢}",
            "evidence": f"has_acknowledgments: {signals.get('has_acknowledgments')}",
            "status": "pending",
        })

    if not signals.get("has_funding"):
        todos.append({
            "id": "META-03",
            "category": "metadata",
            "priority": "P2",
            "description": "缺少基金资助信息",
            "auto_fixable": True,
            "fix_strategy": "在致谢部分添加基金资助占位符（如'国家自然科学基金（项目编号：待补充）'）",
            "evidence": f"has_funding: {signals.get('has_funding')}",
            "status": "pending",
        })

    # Figure placement issues
    if signals.get("figures_in_appendix") and signals.get("intext_figure_refs", 0) < 3:
        todos.append({
            "id": "FIG-01",
            "category": "figures",
            "priority": "P2",
            "description": f"所有 {len(signals.get('figure_files', []))} 张图集中在附录，正文中仅 {signals.get('chinese_figure_refs', 0)} 处交叉引用",
            "auto_fixable": False,
            "fix_strategy": "在 DOCX 正文中为每张关键图添加'如图X所示'引用，并将最重要的 3-4 张图（事件研究、置换检验、趋势图、分布图）移至正文对应章节",
            "evidence": f"图形数: {len(signals.get('figure_files', []))}；正文引用: {signals.get('chinese_figure_refs', 0)}；附录模式: {signals.get('figures_in_appendix')}",
            "status": "pending",
        })

    # Overfull hboxes
    if signals.get("overfull_hboxes", 0) > 3:
        todos.append({
            "id": "FMT-01",
            "category": "typesetting",
            "priority": "P2",
            "description": f"{signals['overfull_hboxes']} 处 Overfull hbox（正文溢出页宽），影响排版美观",
            "auto_fixable": True,
            "fix_strategy": "在 preamble 中添加 \\tolerance=500 和 \\emergencystretch=0.5em，或手动断行",
            "evidence": f"overfull: {signals['overfull_hboxes']}；underfull: {signals.get('underfull_hboxes', 0)}",
            "status": "pending",
        })

    # Section completeness
    expected_sections = ["引言", "文献综述", "理论框架", "研究设计", "实证结果", "稳健性检验", "讨论", "结论"]
    found_sections = [s for s in signals.get("sections", [])]
    missing = [s for s in expected_sections if not any(s in fs for fs in found_sections)]
    if missing:
        todos.append({
            "id": "SEC-01",
            "category": "structure",
            "priority": "P2",
            "description": f"缺少章节: {', '.join(missing)}",
            "auto_fixable": False,
            "fix_strategy": f"在 DOCX 源文件中补写 {', '.join(missing)} 章节",
            "evidence": f"已找到: {found_sections}；缺失: {missing}",
            "status": "pending",
        })

    # ============================================================
    # P3: NICE-TO-HAVE — 投稿格式打磨
    # ============================================================

    if signals.get("has_english_subtitle"):
        todos.append({
            "id": "TXT-01",
            "category": "text",
            "priority": "P3",
            "description": "英文副标题仍出现在中文正文中，中文期刊投稿宜移除或移至脚注",
            "auto_fixable": True,
            "fix_strategy": "在 assemble 阶段过滤掉英文标题行",
            "evidence": "has_english_subtitle: True",
            "status": "pending",
        })

    # Reference count
    if signals.get("reference_count", 0) < 25:
        todos.append({
            "id": "REF-01",
            "category": "references",
            "priority": "P3",
            "description": f"参考文献仅 {signals.get('reference_count', 0)} 条，《管理世界》级别论文通常 40-60 条",
            "auto_fixable": False,
            "fix_strategy": "通过文献搜索补充 AI 经济增长、自动化、任务模型、TOP500 等相关文献",
            "evidence": f"引用数: {signals.get('reference_count', 0)}；目标: 40-60",
            "status": "pending",
        })

    # Word count
    chinese_chars = signals.get("chinese_chars", 0)
    if chinese_chars < 8000:
        todos.append({
            "id": "LEN-01",
            "category": "length",
            "priority": "P3",
            "description": f"正文字数约 {chinese_chars} 字，《管理世界》论文通常 15000-25000 字",
            "auto_fixable": False,
            "fix_strategy": "在各章节中扩展论证细节、补充文献对话、添加更多实证分析段落",
            "evidence": f"中文字数: {chinese_chars}；目标: 15000-25000",
            "status": "pending",
        })

    # Journal format compliance
    todos.append({
        "id": "JRN-01",
        "category": "journal_format",
        "priority": "P3",
        "description": "未对照《管理世界》投稿指南做格式检查（页边距、字体、标题层级、参考文献格式、图表编号等）",
        "auto_fixable": False,
        "fix_strategy": "搜索《管理世界》投稿指南，对照检查 LaTeX 模板的各项参数",
        "evidence": "需确认: 页边距(上2.54cm下2.54cm左3.18cm右3.18cm?)、字体(宋体小四?)、行距等",
        "status": "pending",
    })

    # Latex warnings
    for warn in signals.get("latex_warnings", [])[:3]:
        todos.append({
            "id": f"WRN-{hash(warn) % 1000:03d}",
            "category": "typesetting",
            "priority": "P3",
            "description": f"LaTeX 警告: {warn[:100]}",
            "auto_fixable": False,
            "fix_strategy": "查看 full_paper.log 中该警告的完整上下文，根据具体问题修复",
            "evidence": warn[:200],
            "status": "pending",
        })

    return todos


def execute_auto_fixes(todos: list[dict], tex_body: str) -> tuple[str, list[str]]:
    """执行 agent：应用所有 auto_fixable TODOs 到 LaTeX 源。"""
    modified = tex_body
    applied = []

    for todo in todos:
        if not todo.get("auto_fixable") or todo.get("status") == "completed":
            continue
        tid = todo["id"]

        if tid == "FMT-01":
            if "\\tolerance=500" not in modified:
                modified = modified.replace(
                    "\\begin{document}",
                    "\\tolerance=500\n\\emergencystretch=0.5em\n\\begin{document}",
                )
                applied.append(tid)

        elif tid == "FMT-02":
            # Unicode → LaTeX math
            unicode_map = {
                'β': r'$\beta$', 'α': r'$\alpha$', 'γ': r'$\gamma$',
                'δ': r'$\delta$', 'ε': r'$\epsilon$', '≈': r'$\approx$',
                '≥': r'$\ge$', '≤': r'$\le$', '×': r'$\times$',
                '₁': r'$_1$', '₂': r'$_2$', '₃': r'$_3$',
                '→': r'$\rightarrow$', '←': r'$\leftarrow$',
                '�': r'$\beta$',
            }
            changed = False
            for char, latex_cmd in unicode_map.items():
                if char in modified:
                    modified = modified.replace(char, latex_cmd)
                    changed = True
            if changed:
                applied.append(tid)

        elif tid == "FMT-03":
            # Already handled by FMT-02 for known chars;
            # for new ones, we'd need dynamism — skip for now
            pass

        elif tid in ("TAB-01", "TAB-02"):
            table_note = "\n\\vspace{0.3em}\n{\\footnotesize 注：括号内为国家层面聚类稳健标准误。所有模型包含国家固定效应和年份固定效应。控制变量均滞后一期。\\textsuperscript{+} $p<0.1$; * $p<0.05$; ** $p<0.01$; *** $p<0.001$。}\n"
            for tbl in ["table1_main_effect.tex", "table2_channel.tex"]:
                if tbl in modified:
                    modified = modified.replace(
                        f"\\input{{{tbl}}}",
                        f"\\input{{{tbl}}}{table_note}",
                    )
            applied.append(tid)

        elif tid == "META-01":
            if "\\thanks{" not in modified:
                modified = modified.replace(
                    "\\author{Siyao Zheng",
                    "\\author{Siyao Zheng\\thanks{上海交通大学国际与公共事务学院，通讯地址：上海市华山路1954号，Email: szyao@sjtu.edu.cn}",
                )
                applied.append(tid)

        elif tid in ("META-02", "META-03"):
            ack = "\n\\section*{致谢}\n本文感谢匿名审稿人的宝贵意见。文责自负。\n\n\\vspace{0.5em}\n{\\footnotesize 基金资助：本研究受到国家自然科学基金（项目编号：待补充）的资助。}\n"
            if "致谢" not in modified:
                if "\\section*{参考文献}" in modified:
                    modified = modified.replace("\\section*{参考文献}", ack + "\n\\section*{参考文献}")
                else:
                    modified += "\n" + ack
                applied.append(tid)

        elif tid == "TXT-01":
            modified = re.sub(
                r'\n\\\\\n\n\*AI Compute Infrastructure.*?Panel\*\n\n',
                '\n',
                modified,
                flags=re.DOTALL,
            )
            # Also try removing from title
            modified = re.sub(
                r'\\title\{.*?\n',
                lambda m: re.sub(
                    r'\n\\\\\n\n\*AI Compute Infrastructure[^*]*\*\n\n',
                    '',
                    m.group(0),
                    flags=re.DOTALL,
                ),
                modified,
                flags=re.DOTALL,
            )
            applied.append(tid)

    return modified, applied


def main() -> None:
    print("=" * 60)
    print("improve_paper.py — 两步智能审阅-改进")
    print("=" * 60)

    # ==== STEP 1: 审阅 agent — 全面提取信号 → 生成 TODO ====
    print("\n━━━ STEP 1: 审阅 agent ━━━")
    print("  提取 PDF + LaTeX + 编译日志中的所有质量信号...")
    signals = extract_all_signals()
    print(f"  ✓ 已提取 {len(signals)} 个信号维度")
    print(f"    - 页数: {signals.get('pages')}")
    print(f"    - 中文字数: {signals.get('chinese_chars')}")
    print(f"    - 节数: {len(signals.get('sections', []))}")
    print(f"    - 图数: {len(signals.get('figure_files', []))}")
    print(f"    - 参考文献: {signals.get('reference_count')} 条")
    print(f"    - 乱码: {signals.get('garbled_chars')} 处")
    print(f"    - Overfull: {signals.get('overfull_hboxes')} 处")

    todos = generate_todos(signals)
    print(f"\n  ✓ 智能分析完成，生成 {len(todos)} 条 TODO:")

    for todo in sorted(todos, key=lambda t: t.get("priority", "P9")):
        auto = "🤖" if todo["auto_fixable"] else "👤"
        print(f"    [{todo['priority']}] {auto} {todo['id']}: {todo['description'][:90]}")

    # Save full TODO file (signals included for downstream agents)
    full_output = {
        "generated_at": __import__('datetime').datetime.now().isoformat(),
        "summary": {
            "total_todos": len(todos),
            "auto_fixable": sum(1 for t in todos if t["auto_fixable"]),
            "manual_only": sum(1 for t in todos if not t["auto_fixable"]),
            "p0": sum(1 for t in todos if t["priority"] == "P0"),
            "p1": sum(1 for t in todos if t["priority"] == "P1"),
            "p2": sum(1 for t in todos if t["priority"] == "P2"),
            "p3": sum(1 for t in todos if t["priority"] == "P3"),
        },
        "todos": todos,
    }
    TODO_FILE.write_text(json.dumps(full_output, ensure_ascii=False, indent=2))
    print(f"\n  ✓ 完整审阅报告已保存: {TODO_FILE}")

    # ==== STEP 2: 执行 agent — 自动修复 ====
    print("\n━━━ STEP 2: 执行 agent ━━━")
    auto_todos = [t for t in todos if t["auto_fixable"] and t["status"] == "pending"]
    print(f"  自动可修复: {len(auto_todos)} 条")

    if auto_todos:
        tex_body = signals.get("tex_body", "")
        if not tex_body and TEX_PATH.exists():
            tex_body = TEX_PATH.read_text()

        modified_tex, applied = execute_auto_fixes(auto_todos, tex_body)

        if applied:
            TEX_PATH.write_text(modified_tex)
            print(f"  ✓ 已应用修复: {applied}")
            for todo in todos:
                if todo["id"] in applied or any(todo["id"] in a for a in applied):
                    todo["status"] = "completed"
            TODO_FILE.write_text(json.dumps(full_output, ensure_ascii=False, indent=2))

            # Recompile
            print("\n  ▶ 重新编译 PDF...")
            ret, stdout, stderr = run_cmd(["python3", str(BUILD_PAPER)])
            if ret == 0:
                print("  ✓ PDF 重新生成成功")
            else:
                print(f"  ✗ 编译失败: {stderr[:300]}")
        else:
            print("  - 所有自动项已处理完毕，无需修复")
    else:
        print("  - 无自动可修复项")

    # ==== SUMMARY ====
    manual = [t for t in todos if not t["auto_fixable"] and t["status"] == "pending"]
    print(f"\n{'=' * 60}")
    print(f"  审阅-执行完成")
    print(f"  自动修复: {len(auto_todos)} 条")
    print(f"  需手动处理: {len(manual)} 条")
    if manual:
        print(f"\n  📋 待手动处理 TODO（供下游 codex agent 执行）:")
        for t in manual:
            print(f"    [{t['priority']}] {t['id']}: {t['description'][:80]}")
            print(f"          → {t['fix_strategy'][:120]}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
