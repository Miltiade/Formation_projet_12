from datetime import date
from typing import Optional
from app.models.classes import Collaborator, Department
from utils.open_db_connection import get_db_connection
from app.controllers.authorizations import has_permission
import pymysql
from argon2 import PasswordHasher

ph = PasswordHasher()

class DataWriter:
    """Classe pour créer et modifier les données dans la BDD,
    après vérification d'authentification et permissions."""

    def __init__(self, user: Optional[Collaborator]):
        self.user = user

    def create_collaborator(self, username: str, email: str, password: str, department_name: str) -> Collaborator:
        """Crée un nouveau collaborateur en base, après vérification des permissions et validation.
        
        Args:
            username (str): Nom d'utilisateur unique.
            email (str): Email valide.
            password (str): Mot de passe en clair.
            department_name (str): Nom du département ("Gestion","Commercial","Support").
        
        Raises:
            PermissionError: si pas la permission.
            ValueError: si données invalides.
            pymysql.MySQLError: erreur base de données.
        Returns:
            Collaborator: instance du collaborateur créé.
        """
        if self.user is None or not has_permission(self.user, "create_collaborator"):
            raise PermissionError("Permission refusée pour créer un collaborateur.")

        # Validation simple
        if not username.strip():
            raise ValueError("Username ne peut pas être vide.")
        if not email.strip() or "@" not in email:
            raise ValueError("Email invalide.")
        if not password:
            raise ValueError("Mot de passe requis.")
        try:
            department = Department(department_name)
        except ValueError as ve:
            raise ValueError(f"Département invalide : {ve}")

        # Hachage du mot de passe avec argon2 (copie du modèle Collaborator)
        password_hash = ph.hash(password)

        sql = """
        INSERT INTO collaborators (username, email, password_hash, department)
        VALUES (%s, %s, %s, %s)
        """
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute(sql, (username, email, password_hash, department.name))
                conn.commit()
                collaborator_id = cur.lastrowid
        finally:
            conn.close()

        return Collaborator(collaborator_id, username, email, password, department)
    
    def update_collaborator(self, collaborator_id: int,
                            username: Optional[str] = None,
                            email: Optional[str] = None,
                            password: Optional[str] = None,
                            department_name: Optional[str] = None) -> None:
        """
        Met à jour un collaborateur existant.
        Vérifie permissions, valide données, hache password si modifié.
        
        Args:
            collaborator_id (int): ID du collaborateur à modifier.
            username (str|None): Nouveau username.
            email (str|None): Nouveau email.
            password (str|None): Nouveau mot de passe clair.
            department_name (str|None): Nouveau département.

        Raises:
            PermissionError: si pas la permission.
            ValueError: si données invalides.
            pymysql.MySQLError: erreur base.
            LookupError: si collaborateur non trouvé.
        """
        if self.user is None or not has_permission(self.user, "update_collaborator"):
            raise PermissionError("Permission refusée pour modifier un collaborateur.")

        updates = []
        params = []
        
        if username is not None:
            if not username.strip():
                raise ValueError("Username ne peut pas être vide.")
            updates.append("username = %s")
            params.append(username)

        if email is not None:
            if not email.strip() or "@" not in email:
                raise ValueError("Email invalide.")
            updates.append("email = %s")
            params.append(email)

        if password is not None:
            password_hash = ph.hash(password)
            updates.append("password_hash = %s")
            params.append(password_hash)

        if department_name is not None:
            try:
                department = Department(department_name)
            except ValueError as ve:
                raise ValueError(f"Département invalide : {ve}")
            updates.append("department = %s")
            params.append(department.name)

        if not updates:
            raise ValueError("Aucun champ à mettre à jour fourni.")

        # Construction requête
        sql = f"UPDATE collaborators SET {', '.join(updates)} WHERE id = %s"
        params.append(collaborator_id)

        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM collaborators WHERE id = %s", (collaborator_id,))
                count = cur.fetchone()[0]
                if count == 0:
                    raise LookupError(f"Collaborateur ID {collaborator_id} non trouvé.")

                cur.execute(sql, tuple(params))
                conn.commit()
        finally:
            conn.close()
    
    def create_contract(self, total_amount: float, remaining_amount: float, creation_date: str, is_signed: bool, client_id: int, commercial_contact_id: int) -> Contract:
        """
        Crée un nouveau contrat en base après vérification des données et permissions.

        Args:
            total_amount (float): montant total, > 0.
            remaining_amount (float): montant restant dû, >= 0 et <= total_amount.
            creation_date (str): date ISO (YYYY-MM-DD).
            is_signed (bool): si signé.
            client_id (int): ID client existant.
            commercial_contact_id (int): ID collaborateur commercial.

        Raises:
            PermissionError, ValueError, LookupError, pymysql.MySQLError.
        Returns:
            Contract: instance créée.
        """

        # Vérifier permission
        if self.user is None:
            raise PermissionError("Utilisateur non authentifié.")

        if self.user.role == "commercial":
            # Droit commercial uniquement sur ses contrats assignés
            if not has_permission(self.user, "create_client"):
                raise PermissionError("Permission insuffisante pour créer un contrat.")
        elif self.user.role == "gestion":
            if not has_permission(self.user, "create_contract"):
                raise PermissionError("Permission insuffisante pour créer un contrat.")
        else:
            raise PermissionError("Permission insuffisante.")

        # Valider montants
        if total_amount <= 0:
            raise ValueError("Le montant total doit être positif.")
        if remaining_amount < 0 or remaining_amount > total_amount:
            raise ValueError("Montant restant incohérent.")

        # Valider date ISO
        try:
            date.fromisoformat(creation_date)
        except ValueError:
            raise ValueError("Date de création invalide, format attendu AAAA-MM-JJ.")
