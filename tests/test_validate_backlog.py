import unittest

from _loader import load

vb = load("validate_backlog")


def task(**overrides):
    """Return a well-formed task dict, optionally overridden per-test."""
    base = {
        "id": 0,
        "name": "do the thing",
        "status": "todo",
        "context": "ctx",
        "description": "desc",
        "locations": ["a.py"],
        "references": ["b.py"],
        "acceptanceCriteria": ["UnitTest: it works"],
        "dependencies": [],
    }
    base.update(overrides)
    return base


class ValidateTests(unittest.TestCase):
    def test_well_formed_backlog_has_no_errors(self):
        self.assertEqual(vb.validate({"status": "todo", "tasks": [task()]}), [])

    def test_missing_top_level_status(self):
        errors = vb.validate({"tasks": []})
        self.assertTrue(any("status" in e for e in errors))

    def test_invalid_top_level_status(self):
        errors = vb.validate({"status": "weird", "tasks": []})
        self.assertTrue(any("not in" in e for e in errors))

    def test_duplicate_ids(self):
        backlog = {
            "status": "todo",
            "tasks": [task(id=0), task(id=0, name="other")],
        }
        errors = vb.validate(backlog)
        self.assertTrue(any("duplicate id" in e for e in errors))

    def test_acceptance_criteria_must_have_prefix(self):
        backlog = {
            "status": "todo",
            "tasks": [task(acceptanceCriteria=["it works"])],
        }
        errors = vb.validate(backlog)
        self.assertTrue(
            any("Inspection:" in e or "UnitTest:" in e for e in errors)
        )

    def test_dependency_cycle_detected(self):
        backlog = {
            "status": "todo",
            "tasks": [
                task(id=0, dependencies=[1]),
                task(id=1, name="task b", dependencies=[0]),
            ],
        }
        errors = vb.validate(backlog)
        self.assertTrue(any("cycle" in e for e in errors))

    def test_dependency_to_nonexistent_id(self):
        backlog = {
            "status": "todo",
            "tasks": [task(id=0, dependencies=[99])],
        }
        errors = vb.validate(backlog)
        self.assertTrue(any("does not match any task id" in e for e in errors))

    def test_self_dependency_rejected(self):
        backlog = {
            "status": "todo",
            "tasks": [task(id=0, dependencies=[0])],
        }
        errors = vb.validate(backlog)
        self.assertTrue(any("own id" in e for e in errors))

    def test_name_too_long(self):
        backlog = {
            "status": "todo",
            "tasks": [task(name="one two three four five six seven eight")],
        }
        errors = vb.validate(backlog)
        self.assertTrue(any("words" in e for e in errors))

    def test_locations_references_overlap(self):
        backlog = {
            "status": "todo",
            "tasks": [task(locations=["x.py"], references=["x.py"])],
        }
        errors = vb.validate(backlog)
        self.assertTrue(any("both locations and references" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
