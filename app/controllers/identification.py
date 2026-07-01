from app.models.classes import Collaborator, Department

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