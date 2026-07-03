from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> None:
    print("$", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    python = sys.executable
    run([python, "scripts/download_data.py"])
    run([python, "scripts/build_panels.py"])
    run([python, "scripts/validate_outputs.py"])


if __name__ == "__main__":
    main()
