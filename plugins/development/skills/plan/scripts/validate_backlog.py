"""Validate a plan backlog.json file against the format rules in references/backlog-format.jsonc.

Usage (run from {project_root}):
    python scripts/validate_backlog.py <feature-short-name>

The script resolves `<cwd>/.agents/features/<feature-short-name>/backlog.json`.

Exit codes:
    0  all checks passed
    1  validation errors
    2  file/argument problems (missing file, invalid JSON syntax)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ALLOWED_STATUSES = {"todo", "in progress", "done"}
REQUIRED_TASK_FIELDS = {
    "id",
    "name",
    "status",
    "context",
    "description",
    "locations",
    "references",
    "acceptanceCriteria",
    "dependencies",
}
MAX_NAME_WORDS = 7
MAX_LOCATIONS = 5
MAX_REFERENCES = 5
AC_PREFIXES = ("Inspection:", "UnitTest:")


def validate(backlog: dict) -> list[str]:
    """Return a list of human-readable validation error messages."""
    errors: list[str] = []

    if not isinstance(backlog, dict):
        return ["top level must be a JSON object"]

    if "status" not in backlog:
        errors.append("missing top-level 'status'")
    elif backlog["status"] not in ALLOWED_STATUSES:
        errors.append(
            f"top-level status {backlog['status']!r} not in {sorted(ALLOWED_STATUSES)}"
        )

    tasks = backlog.get("tasks")
    if not isinstance(tasks, list):
        return errors + ["missing or non-list 'tasks' array"]

    seen_ids: dict[object, int] = {}
    valid_ids: set[int] = set()
    for idx, task in enumerate(tasks):
        if not isinstance(task, dict):
            continue
        if "id" not in task:
            continue
        tid = task.get("id")
        prior = seen_ids.get(tid)
        if prior is not None:
            prior_name = tasks[prior].get("name", "<unnamed>") if isinstance(tasks[prior], dict) else "<?>"
            errors.append(
                f"tasks[{idx}]: duplicate id {tid!r} "
                f"(also used by tasks[{prior}] {prior_name!r})"
            )
        else:
            seen_ids[tid] = idx
            if isinstance(tid, int) and not isinstance(tid, bool):
                valid_ids.add(tid)

    for idx, task in enumerate(tasks):
        label = f"tasks[{idx}]"
        if not isinstance(task, dict):
            errors.append(f"{label}: not a JSON object")
            continue

        name = task.get("name", "<unnamed>")
        label = f"tasks[{idx}] {name!r}"

        missing = REQUIRED_TASK_FIELDS - task.keys()
        if missing:
            errors.append(f"{label}: missing fields {sorted(missing)}")

        tid = task.get("id")
        if "id" in task:
            if isinstance(tid, bool) or not isinstance(tid, int):
                errors.append(f"{label}: id must be an integer (got {type(tid).__name__})")

        deps = task.get("dependencies")
        if "dependencies" in task:
            if not isinstance(deps, list):
                errors.append(f"{label}: dependencies must be an array")
            else:
                for d_idx, dep in enumerate(deps):
                    if isinstance(dep, bool) or not isinstance(dep, int):
                        errors.append(
                            f"{label}: dependencies[{d_idx}] must be an integer task id "
                            f"(got {type(dep).__name__})"
                        )
                        continue
                    if isinstance(tid, int) and not isinstance(tid, bool) and dep == tid:
                        errors.append(
                            f"{label}: dependencies[{d_idx}] references the task's own id ({dep})"
                        )
                    elif dep not in valid_ids:
                        errors.append(
                            f"{label}: dependencies[{d_idx}] = {dep} does not match any task id in this backlog"
                        )

        if not isinstance(name, str) or not name.strip():
            errors.append(f"{label}: name must be a non-empty string")
        else:
            word_count = len(name.split())
            if word_count > MAX_NAME_WORDS:
                errors.append(
                    f"{label}: name is {word_count} words (max {MAX_NAME_WORDS})"
                )

        status = task.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(
                f"{label}: status {status!r} not in {sorted(ALLOWED_STATUSES)}"
            )

        for field in ("context", "description"):
            value = task.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}: {field} must be a non-empty string")

        locations = task.get("locations")
        if not isinstance(locations, list):
            errors.append(f"{label}: locations must be an array")
        elif len(locations) > MAX_LOCATIONS:
            errors.append(
                f"{label}: locations has {len(locations)} entries (max {MAX_LOCATIONS})"
            )
        else:
            for l_idx, loc in enumerate(locations):
                if not isinstance(loc, str):
                    errors.append(
                        f"{label}: locations[{l_idx}] must be a string "
                        f"(got {type(loc).__name__})"
                    )
                elif not loc.strip():
                    errors.append(f"{label}: locations[{l_idx}] is empty or whitespace-only")

        references = task.get("references")
        if not isinstance(references, list):
            errors.append(f"{label}: references must be an array")
        elif len(references) > MAX_REFERENCES:
            errors.append(
                f"{label}: references has {len(references)} entries (max {MAX_REFERENCES})"
            )
        else:
            for r_idx, ref in enumerate(references):
                if not isinstance(ref, str):
                    errors.append(
                        f"{label}: references[{r_idx}] must be a string "
                        f"(got {type(ref).__name__})"
                    )
                elif not ref.strip():
                    errors.append(f"{label}: references[{r_idx}] is empty or whitespace-only")

        if isinstance(locations, list) and isinstance(references, list):
            overlap = set(locations) & set(references)
            if overlap:
                errors.append(
                    f"{label}: {sorted(overlap)} appear in both locations and references"
                )

        acs = task.get("acceptanceCriteria")
        if not isinstance(acs, list) or len(acs) == 0:
            errors.append(f"{label}: acceptanceCriteria must be a non-empty array")
        else:
            for ac_idx, ac in enumerate(acs):
                if not isinstance(ac, str):
                    errors.append(
                        f"{label}: acceptanceCriteria[{ac_idx}] must be a string"
                    )
                elif not ac.startswith(AC_PREFIXES):
                    errors.append(
                        f"{label}: acceptanceCriteria[{ac_idx}] must start with "
                        f"'Inspection:' or 'UnitTest:' (got {ac[:40]!r})"
                    )
                else:
                    matched_prefix = next(p for p in AC_PREFIXES if ac.startswith(p))
                    body = ac[len(matched_prefix):].strip()
                    if not body:
                        errors.append(
                            f"{label}: acceptanceCriteria[{ac_idx}] has no content after "
                            f"{matched_prefix!r}"
                        )

    cycle_errors = _detect_dependency_cycles(tasks, valid_ids)
    errors.extend(cycle_errors)

    return errors


def _detect_dependency_cycles(tasks: list, valid_ids: set[int]) -> list[str]:
    """Find cycles in the task dependency graph and return error messages."""
    graph: dict[int, list[int]] = {}
    names: dict[int, str] = {}
    for task in tasks:
        if not isinstance(task, dict):
            continue
        tid = task.get("id")
        if isinstance(tid, bool) or not isinstance(tid, int) or tid not in valid_ids:
            continue
        name = task.get("name")
        names[tid] = name if isinstance(name, str) and name.strip() else "<unnamed>"
        deps = task.get("dependencies")
        if not isinstance(deps, list):
            continue
        graph[tid] = [
            d for d in deps
            if isinstance(d, int) and not isinstance(d, bool) and d in valid_ids and d != tid
        ]

    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[int, int] = {tid: WHITE for tid in graph}
    reported: set[tuple[int, ...]] = set()
    errors: list[str] = []

    def fmt(node: int) -> str:
        return f"{node} ({names.get(node, '<unnamed>')!r})"

    def visit(node: int, stack: list[int]) -> None:
        color[node] = GRAY
        stack.append(node)
        for nxt in graph.get(node, []):
            if color.get(nxt, BLACK) == GRAY:
                cycle = stack[stack.index(nxt):] + [nxt]
                key = tuple(sorted(cycle[:-1]))
                if key not in reported:
                    reported.add(key)
                    errors.append(
                        "dependency cycle detected: " + " -> ".join(fmt(n) for n in cycle)
                    )
            elif color.get(nxt, BLACK) == WHITE:
                visit(nxt, stack)
        stack.pop()
        color[node] = BLACK

    for tid in graph:
        if color[tid] == WHITE:
            visit(tid, [])

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a plan backlog.json against the backlog-format rules."
    )
    parser.add_argument("feature_short_name", help="Feature short name (kebab-case)")
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress the task list on success; only print summary",
    )
    args = parser.parse_args()

    backlog_path = Path(".agents/features") / args.feature_short_name / "backlog.json"
    if not backlog_path.is_file():
        print(f"error: backlog not found at {backlog_path}", file=sys.stderr)
        return 2

    try:
        backlog = json.loads(backlog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON at {backlog_path}: {exc}", file=sys.stderr)
        return 2

    errors = validate(backlog)
    tasks = backlog.get("tasks", []) if isinstance(backlog, dict) else []
    task_count = len(tasks) if isinstance(tasks, list) else 0

    if errors:
        print(f"FAIL: {len(errors)} validation error(s) in {backlog_path}")
        for err in errors:
            print(f"  - {err}")
        print(f"\n{task_count} task(s) found.")
        return 1

    print(f"OK: {backlog_path} is valid. {task_count} task(s).")
    if not args.quiet and isinstance(tasks, list):
        for idx, task in enumerate(tasks, start=1):
            name = task.get("name", "<unnamed>") if isinstance(task, dict) else "<?>"
            status = task.get("status", "?") if isinstance(task, dict) else "?"
            print(f"  {idx:2d}. [{status}] {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
