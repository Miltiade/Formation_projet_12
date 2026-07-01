from app.models.classes import Collaborator

ROLE_PERMISSIONS = {
    "gestion": ["create_contract", "view_clients", "manage_events"],
    "commercial": ["view_clients", "create_client", "update_contract"],
    "support": ["view_events", "update_event_status"],
}

def get_permissions(user: Collaborator) -> list[str]:
    """Retourne la liste des permissions du rôle utilisateur."""
    return ROLE_PERMISSIONS.get(user.role, [])

def has_permission(user: Collaborator, permission: str) -> bool:
    """Vérifie si l'utilisateur possède une permission précise."""
    return permission in get_permissions(user)