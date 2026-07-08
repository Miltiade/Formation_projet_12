"""TESTS:
-- get_permissions retourne bien la liste complète (permissions communes + spécifiques) selon le rôle.
-- has_permission renvoie True quand l’utilisateur a la permission, et False sinon.
"""

import unittest
from app.controllers.authorizations import get_permissions, has_permission
from app.models.classes import Collaborator, Department

def make_user_for_role(role_name: str) -> Collaborator:
    # Crée un Collaborator avec le département correspondant au rôle donné
    # On mappe role->department pour test rapidement
    role_to_dept = {
        "gestion": "Gestion",
        "commercial": "Commercial",
        "support": "Support",
    }
    dept_name = role_to_dept.get(role_name.lower(), "Commercial")
    dept = Department(dept_name)
    return Collaborator(id=1, username="user", email="u@u.com", password="xxx", department=dept)

class TestAuthorizations(unittest.TestCase):

    def test_get_permissions_contains_common_and_role_specific(self):
        for role in ["gestion", "commercial", "support"]:
            with self.subTest(role=role):
                user = make_user_for_role(role)
                perms = get_permissions(user)
                # Vérifie que les permissions communes sont présentes
                self.assertIn("view_all_clients", perms)
                self.assertIn("view_all_contracts", perms)
                self.assertIn("view_all_events", perms)
                # Vérifie qu’on a au moins une permission spécifique au rôle
                role_perms = set(perms) - {"view_all_clients", "view_all_contracts", "view_all_events",
                                          "view_client", "view_contract", "view_event"}
                self.assertTrue(len(role_perms) > 0, f"Pas de permissions spécifiques pour {role}")

    def test_has_permission_correct_behavior(self):
        user = make_user_for_role("gestion")
        # permission qu'il a
        self.assertTrue(has_permission(user, "create_collaborator"))
        # permission qu'il n'a pas
        self.assertFalse(has_permission(user, "create_client"))

if __name__ == "__main__":
    unittest.main()
