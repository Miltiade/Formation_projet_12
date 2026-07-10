import unittest
from unittest.mock import patch, MagicMock
from app.controllers.read_data_from_db import DataReader
from app.models.classes import Collaborator, Department

"""
Ce fichier teste la classe DataReader:
Comportement attendu de ce test:
setUp: prépare le test
test_get_all_clients_success : si l'utilisateur est auth et a les permissions, l'accès aux clients lui est donné
test_get_all_clients_no_permission: si l'utilisateur n'a pas les permissions, l'accès aux clients lui est refusé
test_get_all_clients_user_none: si l'utilisateur n'est pas authentifié, l'accès aux clients lui est refusé
"""

class TestDataReader(unittest.TestCase):

    def setUp(self):
        """Prépare un Collaborator avec département et instance DataReader"""
        dept = Department("Gestion")
        self.user = Collaborator(1, "testuser", "test@example.com", "secret", dept)
        self.reader = DataReader(self.user)

    @patch("app.controllers.read_data_from_db.get_db_connection")
    @patch("app.controllers.read_data_from_db.has_permission")
    def test_get_all_clients_success(self, mock_has_perm, mock_get_conn):
        # Simuler permission accordée
        mock_has_perm.return_value = True

        # Simuler connexion et curseur
        fake_cursor = MagicMock()
        fake_cursor.fetchall.return_value = [
            (1, "Client A", "a@example.com"),
            (2, "Client B", "b@example.com"),
        ]
        fake_conn = MagicMock()
        fake_conn.cursor.return_value.__enter__.return_value = fake_cursor
        mock_get_conn.return_value = fake_conn

        clients = self.reader.get_all_clients()

        self.assertEqual(len(clients), 2)
        self.assertEqual(clients[0]["name"], "Client A")
        self.assertEqual(clients[1]["email"], "b@example.com")
        mock_has_perm.assert_called_once_with(self.user, "view_all_clients")

    @patch("app.controllers.read_data_from_db.has_permission")
    def test_get_all_clients_no_permission(self, mock_has_perm):
        # DataReader si utilisateur n'a pas les permissions
        mock_has_perm.return_value = False
        with self.assertRaises(PermissionError):
            self.reader.get_all_clients()

    def test_get_all_clients_user_none(self):
        # DataReader sans utilisateur authentifié
        reader = DataReader(None)
        with self.assertRaises(PermissionError):
            reader.get_all_clients()

if __name__ == "__main__":
    unittest.main()