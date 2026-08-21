# === Gestion des événements ===

import click
import sentry_sdk
from app.controllers.write_data_to_db import DataWriter
from app.controllers.read_data_from_db import DataReader
from app.cli.cli_utils import select_record, optional_prompt


def create_event(user):
    """
    Crée un nouvel événement dans la base
    Invite à saisir les informations nécessaires.
    Vérifie que `user` a la permission.
    """
    dw = DataWriter(user)

    click.echo("Création d’un nouvel événement.")

    try:
        name = click.prompt("Nom de l'événement", type=str)
        client_name = click.prompt("Nom complet du client", type=str)
        client_contact = click.prompt("Coordonnées du client (email+téléphone)", type=str) 
        date_start = click.prompt("Date de début", type=str) 
        date_end = click.prompt("Date de fin", type=str)
        location = click.prompt("Lieu", type=str) 
        attendees = click.prompt("Nombre de convives", type=int) 
        notes = click.prompt("Remarques", type=str)

        # Utilisation de select_record pour contract_id (évite erreurs de saisie manuelle)
        contract_id = select_record(
            "contrat",
            lambda: DataReader(user).get_all_contracts(),
            display_field="id"
        )
        if not contract_id:
            click.echo("Annulation.")
            return

        # support_contact_id est optionnel (None autorisé)
        if click.confirm("Assigner un support ?", default=False):
            support_id = select_record(
                "collaborateur",
                lambda: DataReader(user).get_all_collaborators(),
                display_field="username"
            )
            support_contact_id = support_id if support_id else None
        else:
            support_contact_id = None
        
        event = dw.create_event(
            name=name,
            client_name=client_name,
            client_contact=client_contact,
            date_start=date_start,
            date_end=date_end,
            location=location,
            attendees=attendees,
            notes=notes,
            contract_id=contract_id,
            support_contact_id=support_contact_id
        )

    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
        return
    except ValueError as ve:
        click.echo(f"Erreur de saisie : {ve}")
        return
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur lors de la création : {e}")
        return

    # Affichage des données
    support_display = event.support_contact_id or "Non assigné"
    click.echo(
        f"Événement créé avec succès : ID {event.id}, "
        f"nom='{event.name}', client='{event.client_name}', "
        f"début={event.date_start}, fin={event.date_end}, "
        f"lieu={event.location}, convives={event.attendees}, "
        f"contrat_id={event.contract_id}, support_id={support_display}"
    )

def update_assigned_event(user):
    """
    Modifie un événement assigné à `user`.
    Charge les événements assignés et propose édition.
    Vérifie que `user` a la permission.
    """
    dr = DataReader(user)
    dw = DataWriter(user)

    # Select event
    selected_id = select_record(
        "événement",
        dr.get_all_events,
        display_field="name"
    )
    if not selected_id:
        return

    try:
        # Get current data
        event_list = dr.get_all_events()
        target = next((e for e in event_list if e["id"] == selected_id), None)
        if not target:
            click.echo("Événement introuvable.")
            return

        # Field-by-field update matching Event model
        updates = {}

        updates["name"] = optional_prompt("Nom", target.get("name", ""))
        updates["client_name"] = optional_prompt("Nom client", target.get("client_name", ""))
        updates["client_contact"] = optional_prompt("Coordonnées client", target.get("client_contact", ""))
        updates["date_start"] = optional_prompt("Date début", target.get("date_start", ""))
        updates["date_end"] = optional_prompt("Date fin", target.get("date_end", ""))
        updates["location"] = optional_prompt("Lieu", target.get("location", ""))
        updates["attendees"] = optional_prompt("Convives", target.get("attendees"), int)
        updates["notes"] = optional_prompt("Remarques", target.get("notes", ""))

        # Contract and support are special cases - use select_record if changing
        change_contract = click.confirm("Changer le contrat associé ?", default=False)
        if change_contract:
            updates["contract_id"] = select_record("contrat", dr.get_all_contracts, display_field="id")

        change_support = click.confirm("Changer le support assigné ?", default=False)
        if change_support:
            updates["support_contact_id"] = select_record("collaborateur", dr.get_all_collaborators, display_field="username")

        # Filter out None values
        changes = {k: v for k, v in updates.items() if v is not None}

        if not changes:
            click.echo("Aucun changement apporté.")
            return

        dw.update_event(selected_id, **changes)
        click.echo("→ Événement mis à jour.")

    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except ValueError as ve:
        click.echo(f"Erreur de saisie : {ve}")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur lors de la mise à jour : {e}")

def assign_event_support(user):
    """
    Assigne un collaborateur support à un événement spécifique.
    Vérifie que `user` a la permission.
    """
    dr = DataReader(user)
    dw = DataWriter(user)

    # Select event
    selected_id = select_record(
        "événement",
        dr.get_all_events,
        display_field="name"
    )
    if not selected_id:
        return

    # Select support collaborator
    support_id = select_record(
        "collaborateur",
        dr.get_all_collaborators,
        display_field="username"
    )
    if not support_id:
        click.echo("Annulation.")
        return

    try:        
        dw.update_event(selected_id, support_contact_id=support_id)
        click.echo("→ Support assigné avec succès.")
    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except Exception as e:
        sentry_sdk.capture_exception(e)
        click.echo(f"Erreur lors de l'assignment : {e}")