from app.models.classes import Collaborator, Department
from utils.open_db_connection import get_db_connection

class UserManager:

    def create_user(self, id: int, username: str, email: str, password: str, department_name: str) -> Collaborator:
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