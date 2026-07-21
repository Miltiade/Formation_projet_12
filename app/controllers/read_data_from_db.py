from typing import Optional
from app.models.classes import Collaborator
from utils.open_db_connection import get_db_connection
from app.controllers.authorizations import has_permission


class DataReader:
    """Classe pour lire les données clients, contrats, événements depuis la BDD.
    NB : authentification et permissions de l'utilisateur sont toujours vérifiées AVANT la lecture des données."""

    def __init__(self, user: Optional[Collaborator]):
        """
        Args:
            user (Collaborator | None): Utilisateur authentifié, ou None si non authentifié.
        """
        self.user = user

    def _fetch_all(self, query: str) -> list[tuple]:
        """Exécute une requête SELECT et retourne toutes les lignes."""
        try:
            conn = get_db_connection()
        except Exception as e:
            print(f"ERREUR: connexion BDD impossible : {e}")
            raise
        
        try:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
            return rows
        finally:
            conn.close()

    # ==================== COLLABORATORS ====================
    
    def get_all_collaborators(self) -> list[dict]:
        """
        Récupère tous les collaborateurs si l'utilisateur a la permission.
        Returns:
            list[dict]: Liste de collaborateurs sous forme de dictionnaires.
        Raises:
            PermissionError: Si l'utilisateur n'a pas la permission ou n'est pas authentifié.
        """
        if self.user is None:
            raise PermissionError("Utilisateur non authentifié.")
        if not has_permission(self.user, "view_all_clients"):  # Using common read permission
            raise PermissionError("Permission insuffisante pour voir les collaborateurs.")
        
        rows = self._fetch_all(
            "SELECT id, username, email, department FROM collaborators"
        )
        collaborators = [
            {
                "id": r[0],
                "username": r[1],
                "email": r[2],
                "department": r[3]
            }
            for r in rows
        ]
        return collaborators

    def get_collaborator_by_id(self, collaborator_id: int) -> dict:
        """
        Récupère un collaborateur par ID.
        Returns:
            dict: Collaborateur sous forme de dictionnaire.
        Raises:
            LookupError: Si collaborateur non trouvé.
            PermissionError: Si utilisateur non authentifié.
        """
        if self.user is None:
            raise PermissionError("Utilisateur non authentifié.")
        
        rows = self._fetch_all(
            "SELECT id, username, email, department FROM collaborators WHERE id = %s",
        )
        # Execute with parameterized query
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, username, email, department FROM collaborators WHERE id = %s",
                    (collaborator_id,)
                )
                row = cur.fetchone()
                if row is None:
                    raise LookupError(f"Collaborateur ID {collaborator_id} introuvable.")
                
                return {
                    "id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "department": row[3]
                }
        finally:
            conn.close()

    # ==================== CLIENTS ====================
    
    def get_all_clients(self) -> list[dict]:
        """
        Récupère tous les clients si l'utilisateur a la permission.
        Returns:
            list[dict]: Liste de clients sous forme de dictionnaires.
        Raises:
            PermissionError: Si l'utilisateur n'a pas la permission ou n'est pas authentifié.
        """
        if self.user is None:
            raise PermissionError("Utilisateur non authentifié.")
        if not has_permission(self.user, "view_all_clients"):
            raise PermissionError("Permission insuffisante pour voir tous les clients.")
        
        rows = self._fetch_all(
            "SELECT id, full_name, email, phone, company_name, creation_date, commercial_contact FROM clients"
        )
        clients = [
            {
                "id": r[0],
                "full_name": r[1],
                "email": r[2],
                "phone": r[3],
                "company_name": r[4],
                "creation_date": r[5],
                "commercial_contact": r[6]
            }
            for r in rows
        ]
        return clients

    def get_client_by_id(self, client_id: int) -> dict:
        """
        Récupère un client par ID.
        Returns:
            dict: Client sous forme de dictionnaire.
        Raises:
            LookupError: Si client non trouvé.
            PermissionError: Si utilisateur non authentifié.
        """
        if self.user is None:
            raise PermissionError("Utilisateur non authentifié.")
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, full_name, email, phone, company_name, creation_date, commercial_contact FROM clients WHERE id = %s",
                    (client_id,)
                )
                row = cur.fetchone()
                if row is None:
                    raise LookupError(f"Client ID {client_id} introuvable.")
                
                return {
                    "id": row[0],
                    "full_name": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "company_name": row[4],
                    "creation_date": row[5],
                    "commercial_contact": row[6]
                }
        finally:
            conn.close()

    # ==================== CONTRACTS ====================
    
    def get_all_contracts(self) -> list[dict]:
        """
        Récupère tous les contrats si l'utilisateur a la permission.
        Returns:
            list[dict]: Liste des contrats.
        Raises:
            PermissionError: Si l'utilisateur n'a pas la permission ou n'est pas authentifié.
        """
        if self.user is None:
            raise PermissionError("Utilisateur non authentifié.")
        if not has_permission(self.user, "view_all_contracts"):
            raise PermissionError("Permission insuffisante pour voir tous les contrats.")

        rows = self._fetch_all(
            "SELECT id, total_amount, remaining_amount, creation_date, is_signed, client_id, commercial_contact_id FROM contracts"
        )
        contracts = [
            {
                "id": r[0],
                "total_amount": r[1],
                "remaining_amount": r[2],
                "creation_date": r[3],
                "is_signed": r[4],
                "client_id": r[5],
                "commercial_contact_id": r[6]
            }
            for r in rows
        ]
        return contracts

    def get_contract_by_id(self, contract_id: int) -> dict:
        """
        Récupère un contrat par ID.
        Returns:
            dict: Contrat sous forme de dictionnaire.
        Raises:
            LookupError: Si contrat non trouvé.
            PermissionError: Si utilisateur non authentifié.
        """
        if self.user is None:
            raise PermissionError("Utilisateur non authentifié.")
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, total_amount, remaining_amount, creation_date, is_signed, client_id, commercial_contact_id FROM contracts WHERE id = %s",
                    (contract_id,)
                )
                row = cur.fetchone()
                if row is None:
                    raise LookupError(f"Contrat ID {contract_id} introuvable.")
                
                return {
                    "id": row[0],
                    "total_amount": row[1],
                    "remaining_amount": row[2],
                    "creation_date": row[3],
                    "is_signed": row[4],
                    "client_id": row[5],
                    "commercial_contact_id": row[6]
                }
        finally:
            conn.close()

    # ==================== EVENTS ====================
    
    def get_all_events(self) -> list[dict]:
        """
        Récupère tous les événements si l'utilisateur a la permission.
        Returns:
            list[dict]: Liste des événements.
        Raises:
            PermissionError: Si l'utilisateur n'a pas la permission ou n'est pas authentifié.
        """
        if self.user is None:
            raise PermissionError("Utilisateur non authentifié.")
        if not has_permission(self.user, "view_all_events"):
            raise PermissionError("Permission insuffisante pour voir tous les événements.")

        rows = self._fetch_all(
            "SELECT id, title, description, start_date, end_date, contract_id FROM events"
        )
        events = [
            {
                "id": r[0],
                "title": r[1],
                "description": r[2],
                "start_date": r[3],
                "end_date": r[4],
                "contract_id": r[5]
            }
            for r in rows
        ]
        return events

    def get_event_by_id(self, event_id: int) -> dict:
        """
        Récupère un événement par ID.
        Returns:
            dict: Événement sous forme de dictionnaire.
        Raises:
            LookupError: Si événement non trouvé.
            PermissionError: Si utilisateur non authentifié.
        """
        if self.user is None:
            raise PermissionError("Utilisateur non authentifié.")
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, title, description, start_date, end_date, contract_id FROM events WHERE id = %s",
                    (event_id,)
                )
                row = cur.fetchone()
                if row is None:
                    raise LookupError(f"Événement ID {event_id} introuvable.")
                
                return {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "start_date": row[3],
                    "end_date": row[4],
                    "contract_id": row[5]
                }
        finally:
            conn.close()