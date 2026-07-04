from __future__ import annotations

import subprocess
import sys
import time
from argparse import ArgumentParser
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def run_cmd(args: list[str], label: str = "") -> tuple[bool, float]:
    tag = f"  [{label}]" if label else ""
    print(f"\n{'='*60}")
    print(f"▶{tag} {' '.join(args)}")
    print(f"{'='*60}")
    start = time.time()
    try:
        subprocess.run(args, cwd=ROOT, check=True)
        elapsed = time.time() - start
        print(f"✓{tag} done ({elapsed:.1f}s)")
        return True, elapsed
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start
        print(f"✗{tag} FAILED (exit {e.returncode}, {elapsed:.1f}s)")
        return False, elapsed


def main() -> None:
    parser = ArgumentParser(description="一键运行经济增长因素研究完整分析管线")
    parser.add_argument("--download", action="store_true", help="包含数据下载步骤")
    parser.add_argument("--data-only", action="store_true", help="仅运行数据管线")
    parser.add_argument("--table-only", action="store_true", help="仅运行回归表格")
    parser.add_argument("--did-only", action="store_true", help="仅运行 DID 诊断")
    parser.add_argument("--paper", action="store_true", help="生成全文 PDF（需先运行数据管线）")
    parser.add_argument("--improve", action="store_true", help="审阅 PDF → 自动修复 → 重新编译（循环直到无改进）")
    parser.add_argument("--full", action="store_true", help="完整一键：下载 → 建面板 → 回归 → DID → PDF → 审阅改进")
    args = parser.parse_args()

    python = sys.executable
    rscript = "Rscript"
    results: list[tuple[str, bool, float]] = []
    t0 = time.time()

    # --full 模式：从头到尾
    if args.full:
        args.download = True
        args.paper = True
        args.improve = True

    # --- 数据管线 ---
    if not args.table_only and not args.did_only and not args.paper:
        if args.download:
            ok, t = run_cmd([python, "scripts/download_data.py"], "download")
            results.append(("download_data.py", ok, t))
            if not ok:
                sys.exit(1)

        ok, t = run_cmd([python, "scripts/fix_data_quality.py"], "fix data quality")
        results.append(("fix_data_quality.py", ok, t))

        ok, t = run_cmd([python, "scripts/build_panels.py"], "build panels")
        results.append(("build_panels.py", ok, t))
        if not ok:
            sys.exit(1)

        ok, t = run_cmd([python, "scripts/validate_outputs.py"], "validate")
        results.append(("validate_outputs.py", ok, t))

    if args.data_only and not args.paper:
        print_summary(results, time.time() - t0)
        return

    # --- 回归表格 ---
    if not args.did_only and not args.paper:
        ok, t = run_cmd([rscript, "scripts/run_analysis.R"], "regression tables")
        results.append(("run_analysis.R", ok, t))

    # --- DID 诊断 ---
    if not args.table_only and not args.paper:
        ok, t = run_cmd([rscript, "scripts/run_did_diagnostics.R"], "DID diagnostics")
        results.append(("run_did_diagnostics.R", ok, t))

    # --- 生成全文 PDF ---
    if args.paper:
        ok, t = run_cmd([python, "scripts/build_paper.py"], "build paper PDF")
        results.append(("build_paper.py", ok, t))

        # --- 审阅 → 自动修复 → 重新编译（循环） ---
        if args.improve:
            max_rounds = 3
            prev_todo_count = None
            for round_num in range(1, max_rounds + 1):
                print(f"\n{'#'*60}")
                print(f"#  审阅-改进循环 第 {round_num}/{max_rounds} 轮")
                print(f"{'#'*60}")
                ok, t = run_cmd([python, "scripts/improve_paper.py"], f"improve round {round_num}")
                results.append((f"improve_paper.py (round {round_num})", ok, t))
                if not ok:
                    break
                # Check if any auto-fixable TODOs remain
                todo_file = ROOT / "outputs" / "writing" / "improvement_todos.json"
                if todo_file.exists():
                    todo_data = json.loads(todo_file.read_text())
                    todos = todo_data.get("todos", todo_data)  # handle both old and new format
                    auto_pending = [t for t in todos if isinstance(t, dict) and t.get("auto_fixable") and t.get("status") == "pending"]
                    if not auto_pending:
                        print(f"  ✓ 无可自动修复项，停止循环")
                        break
                    if prev_todo_count == len(auto_pending):
                        print(f"  ⚠ 待修复项未减少 ({len(auto_pending)})，停止循环")
                        break
                    prev_todo_count = len(auto_pending)

    print_summary(results, time.time() - t0)


def print_summary(results: list[tuple[str, bool, float]], total_time: float) -> None:
    ok_count = sum(1 for _, ok, _ in results if ok)
    fail_count = sum(1 for _, ok, _ in results if not ok)
    print(f"\n{'='*60}")
    print(f"✓ 全部完成：{ok_count}/{len(results)} 步骤成功，总耗时 {total_time:.1f}s")
    if fail_count > 0:
        print(f"✗ {fail_count} 个步骤失败")
    else:
        pdf_path = ROOT / "outputs" / "writing" / "full_paper.pdf"
        if pdf_path.exists():
            print(f"  📄 全文 PDF: outputs/writing/full_paper.pdf")
        todo_file = ROOT / "outputs" / "writing" / "improvement_todos.json"
        if todo_file.exists():
            print(f"  📋 改进 TODO: outputs/writing/improvement_todos.json")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
