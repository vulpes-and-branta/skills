"""Load skill scripts by file path so they can be exercised as modules.

The scripts under plugins/*/skills/*/scripts/ aren't on sys.path, so this
helper uses importlib to load each script by absolute path.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

_REPO = Path(__file__).resolve().parent.parent
_SDD = _REPO / "plugins/spec-driven-development/skills"
_SCRIPTS = {
    "next_tasks": _SDD / "sdd-build/scripts/next_tasks.py",
    "get_task": _SDD / "sdd-build-task/scripts/get_task.py",
    "validate_backlog": _SDD / "sdd-plan/scripts/validate_backlog.py",
}


def load(name: str) -> ModuleType:
    path = _SCRIPTS[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not build spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
