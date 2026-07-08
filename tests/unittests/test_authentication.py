import unittest
from unittest.mock import patch, MagicMock
from app.controllers.authentication import UserManager, AuthService
from app.models.classes import Collaborator, Department


def make_collaborator(id=1, username="bob", email="bob@x.com",
                      password="secret", department_name="Commercial"):
    dept = Department(department_name)
    return Collaborator(id=id, username=username, email=email,
                        password=password, department=dept)


class TestUserManager(unittest.TestCase):

    def setUp(self):
        self.fake_conn = MagicMock()
        self.fake_cursor = MagicMock()
        self.fake_conn.cursor.return_value = self.fake_cursor
        self.manager = UserManager()

    def test_authenticate_returns_none_when_email_not_found(self):
        self.fake_cursor.fetchone.return_value = None
        with patch("app.controllers.authentication.get_db_connection",
                   return_value=self.fake_conn):
            result = self.manager.authenticate("nobody@x.com", "secret")
        self.assertIsNone(result)

    def test_authenticate_returns_user_when_password_matches(self):
        real_user = make_collaborator(password="secret")
        real_hash = real_user._Collaborator__password_hash
        self.fake_cursor.fetchone.return_value = (
            real_user.id, real_user.username, real_user.email,
            real_hash, real_user.department.name
        )
        with patch("app.controllers.authentication.get_db_connection",
                   return_value=self.fake_conn):
            result = self.manager.authenticate("bob@x.com", "secret")
        self.assertIsNotNone(result)
        self.assertEqual(result.email, "bob@x.com")

    def test_authenticate_returns_none_when_password_wrong(self):
        real_user = make_collaborator(password="secret")
        real_hash = real_user._Collaborator__password_hash
        self.fake_cursor.fetchone.return_value = (
            real_user.id, real_user.username, real_user.email,
            real_hash, real_user.department.name
        )
        with patch("app.controllers.authentication.get_db_connection",
                   return_value=self.fake_conn):
            result = self.manager.authenticate("bob@x.com", "WRONG")
        self.assertIsNone(result)

    def test_create_user_executes_insert_with_hashed_password(self):
        with patch("app.controllers.authentication.get_db_connection",
                   return_value=self.fake_conn):
            self.manager.create_user(
                id=42, username="alice", email="a@x.com",
                password="plain", department_name="Commercial"
            )
        self.fake_cursor.execute.assert_called_once()
        sql, params = self.fake_cursor.execute.call_args[0]
        # The 4th param is the password hash — must NOT be the plain password
        self.assertNotEqual(params[3], "plain")
        self.assertTrue(len(params[3]) > 20)


class TestAuthService(unittest.TestCase):

    def test_create_token_returns_a_jwt_string(self):
        user = make_collaborator()
        token = AuthService.create_token(user)
        self.assertEqual(len(token.split(".")), 3)

    def test_decode_token_roundtrip_returns_payload(self):
        user = make_collaborator(id=7, department_name="Gestion")
        token = AuthService.create_token(user)
        payload = AuthService.decode_token(token)
        self.assertEqual(payload["user_id"], 7)
        self.assertEqual(payload["role"], "gestion")


if __name__ == "__main__":
    unittest.main()
