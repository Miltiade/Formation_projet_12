# === Gestion des contrats ===

import click
from app.controllers.write_data_to_db import DataWriter


def create_contract(user):
    """
    Crée un nouveau contrat dans la base.
    Collecte les données nécessaires via prompts CLI.
    Vérifie que `user` a la permission.
    """
    dw = DataWriter(user)

    click.echo("Création d’un nouveau contrat.")

    try:
        total_amount = click.prompt("Montant total", type=float) 
        remaining_amount = click.prompt("Reste à payer", type=float)
        creation_date = click.prompt("Date de création", type=str) # ISO format, e.g. '2025-01-15'
        is_signed = click.prompt("Is contract already signed?", type=bool)
        client = click.prompt("Client", type=str) # type is client ID
        commercial_contact = click.prompt("Contact commercial chez Epic Event", type=str) # type is collaborator ID
        
        contract = dw.create_contract(total_amount, remaining_amount, creation_date, is_signed, client, commercial_contact)

    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
        return
    except ValueError as ve:
        click.echo(f"Erreur de saisie : {ve}")
        return
    except Exception as e:
        click.echo(f"Erreur lors de la création : {e}")
        return

    click.echo(f"Contrat créé avec succès : ID {contract.id}, total amount{contract.total_amount}, remaining_amount{contract.remaining_amount}, creation_date{contract.creation_date}, is_signed{contract.is_signed}, client{contract.client}, commercial_contact{contract.commercial_contact}")


def update_assigned_contract(user):
    """
    Modifie un contrat assigné à `user`.
    Charge les contrats assignés et permet modification.
    Vérifie que `user` a la permission.
    """
    # On affiche la liste de tous les contrats de l'utilisateur ; on invite à désigner un contrat à modifier  
    # On montre chaque champ, l'un après l'autre, à l'utilisateur ; pour chaque champ, il est invité à saisir une nouvelle valeur ou à laisser le champ vide
    # On vérifie que l'utilisateur a la permission
