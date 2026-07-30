import os
import shutil
import tempfile
import unittest

from data.database import SQLiteDatabase
from logic.auth_manager import AuthManager


class AuthManagerCaseInsensitiveTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "tasks.db")
        self.storage = SQLiteDatabase(self.db_path)
        self.auth = AuthManager(self.storage)

    def tearDown(self):
        shutil.rmtree(self.tmpdir.name, ignore_errors=True)

    def test_login_is_case_insensitive(self):
        self.auth.register("Alice", "1234")

        user = self.auth.login("alice", "1234")

        self.assertEqual(user["username"], "Alice")

    def test_duplicate_usernames_are_blocked_case_insensitively(self):
        self.auth.register("Alice", "1234")

        with self.assertRaises(ValueError):
            self.auth.register("ALICE", "1234")


if __name__ == "__main__":
    unittest.main()
