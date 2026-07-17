"""Report progress of a task's dependencies from a feature's progress.jsonl.

Ensures progress.jsonl exists (created empty if missing), looks up the task's
dependencies in backlog.json, and prints one line per dependency describing
the recorded progress. Read-only with respect to backlog.json.

Usage (run from {project_root}):
    python scripts/get_dependency_progress.py <feature-short-name> <task-id>

Output (stdout):
    Empty string if the task has no dependencies. Otherwise one line per
    dependency:
        TaskId: [taskId] Summary: [summary] Deviations: [deviations]

Exit codes:
    0  success (including the no-dependencies case)
    1  no task with the given id in this backlog
    2  file/argument problems (missing backlog, invalid JSON, malformed
       backlog, non-integer task-id)
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


def load_progress(progress_path: Path) -> dict[int, dict]:
    """Map taskId -> latest progress entry for that task."""
    entries: dict[int, dict] = {}
    for line in progress_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(entry, dict) and isinstance(entry.get("taskId"), int):
            entries[entry["taskId"]] = entry
    return entries


def format_entry(dep_id: int, entry: dict | None) -> str:
    if entry is None:
        return f"TaskId: {dep_id} Summary: (no progress entry) Deviations: []"
    summary = entry.get("summary", "")
    deviations = entry.get("deviations", [])
    return f"TaskId: {dep_id} Summary: {summary} Deviations: {json.dumps(deviations)}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print progress of a task's dependencies from progress.jsonl.",
    )
    parser.add_argument("feature_short_name", help="Feature short name (kebab-case)")
    parser.add_argument("task_id", help="Integer id of the task whose dependencies to report")
    args = parser.parse_args()

    try:
        task_id = int(args.task_id)
    except ValueError:
        print(f"error: task-id must be an integer (got {args.task_id!r})", file=sys.stderr)
        return 2

    feature_dir = Path(".agents/features") / args.feature_short_name

    progress_path = feature_dir / "progress.jsonl"
    if not progress_path.is_file():
        progress_path.parent.mkdir(parents=True, exist_ok=True)
        progress_path.touch()

    backlog_path = feature_dir / "backlog.json"
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

    dependencies = task.get("dependencies", [])
    if not isinstance(dependencies, list) or not dependencies:
        return 0

    progress = load_progress(progress_path)
    lines = [format_entry(dep_id, progress.get(dep_id)) for dep_id in dependencies]
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
