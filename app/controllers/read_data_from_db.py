from typing import Optional
from app.models.classes import Collaborator
from utils.open_db_connection import get_db_connection
from app.controllers.authorizations import has_permission


class DataReader:
    """Classe pour lire les données clients, contrats, événements depuis la BDD.
    NB : authentification et permissions de l'utilisateur sont toujours vérifiées avant la lecture des données."""

    def __init__(self, user: Optional[Collaborator]):
        """
        Args:
            user (Collaborator | None): Utilisateur authentifié, ou None si non authentifié.
        """
        self.user = user
        print(user)

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
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email FROM clients")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Convertir les tuples en dict simples
        clients = [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]
        print(clients)
        return clients
        
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

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, client_id, amount, status FROM contracts")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        contracts = [{"id": r[0], "client_id": r[1], "amount": r[2], "status": r[3]} for r in rows]
        print(contracts)
        return contracts

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

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, contract_id, date_event, location FROM events")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        events = [{"id": r[0], "contract_id": r[1], "date_event": r[2], "location": r[3]} for r in rows]
        print(events)
        return events