from app.models.classes import Collaborator

# Permissions communes à tous

COMMON_READ_PERMISSIONS = [
    "view_all_clients",
    "view_all_contracts",
    "view_all_events",
    "view_client",
    "view_contract",
    "view_event",
]

# Permissions spécifiques à chaque rôle

ROLE_PERMISSIONS = {


    #  GESTION :
       # Créer, mettre à jour et supprimer des collaborateurs; 
       # Créer et modifier tous les contrats;
       # Filtrer l’affichage des événements, par exemple : afficher tous les événements qui n’ont pas de "support" associé
       # Modifier des événements (pour associer un collaborateur support à l’événement)
    "gestion":
        [
         "create_collaborator",
         "update_collaborator",
         "delete_collaborator",
         "create_contract",
         "update_contract",       
         "filter_unassigned_events",
         "assign_event_support"
         ],

    # COMMERCIAL :
        # Créer un client (le client leur est automatiquement associé)
        # Mettre à jour les clients dont ils sont responsables
        # Modifier/mettre à jour les contrats des clients dont ils sont responsables
        # Filtrer l’affichage des contrats, par exemple : afficher tous les contrats pas encore signés, ou pas encore entièrement payés.
        # Créer un événement pour un de leurs clients qui a signé un contrat
    "commercial":
        [
         "create_client",
         "update_assigned_client", 
         "update_assigned_contract", 
         "filter_unsigned_contracts",
         "filter_unpaid_contracts", 
         "create_event"
         ],
    
    
    # SUPPORT
        # Filtrer l’affichage des événements (e.g. afficher uniquement les événements qui leur sont attribués)
        # Mettre à jour les événements dont ils sont responsables    
    "support":
        [
         "filter_own_events",         
         "update_assigned_event"
         ],
}

def get_permissions(user: Collaborator) -> list[str]:
    """Retourne la liste des permissions du rôle utilisateur."""
    return ROLE_PERMISSIONS.get(user.role, []) + COMMON_READ_PERMISSIONS

def has_permission(user: Collaborator, permission: str) -> bool:
    """Vérifie si l'utilisateur possède une permission précise."""
    return permission in get_permissions(user)