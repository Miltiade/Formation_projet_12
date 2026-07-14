from datetime import date
from typing import Optional
from app.models.classes import Collaborator, Department, Client
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

    def get_collaborator_by_id(self, collaborator_id: int) -> Collaborator:
        """Récupère un collaborateur par ID. Lève LookupError si introuvable."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                sql = "SELECT id, username, email, password_hash, department FROM collaborators WHERE id = %s"
                cur.execute(sql, (collaborator_id,))
                row = cur.fetchone()
                if row is None:
                    raise LookupError(f"Collaborator ID {collaborator_id} non trouvé.")

                id_, username, email, password_hash, department_name = row
                department = Department(department_name)
                collaborator = Collaborator(id=id_, username=username, email=email, password=password_hash, department=department)
                # Remplacer le hash généré par celui en base, pour cohérence
                collaborator._Collaborator__password_hash = password_hash
                return collaborator
        finally:
            conn.close()

    def get_client_by_id(self, client_id: int) -> Client:
        """Récupère un client par ID avec son commercial_contact associé. Lève LookupError si introuvable."""
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Récupérer client et id commercial_contact
                sql = """
                SELECT full_name, email, phone, company_name, creation_date, last_update_date, commercial_contact
                FROM clients
                WHERE id = %s
                """
                cur.execute(sql, (client_id,))
                row = cur.fetchone()
                if row is None:
                    raise LookupError(f"Client ID {client_id} non trouvé.")

                full_name, email, phone, company_name, creation_date, last_update_date, commercial_contact_id = row

                # Récupérer le commercial_contact complet
                commercial_contact = self.get_collaborator_by_id(commercial_contact_id)

                return Client(
                    full_name=full_name,
                    email=email,
                    phone=phone,
                    company_name=company_name,
                    creation_date=creation_date,
                    last_update_date=last_update_date,
                    commercial_contact=commercial_contact,
                )
        finally:
            conn.close()

    def get_contract_by_id(self, contract_id: int) -> Contract:
        """
        Récupère un contrat par ID avec ses relations client et collaborateur.
        Lève LookupError si introuvable.

        Args:
            contract_id (int): ID du contrat.

        Returns:
            Contract: instance complète.

        Raises:
            LookupError: si contrat non trouvé.
        """
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                sql = """
                SELECT total_amount, remaining_amount, creation_date, is_signed, client_id, commercial_contact_id
                FROM contracts
                WHERE id = %s
                """
                cur.execute(sql, (contract_id,))
                row = cur.fetchone()
                if row is None:
                    raise LookupError(f"Contrat ID {contract_id} non trouvé.")

                total_amount, remaining_amount, creation_date, is_signed, client_id, commercial_contact_id = row

                # Récupérer les objets liés en réutilisant vos méthodes existantes
                client_obj = self.get_client_by_id(client_id)
                commercial_obj = self.get_collaborator_by_id(commercial_contact_id)

                return Contract(contract_id, total_amount, remaining_amount, creation_date, is_signed, client_obj, commercial_obj)
        finally:
            conn.close()

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

        client_obj = self.get_client_by_id(client_id)
        commercial_obj = self.get_collaborator_by_id(commercial_contact_id)

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
        
        # Insertion en base
        sql = """
            INSERT INTO contracts (total_amount, remaining_amount, creation_date, is_signed, client_id, commercial_contact_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute(sql, (total_amount, remaining_amount, creation_date, is_signed, client_id, commercial_contact_id))
                conn.commit()
                contract_id = cur.lastrowid
        finally:
            conn.close()

        # Retourner l’objet Contract avec l’id généré
        return Contract(contract_id, total_amount, remaining_amount, creation_date, is_signed, client_obj, commercial_obj)

    def update_contract(self, contract_id: int,
                        total_amount: Optional[float] = None,
                        remaining_amount: Optional[float] = None,
                        creation_date: Optional[str] = None,
                        is_signed: Optional[bool] = None,
                        client_id: Optional[int] = None,
                        commercial_contact_id: Optional[int] = None) -> None:
        """
        Met à jour un contrat existant.
        Vérifie permissions, valide données, met à jour relationnels.

        Args:
            contract_id (int): ID du contrat à modifier.
            total_amount (float|None): Nouveau montant total (>0).
            remaining_amount (float|None): Nouveau montant restant (>=0 et <= total_amount).
            creation_date (str|None): Nouvelle date ISO (AAAA-MM-JJ).
            is_signed (bool|None): Nouveau statut signé.
            client_id (int|None): Nouveau client lié.
            commercial_contact_id (int|None): Nouveau collaborateur commercial.

        Raises:
            PermissionError: si pas la permission.
            ValueError: en cas de données invalides.
            LookupError: si contrat, client ou collaborateur non trouvé.
            pymysql.MySQLError: erreur base.
        """

        # Vérifier utilisateur et permission
        if self.user is None:
            raise PermissionError("Utilisateur non authentifié.")

        # Exemple logique de permission ; ajustez selon votre politique
        if self.user.role == "commercial":
            if not has_permission(self.user, "update_contract"):
                raise PermissionError("Permission insuffisante pour modifier ce contrat.")
        elif self.user.role == "gestion":
            if not has_permission(self.user, "update_contract"):
                raise PermissionError("Permission insuffisante pour modifier ce contrat.")
        else:
            raise PermissionError("Permission insuffisante.")

        # Vérifier que le contrat existe
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT total_amount FROM contracts WHERE id = %s", (contract_id,))
                existing = cur.fetchone()
                if existing is None:
                    raise LookupError(f"Contrat ID {contract_id} non trouvé.")
                # On récupère total_amount existant si besoin pour validation restante
                existing_total = existing[0]

            # Valider les champs reçus

            updates = []
            params = []

            if total_amount is not None:
                if total_amount <= 0:
                    raise ValueError("Le montant total doit être positif.")
                updates.append("total_amount = %s")
                params.append(total_amount)
            else:
                total_amount = existing_total  # pour valider remaining si nécessaire

            if remaining_amount is not None:
                if remaining_amount < 0 or remaining_amount > total_amount:
                    raise ValueError("Montant restant incohérent.")
                updates.append("remaining_amount = %s")
                params.append(remaining_amount)
            
            if creation_date is not None:
                try:
                    date.fromisoformat(creation_date)
                except ValueError:
                    raise ValueError("Date de création invalide, format attendu AAAA-MM-JJ.")
                updates.append("creation_date = %s")
                params.append(creation_date)

            if is_signed is not None:
                if not isinstance(is_signed, bool):
                    raise ValueError("Le champ 'is_signed' doit être un booléen.")
                updates.append("is_signed = %s")
                params.append(is_signed)

            if client_id is not None:
                # Vérifier que le client existe
                try:
                    _ = self.get_client_by_id(client_id)
                except LookupError:
                    raise LookupError(f"Client ID {client_id} non trouvé.")
                updates.append("client_id = %s")
                params.append(client_id)

            if commercial_contact_id is not None:
                # Vérifier que le collaborateur existe
                try:
                    _ = self.get_collaborator_by_id(commercial_contact_id)
                except LookupError:
                    raise LookupError(f"Collaborator ID {commercial_contact_id} non trouvé.")
                updates.append("commercial_contact_id = %s")
                params.append(commercial_contact_id)

            if not updates:
                raise ValueError("Aucun champ à mettre à jour fourni.")

            params.append(contract_id)
            sql = f"UPDATE contracts SET {', '.join(updates)} WHERE id = %s"

            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                conn.commit()
        finally:
            conn.close()

    def create_event(self, title: str, description: str, start_date: str, end_date: str,
                    contract_id: int) -> Event:
        """
        Crée un nouvel événement lié à un contrat, après validation et contrôle des permissions.

        Args:
            title (str): Titre non vide.
            description (str): Description non vide.
            start_date (str): Date de début ISO (AAAA-MM-JJ).
            end_date (str): Date de fin ISO (AAAA-MM-JJ), >= start_date.
            contract_id (int): ID du contrat existant.

        Raises:
            PermissionError, ValueError, LookupError, pymysql.MySQLError.

        Returns:
            Event: L’instance créée.
        """

        if self.user is None or not has_permission(self.user, "create_event"):
            raise PermissionError("Permission refusée pour créer un événement.")

        # Validation simple
        if not title.strip():
            raise ValueError("Le titre ne peut pas être vide.")
        if not description.strip():
            raise ValueError("La description ne peut pas être vide.")
        try:
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)
            if end < start:
                raise ValueError("La date de fin doit être postérieure ou égale à la date de début.")
        except ValueError:
            raise ValueError("Dates invalides, format attendu AAAA-MM-JJ.")

        # Vérifier existence du contrat
        try:
            contract = self.get_contract_by_id(contract_id)  # À implémenter si ce n’est pas fait
        except LookupError:
            raise LookupError(f"Contrat ID {contract_id} non trouvé.")

        sql = """
        INSERT INTO events (title, description, start_date, end_date, contract_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute(sql, (title, description, start_date, end_date, contract_id))
                conn.commit()
                event_id = cur.lastrowid
        finally:
            conn.close()

        return Event(event_id, title, description, start_date, end_date, contract)


    def update_event(self, event_id: int,
                    title: Optional[str] = None,
                    description: Optional[str] = None,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None,
                    contract_id: Optional[int] = None) -> None:
        """
        Met à jour un événement existant.
        Valide les données et permissions.

        Args:
            event_id (int): ID de l’événement à modifier.
            title (str|None): Nouveau titre.
            description (str|None): Nouvelle description.
            start_date (str|None): Nouvelle date de début ISO.
            end_date (str|None): Nouvelle date de fin ISO.
            contract_id (int|None): Nouveau contrat lié.

        Raises:
            PermissionError, ValueError, LookupError, pymysql.MySQLError.
        """

        if self.user is None or not has_permission(self.user, "update_event"):
            raise PermissionError("Permission refusée pour modifier un événement.")

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                # Vérifier que l’événement existe
                cur.execute("SELECT start_date, end_date FROM events WHERE id = %s", (event_id,))
                existing = cur.fetchone()
                if existing is None:
                    raise LookupError(f"Événement ID {event_id} non trouvé.")
                existing_start, existing_end = existing

            updates = []
            params = []

            if title is not None:
                if not title.strip():
                    raise ValueError("Le titre ne peut pas être vide.")
                updates.append("title = %s")
                params.append(title)

            if description is not None:
                if not description.strip():
                    raise ValueError("La description ne peut pas être vide.")
                updates.append("description = %s")
                params.append(description)

            if start_date is not None:
                try:
                    start = date.fromisoformat(start_date)
                except ValueError:
                    raise ValueError("Date de début invalide, format attendu AAAA-MM-JJ.")
            else:
                start = existing_start

            if end_date is not None:
                try:
                    end = date.fromisoformat(end_date)
                except ValueError:
                    raise ValueError("Date de fin invalide, format attendu AAAA-MM-JJ.")
            else:
                end = existing_end

            if start_date is not None or end_date is not None:
                if end < start:
                    raise ValueError("La date de fin doit être postérieure ou égale à la date de début.")
                if start_date is not None:
                    updates.append("start_date = %s")
                    params.append(start_date)
                if end_date is not None:
                    updates.append("end_date = %s")
                    params.append(end_date)

            if contract_id is not None:
                # Vérifier que le contrat existe
                try:
                    _ = self.get_contract_by_id(contract_id)
                except LookupError:
                    raise LookupError(f"Contrat ID {contract_id} non trouvé.")
                updates.append("contract_id = %s")
                params.append(contract_id)

            if not updates:
                raise ValueError("Aucun champ à modifier fourni.")

            params.append(event_id)
            sql = f"UPDATE events SET {', '.join(updates)} WHERE id = %s"

            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                conn.commit()
        finally:
            conn.close()