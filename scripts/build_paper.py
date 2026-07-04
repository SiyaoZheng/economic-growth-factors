#!/usr/bin/env python3
"""
build_paper.py — 一键生成全文 PDF
1. 合并所有 DOCX 章节 → 单一大 Markdown 文件
2. 将 LaTeX 表格转换为 Markdown 表格
3. 将图形引用嵌入 Markdown
4. 用 pandoc + xelatex 编译为 PDF
"""

from __future__ import annotations

import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD_DIR = ROOT / "outputs" / "writing" / "writing_scaffold"
TABLES_DIR = ROOT / "outputs" / "writing"
FIGURES_DIR = ROOT / "outputs" / "writing" / "paper_figures"
OUTDIR = ROOT / "outputs" / "writing"
TEMPLATE_DIR = ROOT / "outputs" / "writing"

CHAPTER_ORDER = [
    "完整正文_引言.docx",
    "完整正文_文献综述.docx",
    "完整正文_理论框架.docx",
    "完整正文_研究设计.docx",
    "完整正文_实证结果.docx",
    "完整正文_稳健性讨论结论.docx",
]

# Map figure filenames to their LaTeX labels and captions
FIGURE_MAP = {
    "compute_distribution.png": {
        "label": "fig:compute_dist",
        "caption": r"TOP500 总算力分布（log Rmax），1993–2025 年",
    },
    "treatment_heatmap.png": {
        "label": "fig:heatmap",
        "caption": r"各国算力覆盖率热力图，2015–2023 年",
    },
    "raw_trends.png": {
        "label": "fig:raw_trends",
        "caption": r"高算力组与低算力组 GDP 增长率原始趋势",
    },
    "pretrend_diagnostic.png": {
        "label": "fig:pretrend",
        "caption": r"处理前趋势诊断（pretrend diagnostic）",
    },
    "event_study_twfe.png": {
        "label": "fig:event_study",
        "caption": r"双向固定效应事件研究图",
    },
    "placebo_randomization.png": {
        "label": "fig:placebo_rand",
        "caption": r"随机置换检验（randomization inference）",
    },
    "placebo_continuous.png": {
        "label": "fig:placebo_cont",
        "caption": r"连续处理剂量的安慰剂检验",
    },
    "coef_stability.png": {
        "label": "fig:coef_stab",
        "caption": r"系数稳定性检验（排除单个国家逐一回归）",
    },
}

# Table insertion markers in the DOCX text
TABLE_MARKERS = [
    ("表 1 报告了主要变量的描述性统计。", "\\input{table1_main_effect.tex}"),
    ("表 2 报告了基准回归结果。", "\\input{table2_channel.tex}"),
]


def run_cmd(args: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(args, cwd=cwd or ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ CMD FAILED: {' '.join(args)}")
        print(f"  stderr: {result.stderr[:500]}")
        sys.exit(1)
    return result.stdout


def docx_to_latex(docx_path: Path) -> str:
    """Convert a single DOCX to LaTeX body text using pandoc."""
    tmp_tex = Path("/tmp/_paper_chunk.tex")
    run_cmd([
        "pandoc", str(docx_path),
        "-f", "docx",
        "-t", "latex",
        "-o", str(tmp_tex),
        "--wrap=none",
        "--top-level-division=section",
    ])
    text = tmp_tex.read_text()

    # Strip the pandoc wrapper: remove \section*{References} if it's a standalone ref section
    # Also remove the auto-generated title/author blocks (pandoc may extract them)
    # The first few lines may contain \title{}, \author{}, \date{} — strip them
    text = re.sub(r'\\title\{.*?\}', '', text, flags=re.DOTALL)
    text = re.sub(r'\\author\{.*?\}', '', text, flags=re.DOTALL)
    text = re.sub(r'\\date\{.*?\}', '', text, flags=re.DOTALL)
    text = re.sub(r'\\maketitle', '', text)

    return text.strip()



def sanitize_unicode(tex: str) -> str:
    """Replace unicode symbols that xelatex can't render with LaTeX math commands."""
    replacements = {
        'β': r'$\beta$', 'α': r'$\alpha$', 'γ': r'$\gamma$',
        'δ': r'$\delta$', 'ε': r'$\epsilon$', '≈': r'$\approx$',
        '≥': r'$\ge$', '≤': r'$\le$', '×': r'$\times$',
        '₁': r'$_1$', '₂': r'$_2$', '₃': r'$_3$',
        '→': r'$\rightarrow$', '←': r'$\leftarrow$',
    }
    for char, latex_cmd in replacements.items():
        tex = tex.replace(char, latex_cmd)
    return tex


def assemble_latex_body() -> str:
    """Merge all DOCX chapters into one LaTeX body, with figures and tables injected."""
    # First, gather all chapter texts
    chapters: list[str] = []
    chapter_sources: list[str] = []

    for ch_name in CHAPTER_ORDER:
        ch_path = SCAFFOLD_DIR / ch_name
        if not ch_path.exists():
            print(f"  ⚠ Missing chapter: {ch_name}, skipping")
            continue
        latex = docx_to_latex(ch_path)
        # Inject tables at marker positions
        for marker_text, table_cmd in TABLE_MARKERS:
            if marker_text in latex:
                latex = latex.replace(marker_text, marker_text + "\n\n" + table_cmd + "\n")
        chapters.append(latex)
        chapter_sources.append(ch_name)

    body = "\n\n\\clearpage\n\n".join(chapters)

    # After assembling, also inject figures as a \section* if they exist
    # Actually, figures should be placed near their references. For now, add a
    # "附录：图形" section at the end with all figures.
    existing_figures = sorted([f for f in FIGURES_DIR.glob("*.png") if f.name in FIGURE_MAP])
    if existing_figures:
        body += "\n\n\\clearpage\n\\section*{附录：图形}\n\n"
        for fig_path in existing_figures:
            info = FIGURE_MAP.get(fig_path.name, {})
            label = info.get("label", fig_path.stem)
            caption = info.get("caption", fig_path.stem)
            rel_path = f"paper_figures/{fig_path.name}"
            body += f"""
\\begin{{figure}}[htbp]
\\centering
\\includegraphics[width=0.85\\textwidth]{{{rel_path}}}
\\caption{{{caption}}}
\\label{{{label}}}
\\end{{figure}}

"""

    return body


def generate_tex_full(latex_body: str, template_path: str | None = None) -> str:
    """Wrap the body in a full LaTeX document with Chinese-capable preamble."""
    # Chinese font setup: use available system fonts
    preamble = r"""
\documentclass[12pt,a4paper]{ctexart}

% Page layout
\usepackage[top=2.5cm, bottom=2.5cm, left=3cm, right=3cm]{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{caption}
\usepackage{float}
\usepackage{hyperref}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{longtable}
\usepackage{array}

\hypersetup{
  colorlinks=true,
  linkcolor=blue,
  citecolor=blue,
  urlcolor=blue,
}

% Chinese font setup
\setCJKmainfont{Songti SC}[
  BoldFont=Songti SC Bold,
  ItalicFont=Kaiti SC,
]
\setCJKsansfont{Heiti SC}
\setCJKmonofont{STFangsong}

% Title info
\title{\textbf{人工智能算力基础设施与经济增长：\\基于跨国面板的初步证据}}
\author{Siyao Zheng\thanks{上海交通大学国际与公共事务学院}}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
\noindent 本文利用 TOP500 全球超级计算机排名数据构建 1993--2025 年国家层面 AI 算力基础设施面板，并与 Penn World Table 11.0 的经济增长数据合并，实证检验国家 AI 算力规模与经济增长之间的关联。在 185 个国家 2015--2023 年的分析样本中，使用双向固定效应模型（国家 + 年份）发现，log 总算力与年度 GDP 增长率之间存在稳健的负向条件关联（$\beta = -0.062$，SE $= 0.033$，$p = 0.066$）。这一负向关联在加权最小二乘、无极端样本、排除中国及排除 OECD 高收入国家等多个稳健性检验下保持一致，并在 2000 次随机置换检验中拒绝零效应的零假设（$p = 0.001$）。本文进一步通过交互项分析探讨 Acemoglu--Restrepo 任务模型框架下的自动化替代渠道和新任务创造渠道，发现负向关联在工业化程度较低的国家中更加显著——这一模式与自动化替代假说一致。本文严格将发现定性为"条件关联"而非因果效应，并明确指出研究设计在反向因果、时变混淆和测量误差方面的局限。

\vspace{1em}
\noindent \textbf{关键词：} 人工智能；算力基础设施；经济增长；TOP500；跨国面板；任务模型
\end{abstract}

\newpage
\tableofcontents
\newpage
"""

    latex_body = sanitize_unicode(latex_body)
    full_tex = preamble + "\n" + latex_body + "\n\n\\end{document}\n"

    # Write to disk
    tex_path = OUTDIR / "full_paper.tex"
    tex_path.write_text(full_tex)
    print(f"  ✓ LaTeX written: {tex_path} ({len(full_tex)} chars)")
    return str(tex_path)


def compile_pdf(tex_path: str) -> str:
    """Run xelatex twice to resolve cross-refs."""
    tex_dir = Path(tex_path).parent
    job_name = Path(tex_path).stem

    for run in [1, 2]:
        print(f"  ▶ xelatex run {run}...")
        run_cmd([
            "xelatex",
            "-interaction=nonstopmode",
            "-output-directory", str(tex_dir),
            tex_path,
        ], cwd=tex_dir)

    pdf_path = tex_dir / f"{job_name}.pdf"
    if pdf_path.exists():
        print(f"  ✓ PDF generated: {pdf_path}")
        return str(pdf_path)
    else:
        print(f"  ✗ PDF not found at {pdf_path}")
        sys.exit(1)


def main() -> None:
    print("=" * 60)
    print("build_paper.py — 生成全文 PDF")
    print("=" * 60)

    # Step 1: Assemble body
    print("\n[1/3] Assembling chapters from DOCX...")
    body = assemble_latex_body()

    # Step 2: Generate full .tex
    print("\n[2/3] Generating full LaTeX...")
    tex_path = generate_tex_full(body)

    # Step 3: Compile
    print("\n[3/3] Compiling PDF with xelatex...")
    pdf_path = compile_pdf(tex_path)

    print(f"\n{'=' * 60}")
    print(f"✓ 全文 PDF 已生成: {pdf_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
