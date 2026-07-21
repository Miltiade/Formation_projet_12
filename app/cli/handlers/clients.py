# === Gestion des clients ===

import click
from app.controllers.write_data_to_db import DataWriter
from app.controllers.read_data_from_db import DataReader
from app.cli.cli_utils import select_record, optional_prompt


def create_client(user):
    """
    Crée un nouveau client dans la base.
    Collecte les données nécessaires via prompts CLI.
    Vérifie que `user` a la permission.
    """
    dw = DataWriter(user)

    click.echo("Création d’un nouveau client.")

    try:
        full_name = click.prompt("Nom complet", type=str)
        email = click.prompt("Email", type=str)
        phone = click.prompt("Telephone", type=str)
        company_name = click.prompt("Nom de l'entreprise", type=str)
        creation_date = click.prompt("Date de création", type=str)        # ISO format, e.g. '2025-01-15'
        # last_update_date = click.prompt
        commercial_contact = click.prompt("Contact commercial chez Epic Event", type=str) # type is collaborator ID

        client = dw.create_client(full_name, email, phone, company_name, creation_date, commercial_contact)

    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
        return
    except ValueError as ve:
        click.echo(f"Erreur de saisie : {ve}")
        return
    except Exception as e:
        click.echo(f"Erreur lors de la création : {e}")
        return

    click.echo(f"Client créé avec succès : full_name {client.full_name}, email {client.email}, phone{client.phone}, company_name{client.company_name}, creation_date{client.creation_date}, commercial_contact{client.commercial_contact}")

def update_assigned_client(user):
    """
    Modifie un client assigné à `user`.
    Charge les clients assignés et permet modification.
    Vérifie que `user` a la permission.
    """
    selected_id = select_record(user, "client", DataReader(user).get_all_clients)
    if selected_id is None:
        return

    try:
        reader = DataReader(user)
        client_list = reader.get_all_clients()
        client_dict = next((c for c in client_list if c["id"] == selected_id), None)
        if not client_dict:
            click.echo("Client introuvable.")
            return
        
        updates = optional_prompt(client_dict, {
            "full_name": ("Nom complet", str),
            "email": ("Email", str),
            "phone": ("Téléphone", str),
            "company_name": ("Nom entreprise", str),
        })

        if not updates:
            click.echo("Aucun changement apporté.")
            return

        click.echo(f"Mise à jour prête : {updates}")
        
    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except Exception as e:
        click.echo(f"Erreur lors de la mise à jour : {e}")
