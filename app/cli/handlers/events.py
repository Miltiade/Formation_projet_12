# === Gestion des événements ===

import click
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
        client_name = click.prompt("Nom complet du client", type=str)
        client_contact = click.prompt("Coordonnées du client (email+téléphone)", type=str) 
        date_start = click.prompt("Date de début", type=str) 
        date_end = click.prompt("Date de fin", type=str)
        location = click.prompt("Lieu", type=str) 
        attendees = click.prompt("Nombre de convives", type=int) 
        notes = click.prompt("Remarques", type=str)
        contract = click.prompt("Contrat associé à cet événement", type=str) # type is contract ID
        support_contact = click.prompt("Contact support chez Epic Event", type=str) # type is collaborator ID
        
        event = dw.create_event(id, client_name, client_contact, date_start, date_end, location, attendees, notes, contract, support_contact)

    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
        return
    except ValueError as ve:
        click.echo(f"Erreur de saisie : {ve}")
        return
    except Exception as e:
        click.echo(f"Erreur lors de la création : {e}")
        return

    click.echo(f"Evénement créé avec succès : ID {event.id}, client_name{event.client_name}, client_contact{event.client_contact}, date_start{event.date_start}, date_end{event.date_end}, location{event.location}, attendees{event.attendees}, notes{event.notes}, contract{event.contract}, support_contact{event.support_contact}")


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
        # This requires update_event() with support_contact_id parameter OR dedicated method
        dw.update_event(selected_id, support_contact_id=support_id)
        click.echo("→ Support assigné avec succès.")
    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except Exception as e:
        click.echo(f"Erreur lors de l'assignment : {e}")