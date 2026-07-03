#!/usr/bin/env python3
"""Guarded automatic Git snapshots for this repository."""

from __future__ import annotations

import fcntl
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.8+ has zoneinfo.
    ZoneInfo = None


REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = REPO_ROOT / ".git" / "autosnapshot"
LOG_FILE = LOG_DIR / "events.jsonl"
LOCK_FILE = LOG_DIR / "autosnapshot.lock"

DEFAULT_REMOTE = "origin"
DEFAULT_MAX_FILE_MB = 50
PROTECTED_DATA_PREFIXES = ("data/raw/", "data/interim/", "data/processed/")
FORBIDDEN_BASENAMES = {
    ".env",
    ".env.local",
    ".netrc",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
}
FORBIDDEN_SUFFIXES = (
    ".key",
    ".pem",
    ".p12",
    ".pfx",
    ".mobileprovision",
)
SECRET_MARKERS = (
    "-----BEGIN " + "PRIVATE KEY-----",
    "-----BEGIN RSA " + "PRIVATE KEY-----",
    "OPENAI_" + "API_KEY=",
    "ANTHROPIC_" + "API_KEY=",
    "LINEAR_" + "API_KEY=",
    "gh" + "p_",
    "gh" + "o_",
    "github_" + "pat_",
)


class GitError(RuntimeError):
    def __init__(self, args: list[str], returncode: int, stdout: str, stderr: str) -> None:
        self.args_list = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(f"{' '.join(args)} failed with exit code {returncode}")


def run_git(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        raise GitError(["git", *args], result.returncode, result.stdout, result.stderr)
    return result


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def now_local_for_message() -> str:
    if ZoneInfo is None:
        return datetime.now().strftime("%Y-%m-%d %H:%M")
    return datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M")


def log_event(status: str, **fields: object) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    event = {"timestamp": now_utc(), "status": status, **fields}
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def current_branch() -> str:
    return run_git(["branch", "--show-current"]).stdout.strip()


def branch_remote(branch: str) -> str:
    configured = run_git(["config", "--get", f"branch.{branch}.remote"], check=False)
    if configured.returncode == 0 and configured.stdout.strip():
        return configured.stdout.strip()
    origin = run_git(["remote", "get-url", DEFAULT_REMOTE], check=False)
    if origin.returncode == 0:
        return DEFAULT_REMOTE
    return ""


def upstream_ref() -> str:
    result = run_git(
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        check=False,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return ""


def ahead_behind(upstream: str) -> tuple[int, int]:
    result = run_git(["rev-list", "--left-right", "--count", f"HEAD...{upstream}"])
    ahead_text, behind_text = result.stdout.strip().split()[:2]
    return int(ahead_text), int(behind_text)


def has_staged_changes() -> bool:
    result = run_git(["diff", "--cached", "--quiet"], check=False)
    if result.returncode == 0:
        return False
    if result.returncode == 1:
        return True
    raise GitError(["git", "diff", "--cached", "--quiet"], result.returncode, result.stdout, result.stderr)


def has_worktree_changes() -> bool:
    return bool(run_git(["status", "--porcelain=v1"]).stdout.strip())


def unstaged_conflicts() -> list[str]:
    return [line for line in run_git(["diff", "--name-only", "--diff-filter=U"]).stdout.splitlines() if line]


def staged_files() -> list[str]:
    raw = run_git(["diff", "--cached", "--name-only", "-z"]).stdout
    return [item for item in raw.split("\0") if item]


def max_file_bytes() -> int:
    raw = os.environ.get("AUTOGIT_MAX_FILE_MB", str(DEFAULT_MAX_FILE_MB))
    try:
        return int(raw) * 1024 * 1024
    except ValueError:
        return DEFAULT_MAX_FILE_MB * 1024 * 1024


def forbidden_path_reason(path: str) -> str:
    normalized = path.replace("\\", "/")
    lower = normalized.lower()
    basename = Path(normalized).name.lower()
    if (
        normalized.startswith(PROTECTED_DATA_PREFIXES)
        and not normalized.endswith("/.gitkeep")
    ):
        return "generated data directory"
    if basename in FORBIDDEN_BASENAMES:
        return "sensitive filename"
    if lower.endswith(FORBIDDEN_SUFFIXES):
        return "sensitive file extension"
    if "/.ssh/" in lower or lower.startswith(".ssh/"):
        return "ssh material"
    return ""


def staged_file_issues(paths: Iterable[str]) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    limit = max_file_bytes()
    for path in paths:
        reason = forbidden_path_reason(path)
        if reason:
            issues.append({"path": path, "reason": reason})
            continue

        full_path = REPO_ROOT / path
        if not full_path.exists() or not full_path.is_file() or full_path.is_symlink():
            continue

        size = full_path.stat().st_size
        if size > limit:
            issues.append({"path": path, "reason": "file too large", "bytes": size})
            continue

        if size <= 1_000_000:
            try:
                text = full_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            marker = next((item for item in SECRET_MARKERS if item in text), "")
            if marker:
                issues.append({"path": path, "reason": "secret-like content marker"})
    return issues


def reset_index_after_autostage() -> None:
    run_git(["reset", "--mixed", "--quiet"], check=False)


def push_current_branch(branch: str, upstream: str) -> tuple[bool, str]:
    if os.environ.get("AUTOGIT_PUSH", "1").lower() in {"0", "false", "no"}:
        return False, "push disabled by AUTOGIT_PUSH"

    if upstream:
        result = run_git(["push", "--quiet"], check=False)
    else:
        result = run_git(["push", "--set-upstream", DEFAULT_REMOTE, branch], check=False)

    if result.returncode == 0:
        return True, ""
    return False, (result.stderr or result.stdout).strip()


def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with LOCK_FILE.open("w", encoding="utf-8") as lock_handle:
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            log_event("skipped", reason="another autosnapshot is already running")
            return 0

        try:
            run_git(["rev-parse", "--is-inside-work-tree"])
            branch = current_branch()
            if not branch:
                log_event("blocked", reason="detached HEAD")
                return 2

            conflicts = unstaged_conflicts()
            if conflicts:
                log_event("blocked", reason="merge conflicts", files=conflicts)
                return 2

            remote = branch_remote(branch)
            upstream = upstream_ref()
            fetch_error = ""
            if remote:
                fetch = run_git(["fetch", "--quiet", "--prune", remote], check=False)
                if fetch.returncode != 0:
                    fetch_error = (fetch.stderr or fetch.stdout).strip()

            ahead = behind = 0
            if upstream and not fetch_error:
                ahead, behind = ahead_behind(upstream)
                if behind:
                    log_event(
                        "blocked",
                        reason="remote branch is ahead",
                        branch=branch,
                        upstream=upstream,
                        ahead=ahead,
                        behind=behind,
                    )
                    return 2

            if not has_worktree_changes():
                if ahead:
                    pushed, push_error = push_current_branch(branch, upstream)
                    log_event(
                        "pushed" if pushed else "push_failed",
                        reason="" if pushed else push_error,
                        branch=branch,
                        upstream=upstream,
                        ahead=ahead,
                    )
                    return 0 if pushed else 1
                log_event("noop", reason="clean worktree", branch=branch, upstream=upstream)
                return 0

            if has_staged_changes():
                log_event("blocked", reason="manual staged changes present", branch=branch)
                return 2

            run_git(["add", "-A"])
            if not has_staged_changes():
                log_event("noop", reason="changes are ignored or unstaged by git", branch=branch)
                return 0

            files = staged_files()
            issues = staged_file_issues(files)
            if issues:
                reset_index_after_autostage()
                log_event("blocked", reason="staged file safety check failed", files=issues)
                return 2

            message = os.environ.get("AUTOGIT_MESSAGE") or f"autosnapshot: {now_local_for_message()}"
            commit = run_git(["commit", "-m", message], check=False)
            if commit.returncode != 0:
                reset_index_after_autostage()
                log_event(
                    "commit_failed",
                    branch=branch,
                    reason=(commit.stderr or commit.stdout).strip(),
                    files=files,
                )
                return 1

            commit_hash = run_git(["rev-parse", "--short", "HEAD"]).stdout.strip()
            upstream = upstream_ref()
            pushed, push_error = push_current_branch(branch, upstream)
            log_event(
                "committed_and_pushed" if pushed else "committed_push_failed",
                branch=branch,
                commit=commit_hash,
                files=files,
                push_error=push_error,
                fetch_error=fetch_error,
            )
            return 0 if pushed else 1
        except GitError as exc:
            log_event(
                "git_error",
                command=exc.args_list,
                returncode=exc.returncode,
                stdout=exc.stdout.strip(),
                stderr=exc.stderr.strip(),
            )
            return 1
        except Exception as exc:  # pragma: no cover - top-level logging guard.
            log_event("error", reason=repr(exc))
            return 1


if __name__ == "__main__":
    sys.exit(main())
