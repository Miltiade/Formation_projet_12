"""
Module main_menu.py :
Affiche le menu principal selon le rôle utilisateur,
gère la navigation et autorisations,
et dispatche les actions associées.
"""

import click
from app.controllers.authorizations import get_permissions
from app.cli.handlers import (
    create_collaborator, create_client, create_contract, create_event,
    update_collaborator, update_assigned_client, update_assigned_contract,
    delete_collaborator, update_assigned_event, assign_event_support,
    filter_events_view, filter_contracts_view,
)

def show_main_menu(user):
    """Affiche le menu principal adapté, puis gère choix-actions jusqu'à déconnexion."""

    permissions = get_permissions(user)

    common_actions = {
        "view_all_clients": "Consulter tous les clients",
        "view_all_contracts": "Consulter tous les contrats",
        "view_all_events": "Consulter tous les événements",
        "view_client": "Consulter un client particulier",
        "view_contract": "Consulter un contrat particulier",
        "view_event": "Consulter un événement particulier",
    }

    role_actions_map = {
        "gestion": {
            "create_collaborator": "Créer un collaborateur",
            "update_collaborator": "Modifier un collaborateur",
            "delete_collaborator": "Supprimer un collaborateur",
            "filter_events_view": "Filtrer les événements",
            "assign_event_support": "Assigner support à un événement",
        },
        "commercial": {
            "create_client": "Créer un client",
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

    # Construire la liste des options affichées à l'utilisateur
    menu_options = []
    for perm, label in common_actions.items():
        if perm in permissions:
            menu_options.append((perm, label))

    role_perms = role_actions_map.get(user.role, {})
    for perm, label in role_perms.items():
        if perm in permissions:
            menu_options.append((perm, label))

    menu_options.append(("logout", "Déconnexion"))

    while True:
        click.echo("\nMenu principal :")
        for i, (_, label) in enumerate(menu_options, 1):
            click.echo(f"{i}. {label}")

        try:
            choice = click.prompt("Choisissez une option", type=int)
        except click.exceptions.Abort:
            click.echo("\nQuitte le menu.")
            break

        if choice < 1 or choice > len(menu_options):
            click.echo("Choix invalide.")
            continue

        perm_chosen, label_chosen = menu_options[choice - 1]

        if perm_chosen == "logout":
            click.echo("Déconnecté.")
            break

        # Actions à choisir par l'utilisateur (en respectant ses permissions!)
        