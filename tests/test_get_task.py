import unittest

from _loader import load

get_task = load("get_task")


class FindTaskTests(unittest.TestCase):
    def test_finds_task_by_id(self):
        backlog = {
            "tasks": [
                {"id": 0, "name": "a"},
                {"id": 1, "name": "b"},
                {"id": 2, "name": "c"},
            ],
        }
        self.assertEqual(get_task.find_task(backlog, 1)["name"], "b")

    def test_returns_none_when_id_missing(self):
        backlog = {"tasks": [{"id": 0, "name": "a"}]}
        self.assertIsNone(get_task.find_task(backlog, 99))

    def test_returns_none_for_empty_tasks(self):
        self.assertIsNone(get_task.find_task({"tasks": []}, 0))

    def test_skips_non_dict_entries(self):
        backlog = {
            "tasks": [
                "not a dict",
                {"id": 0, "name": "a"},
            ],
        }
        self.assertEqual(get_task.find_task(backlog, 0)["name"], "a")


if __name__ == "__main__":
    unittest.main()
