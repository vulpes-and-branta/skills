import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _loader import load

next_tasks = load("next_tasks")

SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "plugins/development/skills/build/scripts/next_tasks.py"
)


class PickNextTasksTests(unittest.TestCase):
    def test_returns_all_todo_tasks_with_no_deps(self):
        backlog = {
            "tasks": [
                {"id": 0, "name": "a", "status": "todo", "dependencies": []},
                {"id": 1, "name": "b", "status": "todo", "dependencies": []},
            ],
        }
        result = next_tasks.pick_next_tasks(backlog)
        self.assertEqual([t["id"] for t in result], [0, 1])

    def test_includes_task_when_all_deps_done(self):
        backlog = {
            "tasks": [
                {"id": 0, "name": "a", "status": "done", "dependencies": []},
                {"id": 1, "name": "b", "status": "done", "dependencies": []},
                {"id": 2, "name": "c", "status": "todo", "dependencies": [0, 1]},
            ],
        }
        result = next_tasks.pick_next_tasks(backlog)
        self.assertEqual([t["id"] for t in result], [2])

    def test_excludes_task_when_any_dep_not_done(self):
        backlog = {
            "tasks": [
                {"id": 0, "name": "a", "status": "done", "dependencies": []},
                {"id": 1, "name": "b", "status": "todo", "dependencies": []},
                {"id": 2, "name": "c", "status": "todo", "dependencies": [0, 1]},
            ],
        }
        result = next_tasks.pick_next_tasks(backlog)
        self.assertEqual([t["id"] for t in result], [1])

    def test_excludes_in_progress_tasks(self):
        backlog = {
            "tasks": [
                {"id": 0, "name": "a", "status": "in progress", "dependencies": []},
                {"id": 1, "name": "b", "status": "todo", "dependencies": []},
            ],
        }
        result = next_tasks.pick_next_tasks(backlog)
        self.assertEqual([t["id"] for t in result], [1])

    def test_excludes_done_tasks(self):
        backlog = {
            "tasks": [
                {"id": 0, "name": "a", "status": "done", "dependencies": []},
                {"id": 1, "name": "b", "status": "todo", "dependencies": []},
            ],
        }
        result = next_tasks.pick_next_tasks(backlog)
        self.assertEqual([t["id"] for t in result], [1])

    def test_in_progress_dep_blocks_dependent_task(self):
        backlog = {
            "tasks": [
                {"id": 0, "name": "a", "status": "in progress", "dependencies": []},
                {"id": 1, "name": "b", "status": "todo", "dependencies": [0]},
            ],
        }
        self.assertEqual(next_tasks.pick_next_tasks(backlog), [])

    def test_returns_empty_when_all_tasks_done(self):
        backlog = {
            "tasks": [
                {"id": 0, "name": "a", "status": "done", "dependencies": []},
                {"id": 1, "name": "b", "status": "done", "dependencies": []},
            ],
        }
        self.assertEqual(next_tasks.pick_next_tasks(backlog), [])

    def test_returns_empty_for_empty_tasks(self):
        self.assertEqual(next_tasks.pick_next_tasks({"tasks": []}), [])

    def test_skips_non_dict_entries(self):
        backlog = {
            "tasks": [
                "not a dict",
                {"id": 0, "name": "a", "status": "todo"},
            ],
        }
        result = next_tasks.pick_next_tasks(backlog)
        self.assertEqual([t["id"] for t in result], [0])

    def test_handles_missing_dependencies_field(self):
        backlog = {
            "tasks": [
                {"id": 0, "name": "a", "status": "todo"},
            ],
        }
        result = next_tasks.pick_next_tasks(backlog)
        self.assertEqual([t["id"] for t in result], [0])

    def test_chain_of_dependencies_only_unblocks_root(self):
        backlog = {
            "tasks": [
                {"id": 0, "name": "a", "status": "todo", "dependencies": []},
                {"id": 1, "name": "b", "status": "todo", "dependencies": [0]},
                {"id": 2, "name": "c", "status": "todo", "dependencies": [1]},
            ],
        }
        result = next_tasks.pick_next_tasks(backlog)
        self.assertEqual([t["id"] for t in result], [0])

    def test_returns_multiple_eligible_tasks_in_parallel_branches(self):
        backlog = {
            "tasks": [
                {"id": 0, "name": "root", "status": "done", "dependencies": []},
                {"id": 1, "name": "branch-a", "status": "todo", "dependencies": [0]},
                {"id": 2, "name": "branch-b", "status": "todo", "dependencies": [0]},
                {"id": 3, "name": "leaf", "status": "todo", "dependencies": [1, 2]},
            ],
        }
        result = next_tasks.pick_next_tasks(backlog)
        self.assertEqual([t["id"] for t in result], [1, 2])

    def test_done_dep_satisfies_even_when_other_todos_exist(self):
        backlog = {
            "tasks": [
                {"id": 0, "name": "a", "status": "done", "dependencies": []},
                {"id": 1, "name": "unrelated", "status": "todo", "dependencies": []},
                {"id": 2, "name": "b", "status": "todo", "dependencies": [0]},
            ],
        }
        result = next_tasks.pick_next_tasks(backlog)
        self.assertEqual(sorted(t["id"] for t in result), [1, 2])


class FilterFileConflictsTests(unittest.TestCase):
    def _filter(self, tasks):
        eligible = next_tasks.pick_next_tasks({"tasks": tasks})
        admitted = next_tasks.filter_file_conflicts(eligible, tasks)
        return [t["id"] for t in admitted]

    def test_admits_all_when_locations_disjoint(self):
        tasks = [
            {"id": 0, "name": "a", "status": "todo", "locations": ["a.py"]},
            {"id": 1, "name": "b", "status": "todo", "locations": ["b.py"]},
        ]
        self.assertEqual(self._filter(tasks), [0, 1])

    def test_lowest_id_wins_on_shared_location(self):
        tasks = [
            {"id": 3, "name": "c", "status": "todo", "locations": ["shared.py"]},
            {"id": 1, "name": "a", "status": "todo", "locations": ["shared.py"]},
            {"id": 2, "name": "b", "status": "todo", "locations": ["shared.py"]},
        ]
        self.assertEqual(self._filter(tasks), [1])

    def test_greedy_admits_non_overlapping_tail(self):
        # 1[a] blocks 2[a,b], but 3[b] is still free once 2 is skipped.
        tasks = [
            {"id": 1, "name": "a", "status": "todo", "locations": ["a.py"]},
            {"id": 2, "name": "b", "status": "todo", "locations": ["a.py", "b.py"]},
            {"id": 3, "name": "c", "status": "todo", "locations": ["b.py"]},
        ]
        self.assertEqual(self._filter(tasks), [1, 3])

    def test_in_progress_task_reserves_its_locations(self):
        tasks = [
            {"id": 0, "name": "a", "status": "in progress", "locations": ["a.py"]},
            {"id": 1, "name": "b", "status": "todo", "locations": ["a.py"]},
            {"id": 2, "name": "c", "status": "todo", "locations": ["b.py"]},
        ]
        self.assertEqual(self._filter(tasks), [2])

    def test_done_task_locations_are_not_reserved(self):
        tasks = [
            {"id": 0, "name": "a", "status": "done", "locations": ["a.py"]},
            {"id": 1, "name": "b", "status": "todo", "locations": ["a.py"]},
        ]
        self.assertEqual(self._filter(tasks), [1])

    def test_tasks_without_locations_never_conflict(self):
        tasks = [
            {"id": 0, "name": "a", "status": "todo"},
            {"id": 1, "name": "b", "status": "todo", "locations": []},
            {"id": 2, "name": "c", "status": "todo", "locations": ["a.py"]},
        ]
        self.assertEqual(self._filter(tasks), [0, 1, 2])

    def test_references_do_not_conflict(self):
        tasks = [
            {"id": 0, "name": "a", "status": "todo", "locations": ["a.py"],
             "references": ["shared.py"]},
            {"id": 1, "name": "b", "status": "todo", "locations": ["shared.py"]},
        ]
        self.assertEqual(self._filter(tasks), [0, 1])

    def test_equivalent_paths_conflict_after_normalization(self):
        tasks = [
            {"id": 0, "name": "a", "status": "todo", "locations": ["src/a.py"]},
            {"id": 1, "name": "b", "status": "todo", "locations": ["./src//a.py"]},
        ]
        self.assertEqual(self._filter(tasks), [0])

    def test_directory_conflicts_with_file_beneath_it(self):
        tasks = [
            {"id": 0, "name": "a", "status": "todo", "locations": ["src/api/"]},
            {"id": 1, "name": "b", "status": "todo", "locations": ["src/api/routes.py"]},
            {"id": 2, "name": "c", "status": "todo", "locations": ["src/apiary.py"]},
        ]
        self.assertEqual(self._filter(tasks), [0, 2])

    def test_file_beneath_directory_conflicts_in_either_order(self):
        tasks = [
            {"id": 0, "name": "a", "status": "todo", "locations": ["src/api/routes.py"]},
            {"id": 1, "name": "b", "status": "todo", "locations": ["src/api"]},
        ]
        self.assertEqual(self._filter(tasks), [0])

    def test_ignores_non_string_and_blank_locations(self):
        tasks = [
            {"id": 0, "name": "a", "status": "todo", "locations": [None, "  ", "a.py"]},
            {"id": 1, "name": "b", "status": "todo", "locations": ["a.py"]},
        ]
        self.assertEqual(self._filter(tasks), [0])

    def test_handles_malformed_locations_field(self):
        tasks = [
            {"id": 0, "name": "a", "status": "todo", "locations": "not-a-list"},
            {"id": 1, "name": "b", "status": "todo", "locations": ["a.py"]},
        ]
        self.assertEqual(self._filter(tasks), [0, 1])


class AllDoneTests(unittest.TestCase):
    def test_all_done_when_every_task_done(self):
        backlog = {
            "tasks": [
                {"id": 0, "status": "done"},
                {"id": 1, "status": "done"},
            ],
        }
        self.assertTrue(next_tasks.all_done(backlog))

    def test_not_all_done_when_one_in_progress(self):
        backlog = {
            "tasks": [
                {"id": 0, "status": "done"},
                {"id": 1, "status": "in progress"},
            ],
        }
        self.assertFalse(next_tasks.all_done(backlog))

    def test_not_all_done_when_one_todo(self):
        backlog = {
            "tasks": [
                {"id": 0, "status": "done"},
                {"id": 1, "status": "todo"},
            ],
        }
        self.assertFalse(next_tasks.all_done(backlog))

    def test_not_all_done_for_empty_tasks(self):
        # Empty backlog isn't considered "done"; main() will emit next_tasks: [].
        self.assertFalse(next_tasks.all_done({"tasks": []}))


class CliTests(unittest.TestCase):
    FEATURE = "fixture-feature"

    def _run(self, payload):
        with tempfile.TemporaryDirectory() as tmp:
            backlog_dir = Path(tmp) / ".agents" / "features" / self.FEATURE
            backlog_dir.mkdir(parents=True)
            (backlog_dir / "backlog.json").write_text(json.dumps(payload))
            proc = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), self.FEATURE],
                capture_output=True,
                text=True,
                check=False,
                cwd=tmp,
            )
        return proc

    def test_cli_emits_next_tasks_array(self):
        proc = self._run({
            "status": "in progress",
            "tasks": [
                {"id": 0, "name": "a", "status": "done", "dependencies": []},
                {"id": 1, "name": "b", "status": "todo", "dependencies": [0]},
                {"id": 2, "name": "c", "status": "todo", "dependencies": [0]},
            ],
        })
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(
            json.loads(proc.stdout),
            {"next_tasks": [{"id": 1, "name": "b"}, {"id": 2, "name": "c"}]},
        )

    def test_cli_withholds_conflicting_task(self):
        proc = self._run({
            "status": "in progress",
            "tasks": [
                {"id": 0, "name": "a", "status": "done", "dependencies": [],
                 "locations": []},
                {"id": 1, "name": "b", "status": "todo", "dependencies": [0],
                 "locations": ["src/shared.py"]},
                {"id": 2, "name": "c", "status": "todo", "dependencies": [0],
                 "locations": ["src/shared.py"]},
            ],
        })
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(
            json.loads(proc.stdout),
            {"next_tasks": [{"id": 1, "name": "b"}]},
        )

    def test_cli_emits_all_done_when_complete(self):
        proc = self._run({
            "status": "done",
            "tasks": [
                {"id": 0, "name": "a", "status": "done", "dependencies": []},
            ],
        })
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {"status": "all_done"})

    def test_cli_emits_empty_array_when_blocked(self):
        proc = self._run({
            "status": "in progress",
            "tasks": [
                {"id": 0, "name": "a", "status": "in progress", "dependencies": []},
                {"id": 1, "name": "b", "status": "todo", "dependencies": [0]},
            ],
        })
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {"next_tasks": []})

    def test_cli_errors_when_feature_dir_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "no-such-feature"],
                capture_output=True,
                text=True,
                check=False,
                cwd=tmp,
            )
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
