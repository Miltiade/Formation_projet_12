from app.models.classes import Collaborator, Department
from app.open_db_connection import get_db_connection

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

    def authenticate(self, email: str, password: str):
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

    def get_all_users(self) -> list[Collaborator]:
        """Retourne la liste des utilisateurs."""
        return self._users