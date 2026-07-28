import os
import tempfile
import unittest

from data.database import JsonDatabase
from logic.task_manager import TaskManager


class TaskManagerTests(unittest.TestCase):
    def test_add_and_list_tasks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = JsonDatabase(os.path.join(temp_dir, "tasks.json"))
            manager = TaskManager(storage)

            task = manager.add_task("Estudar", "Revisar o template")

            self.assertEqual(task.title, "Estudar")
            self.assertEqual(task.description, "Revisar o template")
            self.assertFalse(task.completed)
            self.assertEqual(len(manager.list_tasks()), 1)
            self.assertEqual(manager.list_tasks()[0].title, "Estudar")


if __name__ == "__main__":
    unittest.main()
