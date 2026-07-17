"""Pick the next eligible tasks from a feature's backlog.json.

Replaces the agent's full-file reads of backlog.json with a single small
JSON output. Returns every task whose status is "todo" and whose
dependencies are all "done", so the caller can dispatch independent
subagents in parallel. Read-only.

Usage (run from {project_root}):
    python scripts/next_tasks.py <feature-short-name>

The script resolves `<cwd>/.agents/features/<feature-short-name>/backlog.json`.

Output (stdout, JSON):
    {"next_tasks": [{"id": <int>, "name": "<task name>"}, ...]}  # work remains (possibly empty if blocked)
    {"status": "all_done"}                                       # every task is done

Exit codes:
    0  output produced (either next tasks or all_done)
    2  file/argument problems (missing file, invalid JSON, malformed backlog)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TODO = "todo"
DONE = "done"


def pick_next_tasks(backlog: dict) -> list[dict]:
    """Return every task with status 'todo' whose dependencies are all 'done'."""
    tasks = backlog.get("tasks", [])
    done_ids = {
        task.get("id")
        for task in tasks
        if isinstance(task, dict) and task.get("status") == DONE
    }

    eligible = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        if task.get("status") != TODO:
            continue
        deps = task.get("dependencies") or []
        if all(dep in done_ids for dep in deps):
            eligible.append(task)
    return eligible


def all_done(backlog: dict) -> bool:
    """True iff every dict-shaped task in the backlog has status 'done'."""
    valid = [t for t in backlog.get("tasks", []) if isinstance(t, dict)]
    return bool(valid) and all(t.get("status") == DONE for t in valid)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Return the next eligible tasks from a feature's backlog.json.",
    )
    parser.add_argument("feature_short_name", help="Feature short name (kebab-case)")
    args = parser.parse_args()

    backlog_path = Path(".agents/features") / args.feature_short_name / "backlog.json"
    if not backlog_path.is_file():
        print(f"error: backlog not found at {backlog_path}", file=sys.stderr)
        return 2

    try:
        backlog = json.loads(backlog_path.read_text())
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON at {backlog_path}: {exc}", file=sys.stderr)
        return 2

    if not isinstance(backlog, dict) or not isinstance(backlog.get("tasks"), list):
        print(f"error: malformed backlog at {backlog_path}", file=sys.stderr)
        return 2

    if all_done(backlog):
        print(json.dumps({"status": "all_done"}))
    else:
        eligible = pick_next_tasks(backlog)
        out = [{"id": t.get("id"), "name": t.get("name")} for t in eligible]
        print(json.dumps({"next_tasks": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
