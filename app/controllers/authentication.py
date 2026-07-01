from typing import Optional
from app.models.classes import Collaborator, Department

class UserManager:
    """Gestionnaire simple d'utilisateurs en mémoire."""

    def __init__(self):
        self._users = []  # Liste interne d'objets Collaborator

    def create_user(self, id: int, username: str, email: str, password: str, department_name: str) -> Collaborator:
        """Crée un collaborateur sécurisé et l'ajoute à la liste."""
        department = Department(department_name)
        user = Collaborator(id=id, username=username, email=email, password=password, department=department)
        self._users.append(user)
        return user

    def authenticate(self, email: str, password: str) -> Optional[Collaborator]:
        """Cherche un utilisateur par email et vérifie le mot de passe."""
        for user in self._users:
            if user.email == email and user.verify_password(password):
                return user
        return None

    def get_all_users(self) -> list[Collaborator]:
        """Retourne la liste des utilisateurs."""
        return self._users