"""Pick the next eligible tasks from a feature's backlog.json.

Replaces the agent's full-file reads of backlog.json with a single small
JSON output. Returns every task whose status is "todo", whose dependencies
are all "done", and whose `locations` do not collide with another returned
task or with a task already "in progress" — so the caller can dispatch the
result in parallel without subagents racing on the same files. Read-only.

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
IN_PROGRESS = "in progress"


def _normalize(location: str) -> str:
    """Collapse a location string to a comparable posix-style relative path.

    Case-folded because macOS and Windows filesystems are case-insensitive by
    default, so `SRC/A.py` and `src/a.py` are the same file and must collide.
    On case-sensitive filesystems this can serialize two genuinely distinct
    files, which costs a little parallelism but never causes a write race.
    Used only for comparison; emitted task ids and names keep their own casing.
    """
    parts = [p for p in location.strip().replace("\\", "/").split("/") if p not in ("", ".")]
    return "/".join(parts).casefold()


def _locations(task: dict) -> list[str]:
    """Normalized, non-empty `locations` entries for a task."""
    raw = task.get("locations") or []
    if not isinstance(raw, list):
        return []
    return [n for loc in raw if isinstance(loc, str) and (n := _normalize(loc))]


def _collides(location: str, reserved: set[str]) -> bool:
    """True if `location` is, contains, or lives under any reserved path."""
    return any(
        location == r or location.startswith(r + "/") or r.startswith(location + "/")
        for r in reserved
    )


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


def filter_file_conflicts(eligible: list[dict], tasks: list[dict]) -> list[dict]:
    """Drop eligible tasks whose files are already spoken for.

    Files held by "in progress" tasks are reserved up front. The remainder are
    then admitted greedily in ascending id order, so on a collision the lowest
    id wins and higher-id tasks stay `todo` until the next call.
    """
    reserved: set[str] = set()
    for task in tasks:
        if isinstance(task, dict) and task.get("status") == IN_PROGRESS:
            reserved.update(_locations(task))

    admitted = []
    for task in sorted(eligible, key=lambda t: _sort_id(t)):
        locations = _locations(task)
        if any(_collides(loc, reserved) for loc in locations):
            continue
        reserved.update(locations)
        admitted.append(task)
    return admitted


def _sort_id(task: dict) -> tuple[int, int]:
    """Sort key placing well-formed integer ids first, ascending."""
    task_id = task.get("id")
    return (0, task_id) if isinstance(task_id, int) else (1, 0)


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
        admitted = filter_file_conflicts(eligible, backlog["tasks"])
        out = [{"id": t.get("id"), "name": t.get("name")} for t in admitted]
        print(json.dumps({"next_tasks": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
