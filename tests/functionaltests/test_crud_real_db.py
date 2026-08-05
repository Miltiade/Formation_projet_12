"""
Tests d'intégration DB réels pour Epic Events CRM.

=============================================================================
OBJECTIF
=============================================================================
Valider que les opérations CRUD (Create, Read, Update, Delete) fonctionnent
réellement avec la base de données MySQL, SANS aucun mocking sur la connexion.

=============================================================================
DIFFÉRENCE AVEC LES AUTRES TESTS
=============================================================================
| Test unitaire          | Mock DB | Vitesse | Coverage logique |
|------------------------|---------|---------|------------------|
| tests/unittests/*      | OUI     | ~5s     | Logique métier   |
| tests/functionaltests/*| PARTIEL | ~30s    | Services         |
| CE FICHIER             | NON     | ~45s    | Réalité physique |

=============================================================================
PROCÉDURE D'EXÉCUTION
=============================================================================
1. Vérifier que .env contient les bons credentials DB
2. Lancer prepare_test_db.py (UNE FOIS avant la première démo)
3. Lancer run_tests.py (inclut automatiquement ce fichier)
4. Vérifier que TOUS les tests passent (✅)

=============================================================================
NETTOYAGE DES DONNÉES
=============================================================================
Le nettoyage s'effectue APRÈS CHAQUE TEST (méthode tearDown).
Les IDs réservés pour les tests sont >= 900.
Aucun nettoyage n'est fait AVANT les tests pour permettre le debugging.
"""

import unittest
from utils.open_db_connection import get_db_connection
from app.controllers.write_data_to_db import DataWriter
from app.controllers.read_data_from_db import DataReader
from app.models.classes import Collaborator, Department, Client


class TestCRUDRealDB(unittest.TestCase):
    """
    Classe de tests d'intégration DB réels.
    
    Cette classe teste les opérations CRUD sur la base de données MySQL
    sans aucun mock sur la connexion. Toutes les assertions sont basées
    sur des lectures directes via SQL ou via les lecteurs officiels.
    
    Attributes:
        conn (pymysql.Connection): Connexion MySQL persistante pour tous les tests.
        cursor (pymysql.Cursor): Curseur pour exécuter les requêtes SQL.
        test_user_id (int): ID réservé pour l'utilisateur de test (999).
        test_client_id (int): ID réservé pour le client dummy (901).
    """
    
    # ========================================================================
    # CONFIGURATION CLASS - Exécutée UNE SEULE FOIS avant tous les tests
    # ========================================================================
    
    @classmethod
    def setUpClass(cls):
        """
        Initialise une connexion MySQL persistante pour tous les tests.
        
        Cette méthode crée une connexion partagée qui reste ouverte pendant
        toute l'exécution de la classe de tests. Cela évite d'ouvrir/fermer
        la connexion pour chaque test, ce qui accélère considérablement l'exécution.
        
        Configure également des IDs réservés pour éviter les conflits avec
        les données réelles de production :
            - test_user_id = 999 (collaborateur de test)
            - test_client_id = 901 (client dummy pour contrats)
        
        Raises:
            Exception: Si la connexion à la base de données échoue.
        
        Note:
            La connexion utilise les paramètres de utils/config.py qui
            eux-mêmes chargent les variables d'environnement depuis .env
        """
        print("\n" + "="*60)
        print("🔧 SETUP CLASS : Initialisation connexion DB pour tests CRUD réels")
        print("="*60)
        
        cls.conn = get_db_connection()
        cls.cursor = cls.conn.cursor()
        cls.test_user_id = 999
        cls.test_client_id = 901
        
        print(f"✓ Connexion établie avec succès")
        print(f"✓ ID utilisateur test réservé : {cls.test_user_id}")
        print(f"✓ ID client test réservé : {cls.test_client_id}")
        print("="*60 + "\n")
    
    # ========================================================================
    # NETTOYAGE APRÈS CHAQUE TEST - Garantie d'isolation
    # ========================================================================
    
    def tearDown(self):
        """
        Supprime toutes les données créées pendant ce test spécifique.
        
        Cette méthode est exécutée AUTOMATIQUEMENT après chaque méthode de test,
        que celui-ci ait réussi ou échoué. Elle supprime les données utilisant
        les IDs réservés (>900) pour garantir l'indépendance entre les tests.
        
        Important : Le nettoyage se fait APRÈS le test, pas avant.
        Ceci permet de laisser les données visibles si un test échoue,
        facilitant ainsi le debugging.
        
        Tables nettoyées :
            - events (id > 900)
            - contracts (id > 900)
            - clients (id > 900)
            - collaborators (id > 900)
        
        Note:
            Le commit est obligatoire après DELETE pour valider la suppression.
        """
        # Supprimer les tests orphelins
        self.cursor.execute("DELETE FROM events WHERE id > 900")
        self.cursor.execute("DELETE FROM contracts WHERE id > 900")
        self.cursor.execute("DELETE FROM clients WHERE id > 900")
        self.cursor.execute("DELETE FROM collaborators WHERE id > 900")
        self.conn.commit()
    
    # ========================================================================
    # TEST 1 : Création Client - Vérification d'INSERT physique
    # ========================================================================
    
    def test_create_client_persist_in_db(self):
        """
        Test critique : Vérifie qu'un client créé est physiquement stocké en MySQL.
        
        Scénario :
            1. Crée un utilisateur test (si inexistant) avec rôle Commercial
            2. Utilise DataWriter.create_client() pour créer un client
            3. Lit les données VIA UNE REQUÊTE SQL DIRECTE (sans passer par DataReader)
            4. Compare les valeurs écrites et lues
        
        Ce test détecte :
            - Erreurs d'INSERT silent (pas d'exception mais pas d'écriture)
            - Problèmes de types de données (DATE, VARCHAR, INT)
            - Violations de contraintes (clés étrangères, uniques)
            - Bugs dans la méthode create_client() de DataWriter
        
        Assertions :
            - La ligne existe bien en base (fetchone() != None)
            - Le nom complet correspond exactement
            - L'email correspond exactement
            - Le nom de l'entreprise correspond exactement
        
        Raises:
            AssertionError: Si les données écrites != données lues
            Exception: Toute erreur de connexion ou de requête SQL
        """
        print("\n--- Test 1: Création Client ---")
        
        # ÉTAPE 1 : Préparer un utilisateur de test (rôle Commercial requis)
        try:
            self.cursor.execute("SELECT id FROM collaborators WHERE id = %s", (self.test_user_id,))
            if not self.cursor.fetchone():
                # Utilisateur inexistant → le créer
                dept = Department("Commercial")
                temp_user = Collaborator(
                    id=self.test_user_id,
                    username="test_user_cli",
                    email="test_user@epicevents.com",
                    password="TempPass123!",
                    department=dept
                )
                writer_temp = DataWriter(None)  # Permissions bypassées pour setup
                writer_temp.create_collaborator(
                    username="test_user_cli",
                    email="test_user@epicevents.com",
                    password="TempPass123!",
                    department_name="Commercial"
                )
                print(f"✓ Utilisateur test créé (ID {self.test_user_id})")
        except Exception as e:
            self.fail(f"Échec de la création de l'utilisateur test : {e}")
        
        # ÉTAPE 2 : Créer le client VIA NOTRE CODE MÉTIER
        try:
            user = Collaborator(
                id=self.test_user_id,
                username="test_user_cli",
                email="test_user@epicevents.com",
                password="TempPass123!",  # Password hashé internement
                department=Department("Commercial")
            )
            writer = DataWriter(user)
            
            client_data = {
                "full_name": "Jean Dupont Test",
                "email": "jean.dupont@test-client.fr",
                "phone": "+33612345678",
                "company_name": "Entreprise Test SARL",
                "creation_date": "2025-08-05",
                "commercial_contact_id": self.test_user_id
            }
            
            client = writer.create_client(**client_data)
            print(f"✓ Client créé via DataWriter (ID {client.id})")
            
        except Exception as e:
            self.fail(f"Échec de la création du client via DataWriter : {e}")
        
        # ÉTAPE 3 : Lire les données PAR REQUÊTE SQL DIRECTE (绕过 DataReader)
        try:
            self.cursor.execute("""
                SELECT id, full_name, email, company_name 
                FROM clients 
                WHERE id = %s
            """, (client.id,))
            row = self.cursor.fetchone()
            
            if row is None:
                self.fail(f"Client ID {client.id} introuvable en base ! INSERT a échoué silencieusement.")
            
            print(f"✓ Données lues directement de MySQL")
            
        except Exception as e:
            self.fail(f"Échec de la lecture SQL directe : {e}")
        
        # ÉTAPE 4 : Comparaison ASSERTIVE
        self.assertEqual(row[1], client_data["full_name"],
                        "Le full_name stocké ne correspond pas à l'écriture")
        self.assertEqual(row[2], client_data["email"],
                        "L'email stocké ne correspond pas à l'écriture")
        self.assertEqual(row[3], client_data["company_name"],
                        "Le company_name stocké ne correspond pas à l'écriture")
        
        print(f"✅ Test 1 PASSÉ : Client correctement persisté en DB\n")
    
    # ========================================================================
    # TEST 2 : Création Contrat - Vérification des relations et contraintes
    # ========================================================================
    
    def test_create_contract_with_relations(self):
        """
        Test critique : Vérifie qu'un contrat s'écrit correctement avec ses relations.
        
        Scénario :
            1. S'assure qu'un client existe (utilise le dummy créé dans prepare_test_db.py)
            2. Crée un contrat via DataWriter.create_contract()
            3. Vérifie que les clés étrangères (client_id, commercial_contact_id) sont valides
            4. Lit le contrat via DataReader pour vérifier la cohérence
        
        Ce test détecte :
            - Erreurs de clés étrangères (client_id inexistant)
            - Problèmes de validation (montants négatifs, dates invalides)
            - Bugs dans le hachage ou le stockage des booléens (is_signed)
        
        Assertions :
            - Le contrat est créé avec un ID auto-incrémenté valide
            - Les montants sont stockés exactement (precision flottante)
            - Le booléen is_signed est correct (0 ou 1 en MySQL)
            - La lecture via DataReader retourne les mêmes données
        
        Pre-requisite:
            Un client doit exister en base (ID <= 900 ou préparer avec prepare_test_db.py)
        """
        print("\n--- Test 2: Création Contrat avec Relations ---")
        
        # Trouver un client existant (priorité au dummy ID 901, sinon chercher n'importe lequel)
        self.cursor.execute("SELECT id FROM clients WHERE id = %s", (self.test_client_id,))
        existing = self.cursor.fetchone()
        
        if existing:
            client_id_for_contract = existing[0]
            print(f"✓ Utilisation du client dummy ID {client_id_for_contract}")
        else:
            # Rechercher un client quelconque (fallback)
            self.cursor.execute("SELECT id FROM clients LIMIT 1")
            fallback = self.cursor.fetchone()
            if fallback:
                client_id_for_contract = fallback[0]
                print(f"⚠ Aucun client dummy trouvé. Utilisation du premier client disponible ID {client_id_for_contract}")
            else:
                self.fail("Aucun client trouvé en base ! Exécutez prepare_test_db.py d'abord.")
        
        # Préparer l'utilisateur test (rôle Commercial requis pour créer contrats)
        try:
            self.cursor.execute("SELECT id FROM collaborators WHERE id = %s", (self.test_user_id,))
            if not self.cursor.fetchone():
                # Créer l'utilisateur test s'il n'existe pas
                writer_temp = DataWriter(None)
                writer_temp.create_collaborator(
                    username="test_user_ctr",
                    email="test_user_ctr@epicevents.com",
                    password="TempPass123!",
                    department_name="Commercial"
                )
                print(f"✓ Utilisateur test créé (ID {self.test_user_id})")
        except Exception as e:
            print(f"⚠ Erreur utilisateur test (peut déjà exister) : {e}")
        
        # ÉTAPE 2 : Créer le contrat VIA NOTRE CODE MÉTIER
        try:
            user = Collaborator(
                id=self.test_user_id,
                username="test_user_ctr",
                email="test_user_ctr@epicevents.com",
                password="TempPass123!",
                department=Department("Commercial")
            )
            writer = DataWriter(user)
            
            contract_data = {
                "total_amount": 25000.50,
                "remaining_amount": 25000.50,
                "creation_date": "2025-08-05",
                "is_signed": True,
                "client_id": client_id_for_contract,
                "commercial_contact_id": self.test_user_id
            }
            
            contract = writer.create_contract(**contract_data)
            print(f"✓ Contrat créé via DataWriter (ID {contract.id})")
            
        except Exception as e:
            self.fail(f"Échec de la création du contrat via DataWriter : {e}")
        
        # ÉTAPE 3 : Lire via DataReader et vérifier cohérence
        try:
            reader = DataReader(user)
            read_contract = reader.get_contract_by_id(contract.id)
            
            if read_contract is None:
                self.fail(f"Contrat ID {contract.id} introuvable via DataReader !")
            
            print(f"✓ Contrat lu via DataReader")
            
        except Exception as e:
            self.fail(f"Échec de la lecture via DataReader : {e}")
        
        # ÉTAPE 4 : Assertions comparatives
        self.assertEqual(read_contract['total_amount'], 25000.50,
                        "Le total_amount ne correspond pas (problème de précision flottante ?)")
        self.assertEqual(read_contract['remaining_amount'], 25000.50,
                        "Le remaining_amount ne correspond pas")
        self.assertEqual(read_contract['is_signed'], True,
                        "Le statut is_signed ne correspond pas")
        self.assertEqual(read_contract['client_id'], client_id_for_contract,
                        "Le client_id lié ne correspond pas")
        
        print(f"✅ Test 2 PASSÉ : Contrat correctement persisté avec relations\n")
    
    # ========================================================================
    # TEST 3 : Cohérence Écriture/Lecture - Événement Complexe
    # ========================================================================
    
    def test_event_write_read_consistency(self):
        """
        Test critique : Vérifie que créer puis lire un événement retourne les MÊMES données.
        
        Scénario :
            1. S'assure qu'un contrat existe (pour la relation foreign key)
            2. Crée un événement complet via DataWriter.create_event()
            3. Lit immédiatement l'événement via DataReader.get_event_by_id()
            4. Compare TOUS les champs un par un
        
        Ce test détecte :
            - Pertes de données entre écriture et lecture
            - Problèmes de formatage (dates ISO, entiers, chaînes)
            - Champs manquants dans la requête SELECT de DataReader
            - Conversion erronée des types (NULL vs 0, True vs False)
        
        Assertions :
            - Tous les champs sont présents et égaux entre écriture et lecture
        
        Pre-requisite:
            Un contrat doit exister en base (créé par Test 2 ou prepare_test_db.py)
        """
        print("\n--- Test 3: Cohérence Écriture/Lecture Événement ---")
        
        # Trouver un contrat existant
        self.cursor.execute("SELECT id FROM contracts WHERE id > 0 ORDER BY id DESC LIMIT 1")
        contract_row = self.cursor.fetchone()
        
        if not contract_row:
            self.fail("Aucun contrat trouvé en base ! Test 2 doit passer en premier ou exécuter prepare_test_db.py")
        
        contract_id_for_event = contract_row[0]
        print(f"✓ Utilisation du contrat ID {contract_id_for_event} pour cet événement")
        
        # Préparer l'utilisateur (rôle Commercial ou Gestion requis pour créer événements)
        try:
            self.cursor.execute("SELECT id FROM collaborators WHERE id = %s", (self.test_user_id,))
            if not self.cursor.fetchone():
                writer_temp = DataWriter(None)
                writer_temp.create_collaborator(
                    username="test_user_evt",
                    email="test_user_evt@epicevents.com",
                    password="TempPass123!",
                    department_name="Commercial"
                )
        except Exception as e:
            print(f"⚠ Erreur utilisateur test : {e}")
        
        # ÉTAPE 2 : Créer l'événement VIA NOTRE CODE MÉTIER
        try:
            user = Collaborator(
                id=self.test_user_id,
                username="test_user_evt",
                email="test_user_evt@epicevents.com",
                password="TempPass123!",
                department=Department("Commercial")
            )
            writer = DataWriter(user)
            
            event_data = {
                "name": "Wedding Test Event 2025",
                "client_name": "Marie & Pierre",
                "client_contact": "marie@test.com, +33699999999",
                "date_start": "2025-12-15",
                "date_end": "2025-12-16",
                "location": "Château de Versailles",
                "attendees": 150,
                "notes": "Test complet - Événement de validation",
                "contract_id": contract_id_for_event,
                "support_contact_id": None  # Optionnel
            }
            
            event = writer.create_event(**event_data)
            print(f"✓ Événement créé via DataWriter (ID {event.id})")
            
        except Exception as e:
            self.fail(f"Échec de la création de l'événement via DataWriter : {e}")
        
        # ÉTAPE 3 : Lire via DataReader
        try:
            reader = DataReader(user)
            read_event = reader.get_event_by_id(event.id)
            
            if read_event is None:
                self.fail(f"Événement ID {event.id} introuvable via DataReader !")
            
            print(f"✓ Événement lu via DataReader")
            
        except Exception as e:
            self.fail(f"Échec de la lecture via DataReader : {e}")
        
        # ÉTAPE 4 : Comparaison champ par champ (TOUTES les données)
        comparisons = [
            ("name", event_data["name"]),
            ("client_name", event_data["client_name"]),
            ("client_contact", event_data["client_contact"]),
            ("date_start", event_data["date_start"]),
            ("date_end", event_data["date_end"]),
            ("location", event_data["location"]),
            ("attendees", event_data["attendees"]),
            ("notes", event_data["notes"]),
            ("contract_id", event_data["contract_id"]),
            ("support_contact_id", event_data["support_contact_id"])
        ]
        
        for field_name, expected_value in comparisons:
            actual_value = read_event.get(field_name)
            self.assertEqual(actual_value, expected_value,
                           f"Champ '{field_name}' : écrit={expected_value}, lu={actual_value}")
        
        print(f"✅ Test 3 PASSÉ : Événement cohérent écriture/lecture (10 champs vérifiés)\n")
    
    # ========================================================================
    # TEST 4 : Cycle Complet Authentification & Token JWT
    # ========================================================================
    
    def test_full_auth_token_cycle(self):
        """
        Test critique : Valide le cycle complet d'authentification et de génération de token.
        
        Scénario :
            1. Crée un utilisateur de test avec mot de passe connu
            2. Authentifie avec le bon mot de passe → doit réussir
            3. Authentifie avec un mauvais mot de passe → doit échouer
            4. Génère un token JWT pour l'utilisateur authentifié
            5. Décode le token et vérifie son contenu (user_id, role, exp)
            6. Vérifie que le token expire après délai (non testé ici par temps, mais structure OK)
        
        Ce test détecte :
            - Problèmes de hachage/mot de passe (hash incorrect, algorithme argon2)
            - Erreurs dans la génération JWT (clé secrète, algorithme HS256)
            - Décodage invalide du payload
            - Expiration non configurée correctement
        
        Modules testés :
            - app.controllers.authentication.UserManager.authenticate()
            - app.controllers.authentication.AuthService.create_token()
            - app.controllers.authentication.AuthService.decode_token()
        
        Assertions :
            - Authentification réussie avec bon mot de passe
            - Authentification échouée avec mauvais mot de passe
            - Token est une chaîne de 3 parties (header.payload.signature)
            - Payload contient user_id, role, et expiration
        """
        print("\n--- Test 4: Cycle Complet Authentification & Token ---")
        
        from app.controllers.authentication import UserManager, AuthService
        
        # ÉTAPE 1 : Créer un utilisateur test dédié
        auth_user_email = "auth_test@epicevents.com"
        auth_user_password = "SecureAuthPass123!"
        
        try:
            # Vérifier si l'utilisateur existe déjà
            self.cursor.execute("SELECT id FROM collaborators WHERE email = %s", (auth_user_email,))
            if self.cursor.fetchone():
                print(f"⚠ Utilisateur {auth_user_email} existe déjà, utilisation directe")
            else:
                writer_temp = DataWriter(None)
                writer_temp.create_collaborator(
                    username="auth_test_user",
                    email=auth_user_email,
                    password=auth_user_password,
                    department_name="Gestion"
                )
                print(f"✓ Utilisateur de test authentification créé")
        except Exception as e:
            self.fail(f"Échec de la création de l'utilisateur auth : {e}")
        
        # ÉTAPE 2 : Authentification avec BON mot de passe
        try:
            user_manager = UserManager()
            authenticated_user = user_manager.authenticate(auth_user_email, auth_user_password)
            
            if authenticated_user is None:
                self.fail("Authentification échouée avec le BON mot de passe !")
            
            print(f"✓ Authentification réussie (user_id={authenticated_user.id}, role={authenticated_user.role})")
            
        except Exception as e:
            self.fail(f"Exception lors de l'authentification : {e}")
        
        # ÉTAPE 3 : Authentification avec MAUVAIS mot de passe (doit échouer)
        try:
            failed_auth = user_manager.authenticate(auth_user_email, "WrongPassword999!")
            
            if failed_auth is not None:
                self.fail("Authentification réussie avec le MAUVAIS mot de passe ! C'est une faille de sécurité !")
            
            print(f"✓ Authentification échouée comme attendu avec mauvais mot de passe")
            
        except Exception as e:
            self.fail(f"Exception lors du test de mauvais mot de passe : {e}")
        
        # ÉTAPE 4 : Génération de token JWT
        try:
            token = AuthService.create_token(authenticated_user)
            
            if not isinstance(token, str):
                self.fail("Le token JWT doit être une chaîne de caractères !")
            
            # Token JWT standard a 3 parties séparées par des points
            parts = token.split(".")
            if len(parts) != 3:
                self.fail(f"Token JWT invalide : doit avoir 3 parties, trouvé {len(parts)}")
            
            print(f"✓ Token JWT généré ({len(token)} caractères)")
            
        except Exception as e:
            self.fail(f"Échec de la génération du token JWT : {e}")
        
        # ÉTAPE 5 : Décodage du token et vérification du payload
        try:
            payload = AuthService.decode_token(token)
            
            if payload is None:
                self.fail("Décodage du token a échoué (payload None) !")
            
            # Vérifier les champs essentiels du payload
            self.assertIn("user_id", payload, "Le payload JWT doit contenir 'user_id'")
            self.assertIn("role", payload, "Le payload JWT doit contenir 'role'")
            self.assertIn("exp", payload, "Le payload JWT doit contenir 'exp' (expiration)")
            
            self.assertEqual(payload["user_id"], authenticated_user.id,
                           "user_id dans le token ne correspond pas à l'utilisateur")
            self.assertEqual(payload["role"], authenticated_user.role,
                           "role dans le token ne correspond pas à l'utilisateur")
            
            print(f"✓ Token JWT décodé avec succès (user_id={payload['user_id']}, role={payload['role']})")
            
        except Exception as e:
            self.fail(f"Échec du décodage du token JWT : {e}")
        
        print(f"✅ Test 4 PASSÉ : Cycle authentification & token complet fonctionne\n")


# ==============================================================================
# FONCTION MAIN POUR EXÉCUTION DIRECTE (alternative à unittest.main())
# ==============================================================================

if __name__ == '__main__':
    """
    Point d'entrée alternatif pour exécuter ce fichier seul.
    
    Usage :
        python tests/functionaltests/test_crud_real_db.py
    
    Output attendu :
        ============================================================
        🔧 SETUP CLASS : Initialisation connexion DB...
        ============================================================
        
        --- Test 1: Création Client ---
        ✓ Utilisateur test créé...
        ✓ Client créé via DataWriter...
        ✅ Test 1 PASSÉ...
        
        ... (suite des tests) ...
        
        ============================================================
        ✅ TOUS LES TESTS PASSÉS — SYSTÈME PRÊT POUR DÉMO
        ============================================================
    """
    print("\n" + "="*60)
    print("🚀 DÉMARRAGE DES TESTS CRUD RÉELS (Fichier seul)")
    print("="*60 + "\n")
    
    # Configuration de l'exécution verbosité
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCRUDRealDB)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Bannière finale selon résultat
    if result.wasSuccessful():
        print("\n" + "="*60)
        print("✅ TOUS LES TESTS CRUD RÉELS ONT RÉUSSI")
        print("   Système prêt pour présentation client")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ ERREURS DÉTECTÉES DANS LES TESTS CRUD")
        print("   NE PAS CONTINUER VERS LA DÉMO")
        print("="*60)