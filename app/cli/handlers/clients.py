# === Gestion des clients ===

import click
from app.controllers.write_data_to_db import DataWriter


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
    # On affiche la liste de tous les clients de l'utilisateur ; on invite à désigner un client à modifier  
    # On montre chaque champ, l'un après l'autre, à l'utilisateur ; pour chaque champ, il est invité à saisir une nouvelle valeur ou à laisser le champ vide
    # On vérifie que l'utilisateur a la permission

