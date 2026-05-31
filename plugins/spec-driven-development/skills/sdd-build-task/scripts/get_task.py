"""Look up a single task in a feature's backlog.json by id.

Replaces the agent's grep-and-read of the full backlog with a focused JSON
output containing only the requested task. Read-only.

Usage (run from {project_root}):
    python scripts/get_task.py <feature-short-name> <task-id>

Output (stdout):
    The matched task as pretty-printed JSON.

Exit codes:
    0  task found and printed
    1  no task with the given id in this backlog
    2  file/argument problems (missing file, invalid JSON, malformed backlog,
       non-integer task-id)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def find_task(backlog: dict, task_id: int) -> dict | None:
    for task in backlog.get("tasks", []):
        if isinstance(task, dict) and task.get("id") == task_id:
            return task
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print a single task from a feature's backlog.json by id.",
    )
    parser.add_argument("feature_short_name", help="Feature short name (kebab-case)")
    parser.add_argument("task_id", help="Integer id of the task to retrieve")
    args = parser.parse_args()

    try:
        task_id = int(args.task_id)
    except ValueError:
        print(f"error: task-id must be an integer (got {args.task_id!r})", file=sys.stderr)
        return 2

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

    task = find_task(backlog, task_id)
    if task is None:
        print(f"error: no task with id {task_id} in {backlog_path}", file=sys.stderr)
        return 1

    print(json.dumps(task, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
