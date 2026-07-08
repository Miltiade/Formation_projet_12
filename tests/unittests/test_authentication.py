import unittest
from unittest.mock import MagicMock, patch
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.controllers.authentication import UserManager


class TestUserManager(unittest.TestCase):

    def setUp(self):
        # Fake DB connection — no real Postgres needed
        self.fake_conn = MagicMock()
        self.fake_cursor = MagicMock()
        self.fake_conn.cursor.return_value = self.fake_cursor
        self.manager = UserManager(self.fake_conn)

    def test_authenticate_returns_user_when_credentials_match(self):
        # Arrange: fake DB says "yes, bob exists with this hash"
        self.fake_cursor.fetchone.return_value = ("bob", "hashed_pw")
        with patch("controllers.authentication.check_password", return_value=True):
            # Act
            result = self.manager.authenticate("bob", "secret")
        # Assert
        self.assertIsNotNone(result)

    def test_authenticate_returns_none_when_password_wrong(self):
        self.fake_cursor.fetchone.return_value = ("bob", "hashed_pw")
        with patch("controllers.authentication.check_password", return_value=False):
            result = self.manager.authenticate("bob", "wrong")
        self.assertIsNone(result)

    def test_create_user_executes_insert_with_hashed_password(self):
        with patch("controllers.authentication.hash_password", return_value="hashed_pw"):
            self.manager.create_user(id=42, name="alice", email="a@x", password="plain")
        # Verify the SQL was called with the HASH, not the plain password
        self.fake_cursor.execute.assert_called_once()
        args = self.fake_cursor.execute.call_args[0]
        self.assertIn("hashed_pw", args[1])
        self.assertNotIn("plain", args[1])


if __name__ == "__main__":
    unittest.main()
