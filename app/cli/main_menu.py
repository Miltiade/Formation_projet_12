"""
Module main_menu.py :
Affiche le menu principal selon le rôle utilisateur,
gère la navigation et autorisations (actions communes + actions possibles au rôle uniquement),
dispatche les actions associées
propose logout.
"""

import click
from app.controllers.authorizations import get_permissions
from app.cli.handlers import (
    create_collaborator, update_collaborator, delete_collaborator,
    create_client, update_assigned_client,
    create_contract, update_assigned_contract,
    create_event, update_assigned_event, assign_event_support,
    filter_events_view, filter_contracts_view,
)
from app.cli.handlers.views import (
    view_all_clients, view_all_contracts, view_all_events,
    view_client, view_contract, view_event,
)

def show_main_menu(user):
    """
    Displays main menu, adapted to authenticated user's role and permissions.

    Args:
        user: An authenticated user object with at least a `role` attribute.

    Behavior:
        - Computes the user's permissions.
        - Builds a filtered list of menu options from common and role-specific actions.
        - Loops until the user chooses logout or aborts the prompt.
        - Dispatches the selected action to the matching handler.
    """

    permissions = get_permissions(user)


    # Actions available to all authenticated users, regardless of role.
    common_actions = {
        "view_all_clients": "Consulter tous les clients",
        "view_all_contracts": "Consulter tous les contrats",
        "view_all_events": "Consulter tous les événements",
        "view_client": "Consulter un client particulier",
        "view_contract": "Consulter un contrat particulier",
        "view_event": "Consulter un événement particulier",
    }

    # Mapping of role names to the actions they may offer.
    # Each action is still filtered by the user's actual permissions.
    role_actions_map = {
        "gestion": {
            "create_collaborator": "Créer un collaborateur",
            "update_collaborator": "Modifier un collaborateur",
            "delete_collaborator": "Supprimer un collaborateur",
            "create_contract": "Créer un contrat",
            "update_assigned_contract": "Modifier un contrat",
            "filter_events_view": "Filtrer les événements",
            "assign_event_support": "Assigner support à un événement",
        },
        "commercial": {
            "create_client": "Créer un client",
            "create_contract": "Créer un contrat",
            "update_assigned_client": "Modifier client associé",
            "update_assigned_contract": "Modifier contrat associé",
            "filter_contracts_view": "Filtrer les contrats",
            "create_event": "Créer un événement",
        },
        "support": {
            "filter_events_view": "Filtrer les événements assignés",
            "update_assigned_event": "Modifier événement assigné",
        },
    }

    # Build the final ordered list of menu options.
    
    ## First, add common actions the user is allowed to perform,
    menu_options = []
    for perm, label in common_actions.items():
        if perm in permissions:
            menu_options.append((perm, label))

    ## then, add role-specific actions the user is allowed to perform.
    role_perms = role_actions_map.get(user.role, {})
    for perm, label in role_perms.items():
        if perm in permissions:
            menu_options.append((perm, label))

    menu_options.append(("logout", "Déconnexion"))


    # Map each permission string to the handler that implements it.
    # View handlers take no arguments; action handlers take the current user.
    action_dispatch = {
        "view_all_clients": view_all_clients,
        "view_all_contracts": view_all_contracts,
        "view_all_events": view_all_events,
        "view_client": view_client,
        "view_contract": view_contract,
        "view_event": view_event,
        "create_collaborator": create_collaborator,
        "update_collaborator": update_collaborator,
        "delete_collaborator": delete_collaborator,
        "filter_events_view": filter_events_view,
        "assign_event_support": assign_event_support,
        "create_client": create_client,
        "update_assigned_client": update_assigned_client,
        "create_contract": create_contract,
        "update_assigned_contract": update_assigned_contract,
        "filter_contracts_view": filter_contracts_view,
        "create_event": create_event,
        "update_assigned_event": update_assigned_event,
    }


    # Main interactive loop: display the menu, read the user's choice,
    # validate it, and dispatch to the appropriate handler.
    # The loop exits only when the user selects logout or aborts the prompt.
    while True:
        # Display the numbered menu built from allowed actions.
        click.echo("\nMenu principal :")
        for i, (_, label) in enumerate(menu_options, 1):
            click.echo(f"{i}. {label}")

        # Read the user's numeric choice.
        # click.exceptions.Abort is raised on Ctrl+C or EOF; it is treated as logout.
        try:
            choice = click.prompt("Choisissez une option", type=int)
        except click.exceptions.Abort:
            click.echo("\nQuitte le menu.")
            break

        # Reject choices outside the valid range and re-display the menu.
        if choice < 1 or choice > len(menu_options):
            click.echo("Choix invalide.")
            continue

        # Retrieve the permission key and label for the selected option.
        perm_chosen, label_chosen = menu_options[choice - 1]

        # Logout ends the session and exits the loop.
        if perm_chosen == "logout":
            click.echo("Déconnecté.")
            break
        
        # Find the handler associated with the chosen permission.
        # If none exists, the action is not yet implemented.
        handler = action_dispatch.get(perm_chosen)
        if handler is None:
            click.echo(f"Action '{label_chosen}' non implémentée.")
            continue

        # Execute the handler — all handlers take the current user as argument.
        try:
            handler(user)
        except Exception as e:
            click.echo(f"Erreur lors de l'exécution de '{label_chosen}': {e}")