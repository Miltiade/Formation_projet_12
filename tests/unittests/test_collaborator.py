import unittest
from app.models.classes import Collaborator, Department

class TestCollaborator(unittest.TestCase):
    """Tests unitaires pour la classe Collaborator."""

    def setUp(self):
        """
        Prépare un collaborateur de test avant chaque méthode.
        Crée un département 'Gestion' et un utilisateur avec mot de passe haché.
        """
        self.dept = Department("Gestion")
        self.user = Collaborator(id=1, username="alice", email="alice@example.com",
                                 password="Secret123!", department=self.dept)

    def test_verify_password_correct(self):
        """
        Vérifie que la méthode verify_password retourne True
        pour le mot de passe correct.
        """
        self.assertTrue(self.user.verify_password("Secret123!"))

    def test_verify_password_incorrect(self):
        """
        Vérifie que verify_password retourne False
        pour un mot de passe incorrect.
        """
        self.assertFalse(self.user.verify_password("WrongPass"))

    def test_role_property(self):
        """
        Vérifie que la propriété 'role' renvoie la bonne valeur
        en fonction du département assigné.
        """
        self.assertEqual(self.user.role, "gestion")

if __name__ == "__main__":
    # Exécute les tests quand le script est lancé directement
    unittest.main()