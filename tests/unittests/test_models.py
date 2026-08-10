"""
Tests unitaires pour les modèles Department, Client, Contract, Event.
Aucune connexion DB requise — pure logique métier.
"""

import unittest
from app.models.classes import Department, Client, Contract, Event


class TestDepartment(unittest.TestCase):
    """Tests pour la classe Department."""

    def test_valid_departments_accepted(self):
        """Les 3 départements valides sont acceptés sans erreur."""
        for name in ["Gestion", "Commercial", "Support"]:
            with self.subTest(name=name):
                dept = Department(name)
                self.assertEqual(dept.name, name)

    def test_invalid_department_raises_error(self):
        """Un département inconnu lève une ValueError."""
        with self.assertRaises(ValueError):
            Department("RH")

    def test_role_mapping_is_correct(self):
        """Chaque département mappe vers le bon rôle."""
        cases = {"Gestion": "gestion", "Commercial": "commercial", "Support": "support"}
        for dept_name, expected_role in cases.items():
            with self.subTest(dept=dept_name):
                dept = Department(dept_name)
                self.assertEqual(dept.role, expected_role)


class TestClient(unittest.TestCase):
    """Tests pour la classe Client."""

    def setUp(self):
        self.client = Client(
            id=1, full_name="Jean Dupont", email="jean@test.com",
            phone="+33600000000", company_name="Acme SARL",
            creation_date="2025-01-01", last_update_date="2025-01-01",
            commercial_contact_id=2
        )

    def test_attributes_are_stored(self):
        """Les attributs passés au constructeur sont bien stockés."""
        self.assertEqual(self.client.full_name, "Jean Dupont")
        self.assertEqual(self.client.email, "jean@test.com")
        self.assertEqual(self.client.company_name, "Acme SARL")
        self.assertEqual(self.client.commercial_contact_id, 2)


class TestContract(unittest.TestCase):
    """Tests pour la classe Contract."""

    def setUp(self):
        self.contract = Contract(
            id=1, total_amount=10000.0, remaining_amount=5000.0,
            creation_date="2025-01-15", is_signed=True,
            client_id=1, commercial_contact_id=2
        )

    def test_attributes_are_stored(self):
        """Les attributs passés au constructeur sont bien stockés."""
        self.assertEqual(self.contract.total_amount, 10000.0)
        self.assertEqual(self.contract.remaining_amount, 5000.0)
        self.assertTrue(self.contract.is_signed)
        self.assertEqual(self.contract.client_id, 1)

    def test_unsigned_contract_flag(self):
        """Un contrat non signé a is_signed=False."""
        c = Contract(2, 5000.0, 5000.0, "2025-02-01", False, 1, 2)
        self.assertFalse(c.is_signed)


class TestEvent(unittest.TestCase):
    """Tests pour la classe Event."""

    def setUp(self):
        self.event = Event(
            id=1, name="Product Launch", client_name="Jean Dupont",
            client_contact="jean@test.com", date_start="2025-06-15",
            date_end="2025-06-15", location="Paris", attendees=200,
            notes="Annual event", contract_id=1, support_contact_id=3
        )

    def test_attributes_are_stored(self):
        """Les attributs passés au constructeur sont bien stockés."""
        self.assertEqual(self.event.name, "Product Launch")
        self.assertEqual(self.event.attendees, 200)
        self.assertEqual(self.event.contract_id, 1)
        self.assertEqual(self.event.support_contact_id, 3)

    def test_support_can_be_none(self):
        """Un événement sans support assigné a support_contact_id=None."""
        e = Event(
            id=2, name="Test Event", client_name="Client X",
            client_contact="x@test.com", date_start="2025-07-01",
            date_end="2025-07-01", location="Lyon", attendees=10,
            notes="No support", contract_id=1, support_contact_id=None
        )
        self.assertIsNone(e.support_contact_id)


if __name__ == "__main__":
    unittest.main()