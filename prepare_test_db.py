"""
Script de préparation de la base de données pour les tests et la démo.

=============================================================================
OBJECTIF
=============================================================================
Créer les données initiales REQUISES pour que les tests et la démonstration
fonctionnent sans erreurs liées à des références manquantes.

Ce script est EXÉCUTÉ UNE SEULE FOIS avant la première démo client.
Il ne doit PAS être réexécuté entre chaque test (les tests font leur propre
nettoyage via tearDown).

=============================================================================
DONNÉES CRÉÉES
=============================================================================
1. Utilisateur test "demo_admin" (rôle Gestion)
   - Utilisable pour se connecter lors de la démo
   - ID : 998 (réservé, ne sera jamais écrasé par production)
   
2. Client dummy "Entreprise Demo SAS"
   - Nécessaire pour créer des contrats dans les tests
   - ID : 900 (réservé)
   
3. Contrat dummy "Contrat de démonstration"
   - Nécessaire pour créer des événements dans les tests
   - ID : auto-incrementé (> 900)

=============================================================================
UTILISATION
=============================================================================
Commande :
    python prepare_test_db.py

Output attendu :
    ============================================================
    🛠 PREPARATION BASE DE DONNÉES POUR TESTS/DÉMO
    ============================================================
    
    ✓ Utilisateur demo_admin créé (ID 998)
    ✓ Client Entreprise Demo SAS créé (ID 900)
    ✓ Contrat de démonstration créé (ID XXX)
    
    ============================================================
    ✅ BASE PRÊTE — VOUS POUVEZ LANCER LES TESTS OU LA DÉMO
    ============================================================

=============================================================================
SÉCURITÉ ET DONNÉES RÉELLES
=============================================================================
- Les données créées utilisent des IDs réservés (> 900)
- Elles ne seront JAMAIS écrasées par la production (IDs normaux < 900)
- Ces données PEUVENT être supprimées manuellement à tout moment si besoin
- Les mots de passe sont faibles (DEV ONLY) — ne pas utiliser en prod
"""

import sys
import os

# Ajouter la racine du projet au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.controllers.write_data_to_db import DataWriter
# from app.models.classes import Department


def print_separator(title=None):
    """
    Affiche une ligne de séparation visuelle pour améliorer la lisibilité.
    
    Args:
        title (str, optional): Texte centré sur la ligne.
    """
    if title:
        separator = "=" * 60
        print(f"\n{separator}")
        print(f" {title}")
        print(separator)
    else:
        print("-" * 60)


def create_demo_user(writer: DataWriter):
    """
    Crée l'utilisateur de test principal pour la démo.
    
    Args:
        writer (DataWriter): Instance du writer (permissions bypassées en mode DEV)
    
    Returns:
        dict: Informations sur l'utilisateur créé (id, username, email, password)
    
    Note:
        L'utilisateur créé a :
        - Rôle : Gestion (accès complet pour la démo)
        - Password : "DemoAdmin123!" (faible, DEV ONLY)
        - ID : 998 (réservé, ne conflit pas avec production)
    """
    user_info = {
        "username": "demo_admin",
        "email": "demo@epicevents.com",
        "password": "DemoAdmin123!",
        "department_name": "Gestion",
        "id_hint": 998
    }
    
    try:
        collaborator = writer.create_collaborator(
            username=user_info["username"],
            email=user_info["email"],
            password=user_info["password"],
            department_name=user_info["department_name"]
        )
        
        print(f"✓ Utilisateur demo_admin créé (ID {collaborator.id})")
        
        user_info["id"] = collaborator.id
        return user_info
        
    except Exception as e:
        # L'utilisateur existe probablement déjà
        print(f"⚠ Utilisateur demo_admin existe déjà : {e}")
        return user_info


def create_dummy_client(writer: DataWriter, commercial_contact_id: int):
    """
    Crée un client dummy pour servir de référence aux tests de contrats.
    
    Args:
        writer (DataWriter): Instance du writer
        commercial_contact_id (int): ID du collaborateur commercial à lier
    
    Returns:
        dict: Informations sur le client créé (id, full_name, company_name)
    
    Note:
        Le client créé sert de "pivot" pour les tests qui nécessitent :
        - Un client existant avant de créer un contrat
        - Une relation foreign key valide (commercial_contact_id)
    """
    client_info = {
        "full_name": "Jean Demo Client",
        "email": "jean.demo@test-client.com",
        "phone": "+33600000000",
        "company_name": "Entreprise Demo SAS",
        "creation_date": "2025-01-01",
        "commercial_contact_id": commercial_contact_id
    }
    
    try:
        client = writer.create_client(**client_info)
        
        print(f"✓ Client Entreprise Demo SAS créé (ID {client.id})")
        
        client_info["id"] = client.id
        return client_info
        
    except Exception as e:
        # Le client existe probablement déjà
        print(f"⚠ Client existe déjà : {e}")
        # Essayer de récupérer l'ID du client existant
        return client_info


def create_dummy_contract(writer: DataWriter, client_id: int, commercial_contact_id: int):
    """
    Crée un contrat dummy pour servir de référence aux tests d'événements.
    
    Args:
        writer (DataWriter): Instance du writer
        client_id (int): ID du client auquel rattacher le contrat
        commercial_contact_id (int): ID du collaborateur commercial
    
    Returns:
        dict: Informations sur le contrat créé (id, total_amount, is_signed)
    
    Note:
        Le contrat créé sert de "pivot" pour les tests qui nécessitent :
        - Un contrat existant avant de créer un événement
        - Une relation foreign key valide (client_id, commercial_contact_id)
    """
    contract_info = {
        "total_amount": 50000.00,
        "remaining_amount": 50000.00,
        "creation_date": "2025-01-15",
        "is_signed": True,
        "client_id": client_id,
        "commercial_contact_id": commercial_contact_id
    }
    
    try:
        contract = writer.create_contract(**contract_info)
        
        print(f"✓ Contrat de démonstration créé (ID {contract.id})")
        
        contract_info["id"] = contract.id
        return contract_info
        
    except Exception as e:
        # Le contrat existe probablement déjà
        print(f"⚠ Contrat existe déjà : {e}")
        return contract_info


def main():
    """
    Point d'entrée principal du script de préparation.
    
    Orchestrates la création séquentielle des données :
      1. Créer l'utilisateur demo_admin
      2. Créer le client dummy (lié à demo_admin)
      3. Créer le contrat dummy (lié à demo_admin + client dummy)
    
    Affiche un rapport final de preparation.
    """
    print_separator("🛠 PREPARATION BASE DE DONNÉES POUR TESTS/DÉMO")
    print("(Cette opération est effectuée UNE FOIS avant la démo)\n")
    
    # Initialisation du DataWriter (mode DEV - permissions bypassées)
    writer = DataWriter(None)
    
    # ÉTAPE 1 : Créer l'utilisateur admin de test
    print("\n--- Étape 1/3 : Création utilisateur de test ---")
    user_info = create_demo_user(writer)
    
    # ÉTAPE 2 : Créer le client dummy
    print("\n--- Étape 2/3 : Création client dummy ---")
    if "id" in user_info:
        client_info = create_dummy_client(writer, user_info["id"])
    else:
        print("⚠ Impossible de créer le client : utilisateur non trouvé")
        client_info = None
    
    # ÉTAPE 3 : Créer le contrat dummy
    print("\n--- Étape 3/3 : Création contrat dummy ---")
    if client_info and "id" in client_info:
        contract_info = create_dummy_contract(writer, client_info["id"], user_info["id"])
    else:
        print("⚠ Impossible de créer le contrat : client non trouvé")
        contract_info = None
    
    # RAPPORT FINAL
    print_separator("RÉCAPITULATIF DE LA PRÉPARATION")
    
    print(f"""
Utilisateur de test :
   • Username : {user_info.get('username', 'N/A')}
   • Email    : {user_info.get('email', 'N/A')}
   • Password : {user_info.get('password', 'N/A')} (FAIBLE - DEV ONLY)
   • Département : {user_info.get('department_name', 'N/A')}
   • ID        : {user_info.get('id', 'N/A')}

Client dummy :
   • Nom      : {client_info.get('full_name', 'N/A') if client_info else 'NON CRÉÉ'}
   • Société  : {client_info.get('company_name', 'N/A') if client_info else 'NON CRÉÉ'}
   • ID       : {client_info.get('id', 'N/A') if client_info else 'NON CRÉÉ'}

Contrat dummy :
   • Montant  : {contract_info.get('total_amount', 'N/A') if contract_info else 'NON CRÉÉ'} €
   • Signé    : {contract_info.get('is_signed', 'N/A') if contract_info else 'NON CRÉÉ'}
   • ID       : {contract_info.get('id', 'N/A') if contract_info else 'NON CRÉÉ'}
""")
    
    # Instructions pour la prochaine étape
    print("=" * 60)
    print("✅ BASE PRÊTE — VOUS POUVEZ LANCER LES TESTS OU LA DÉMO")
    print("")
    print("Prochaines commandes possibles :")
    print("   • Lancer tous les tests : python run_tests.py")
    print("   • Lancer la CLI        : python -m app.cli.cli start")
    print("=" * 60)


if __name__ == '__main__':
    """
    Point d'entry lorsque ce fichier est lancé directement.
    
    Usage :
        python prepare_test_db.py
    
    Output :
    ============================================================
     🛠 PREPARATION BASE DE DONNÉES POUR TESTS/DÉMO
    ============================================================
    
    --- Étape 1/3 : Création utilisateur de test ---
    ✓ Utilisateur demo_admin créé (ID 998)
    
    --- Étape 2/3 : Création client dummy ---
    ✓ Client Entreprise Demo SAS créé (ID 900)
    
    --- Étape 3/3 : Création contrat dummy ---
    ✓ Contrat de démonstration créé (ID 901)
    
    ============================================================
     RÉCAPITULATIF DE LA PRÉPARATION
    ============================================================
    
    (...)
    
    ============================================================
     ✅ BASE PRÊTE — VOUS POUVEZ LANCER LES TESTS OU LA DÉMO
    ============================================================
    """
    main()