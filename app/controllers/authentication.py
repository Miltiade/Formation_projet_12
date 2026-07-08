from app.models.classes import Collaborator, Department
from utils.open_db_connection import get_db_connection
import os
import time
import jwt
from utils.config import SECRET_KEY

class UserManager:

    def create_user(self, id: int, username: str, email: str, password: str, department_name: str) -> Collaborator:
        department_name = department_name.capitalize()
        department = Department(department_name)
        user = Collaborator(id=id, username=username, email=email, password=password, department=department)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO collaborators (id, username, email, password_hash, department)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (user.id, user.username, user.email, user._Collaborator__password_hash, user.department.name))
        conn.commit()
        cursor.close()
        conn.close()
        return user

    def authenticate(self, email: str, password: str) -> Collaborator | None:
        """Cherche un utilisateur par email et vérifie le mot de passe."""
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "SELECT id, username, email, password_hash, department FROM collaborators WHERE email = %s"
        cursor.execute(sql, (email,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row is None:
            return None  # email non trouvé
        
        id, username, email, password_hash, department_name = row
        department = Department(department_name)

        # Créez l'utilisateur sans recalculer le hash dans __init__
        user = Collaborator(id=id, username=username, email=email, password=password_hash, department=department)
        # Remplacez le hash généré par le hash en base
        user._Collaborator__password_hash = password_hash

        if user.verify_password(password):
            return user
        else:
            return None

    def get_all_users(self) -> list[Collaborator]:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "SELECT id, username, email, password_hash, department FROM collaborators"
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        users = []
        for row in rows:
            id, username, email, password_hash, department_name = row
            department = Department(department_name)
            user = Collaborator(id=id, username=username, email=email, password=password_hash, department=department)
            user._Collaborator__password_hash = password_hash
            users.append(user)
        return users

TOKEN_FILE = os.path.expanduser("~/.epicevents_token")
ALGORITHM = "HS256"
TOKEN_EXPIRATION_SECONDS = 3600  # 1 heure

class AuthService:
    """Service minimal pour auth avec JWT."""

    @staticmethod
    def create_token(user: Collaborator) -> str:
        """Crée un JWT avec id, role et expiration."""
        payload = {
            "user_id": user.id,
            "role": user.role,
            "exp": time.time() + TOKEN_EXPIRATION_SECONDS,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token

    @staticmethod
    def save_token(token: str):
        """Sauvegarde le token dans un fichier local sécurisé."""
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
        os.chmod(TOKEN_FILE, 0o600)  # Lire/écrire seul user

    @staticmethod
    def load_token() -> str | None:
        """Charge le token depuis le fichier."""
        if not os.path.exists(TOKEN_FILE):
            return None
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()

    @staticmethod
    def decode_token(token: str) -> dict | None:
        """Décode et valide un token. Renvoie payload ou None si erreur."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            print("Votre session a expiré, veuillez vous reconnecter.")
            return None
        except jwt.InvalidTokenError:
            print("Token invalide, veuillez vous reconnecter.")
            return None

    @staticmethod
    def get_current_user_info() -> dict | None:
        """Récupère les infos user depuis token, None si erreur."""
        token = AuthService.load_token()
        if not token:
            print("Aucun token trouvé, veuillez vous connecter.")
            return None
        return AuthService.decode_token(token)

    @staticmethod
    def logout():
        """Supprime le token localement."""
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
            print("Déconnexion réussie.")