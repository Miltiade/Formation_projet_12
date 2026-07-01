from app.models.classes import Collaborator, Department
from typing import Optional


def create_user(id: int, username: str, email: str, password: str, department_name: str) -> Collaborator:
    """
    Crée un Collaborator avec mot de passe hashé et département validé.

    Args:
        id (int): Numéro d'employé unique.
        username (str): Nom d'utilisateur.
        email (str): Adresse email.
        password (str): Mot de passe en clair.
        department_name (str): Nom du département ('Gestion', 'Commercial', 'Support').

    Returns:
        Collaborator: Instance sécurisée avec hash du mot de passe.
    
    Raises:
        ValueError: Si le département est invalide.
    """
    # Validation et création de l'objet Department (lève l'erreur si invalide)
    department = Department(department_name)
    # Création du collaborateur avec hash dans __init__
    user = Collaborator(id=id, username=username, email=email, password=password, department=department)
    return user


def authenticate_user(email: str, password: str, users: list[Collaborator]) -> Optional[Collaborator]:
    """
    Authentifie un utilisateur en vérifiant email et mot de passe.

    Args:
        email (str): Email de l'utilisateur.
        password (str): Mot de passe en clair fourni.
        users (list[Collaborator]): Liste d'utilisateurs existants.

    Returns:
        Collaborator | None: L'utilisateur authentifié, ou None si échec.
    """
    # Recherche utilisateur par email (ici on suppose emails uniques)
    for user in users:
        if user.email == email:
            if user.verify_password(password):
                return user  # Authentification réussie
            else:
                return None  # Mot de passe incorrect
    return None  # Email non trouvé



# Dictionnaire des permissions par rôle
ROLE_PERMISSIONS = {
    "gestion": ["create_contract", "view_clients", "manage_events"],
    "commercial": ["view_clients", "create_client", "update_contract"],
    "support": ["view_events", "update_event_status"],
}

def get_permissions(user: Collaborator) -> list[str]:
    """
    Retourne la liste des permissions associées au rôle de l'utilisateur.

    Args:
        user (Collaborator): L'utilisateur connecté.

    Returns:
        list[str]: Permissions du rôle.
    """
    return ROLE_PERMISSIONS.get(user.role, [])
    
def has_permission(user: Collaborator, permission: str) -> bool:
    """
    Vérifie si l'utilisateur possède une permission spécifique.

    Args:
        user (Collaborator): L'utilisateur connecté.
        permission (str): Permission à tester.

    Returns:
        bool: True si permission accordée, False sinon.
    """
    return permission in get_permissions(user)