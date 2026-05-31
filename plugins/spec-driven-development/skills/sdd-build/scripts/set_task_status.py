"""Update the status of a single task in a feature's backlog.json.

Replaces the agent's read-the-whole-backlog-and-rewrite-it approach with a
focused, in-place edit of one task's `status` field. Mutates the backlog file.

Usage (run from {project_root}):
    python scripts/set_task_status.py <feature-short-name> <task-id> <status>

Where <status> is one of:
    todo
    "in progress"
    done

Exit codes:
    0  status updated and file written
    1  no task with the given id in this backlog
    2  file/argument problems (missing file, invalid JSON, malformed backlog,
       non-integer task-id, invalid status value)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ALLOWED_STATUSES = ("todo", "in progress", "done")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update a single task's status in a feature's backlog.json.",
    )
    parser.add_argument("feature_short_name", help="Feature short name (kebab-case)")
    parser.add_argument("task_id", help="Integer id of the task to update")
    parser.add_argument(
        "status",
        help=f"New status (one of: {', '.join(repr(s) for s in ALLOWED_STATUSES)})",
    )
    args = parser.parse_args()

    try:
        task_id = int(args.task_id)
    except ValueError:
        print(f"error: task-id must be an integer (got {args.task_id!r})", file=sys.stderr)
        return 2

    if args.status not in ALLOWED_STATUSES:
        print(
            f"error: status {args.status!r} not in {list(ALLOWED_STATUSES)}",
            file=sys.stderr,
        )
        return 2

    backlog_path = Path(".agents/features") / args.feature_short_name / "backlog.json"
    if not backlog_path.is_file():
        print(f"error: backlog not found at {backlog_path}", file=sys.stderr)
        return 2

    try:
        backlog = json.loads(backlog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON at {backlog_path}: {exc}", file=sys.stderr)
        return 2

    if not isinstance(backlog, dict) or not isinstance(backlog.get("tasks"), list):
        print(f"error: malformed backlog at {backlog_path}", file=sys.stderr)
        return 2

    matched = None
    for task in backlog["tasks"]:
        if isinstance(task, dict) and task.get("id") == task_id:
            matched = task
            break

    if matched is None:
        print(f"error: no task with id {task_id} in {backlog_path}", file=sys.stderr)
        return 1

    previous = matched.get("status")
    matched["status"] = args.status

    backlog_path.write_text(json.dumps(backlog, indent=2) + "\n", encoding="utf-8")
    print(
        f"OK: tasks[id={task_id}] status {previous!r} -> {args.status!r} in {backlog_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
