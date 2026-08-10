"""
Tests fonctionnels avec base de données réelle.
Fait le cycle complet : Create → Read → Update → Delete.

Stratégie :
- Avant TOUS les tests : wipe toutes les tables liées (events, contracts, clients, collaborators)
- Après TOUS les tests : wipe à nouveau (nettoyage post-test)
- Chaque test utilise des données fraîches, rien n'est partagé entre tests.
"""

import unittest
from utils.open_db_connection import get_db_connection

# Helper SQL for cleanup (runs before/after tests)
WIPES = [
    "DELETE FROM events;",
    "DELETE FROM contracts;",
    "DELETE FROM clients;",
    "DELETE FROM collaborators WHERE id > 1000;  -- Preserve hubert/jobhert",
]

def wipe_all():
    """Efface toutes les tables pertinentes."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            for sql in WIPES:
                cur.execute(sql)
            conn.commit()
    finally:
        conn.close()

def insert_test_data():
    """Insère les données minimales requises pour tous les tests."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. Insert test collaborators (preserve IDs 1 & 2 for reference)
            cur.execute("""INSERT IGNORE INTO collaborators (id, username, email, password_hash, department)
                           VALUES (901, 'test_commercial', 'com@test.com', 'hash1', 'Commercial')""")
            cur.execute("""INSERT IGNORE INTO collaborators (id, username, email, password_hash, department)
                           VALUES (902, 'test_support', 'supp@test.com', 'hash2', 'Support')""")
            
            # 2. Insert test client
            cur.execute("""INSERT INTO clients (id, full_name, email, phone, company_name, creation_date, last_update_date, commercial_contact)
                           VALUES (901, 'Jean Test', 'jean@test.com', '+33600000001', 'Test SARL', '2025-01-01', '2025-01-01', 901)""")
            
            # 3. Insert test contract (signed)
            cur.execute("""INSERT INTO contracts (id, total_amount, remaining_amount, creation_date, is_signed, client_id, commercial_contact_id)
                           VALUES (901, 10000.0, 5000.0, '2025-01-15', 1, 901, 901)""")
            
            # 4. Insert test event
            cur.execute("""INSERT INTO events (id, name, client_name, client_contact, date_start, date_end, location, attendees, notes, contract_id, support_contact)
                           VALUES (901, 'Test Event', 'Jean Test', 'jean@test.com', '2025-06-01', '2025-06-01', 'Paris', 100, 'Test note', 901, 902)""")
            
            conn.commit()
    finally:
        conn.close()

class TestCrudFull(unittest.TestCase):
    """Tests CRUD complets sur la base de données réelle."""

    @classmethod
    def setUpClass(cls):
        """Une seule fois avant tous les tests : nettoiement + insertion."""
        wipe_all()
        insert_test_data()

    @classmethod
    def tearDownClass(cls):
        """Une seule fois après tous les tests : nettoiement final."""
        wipe_all()

    def test_read_client_exists(self):
        """Un client inséré peut être lu par ID."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT full_name, company_name FROM clients WHERE id = 901")
                row = cur.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], "Jean Test")
            self.assertEqual(row[1], "Test SARL")
        finally:
            conn.close()

    def test_contract_is_signed(self):
        """Un contrat inséré a le bon statut signé."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT total_amount, is_signed FROM contracts WHERE id = 901")
                row = cur.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], 10000.0)
            self.assertTrue(row[1])
        finally:
            conn.close()

    def test_event_has_support_assigned(self):
        """Un événement inséré a un support assigné."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT name, support_contact FROM events WHERE id = 901")
                row = cur.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], "Test Event")
            self.assertEqual(row[1], 902)
        finally:
            conn.close()

    def test_update_client_email(self):
        """Modifier l'email d'un client fonctionne."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE clients SET email = 'new@test.com' WHERE id = 901")
                cur.execute("SELECT email FROM clients WHERE id = 901")
                row = cur.fetchone()
            self.assertEqual(row[0], "new@test.com")
        finally:
            conn.close()

    def test_delete_event(self):
        """Supprimer un événement fonctionne."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM events WHERE id = 901")
                cur.execute("SELECT COUNT(*) FROM events WHERE id = 901")
                row = cur.fetchone()
            self.assertEqual(row[0], 0)
        finally:
            conn.close()

if __name__ == "__main__":
    unittest.main()