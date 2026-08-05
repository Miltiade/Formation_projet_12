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
    dr = DataReader(user)

    click.echo("Création d’un nouveau client.")

    try:
        full_name = click.prompt("Nom complet", type=str)
        email = click.prompt("Email", type=str)
        phone = click.prompt("Telephone", type=str)
        company_name = click.prompt("Nom de l'entreprise", type=str)
        creation_date = click.prompt("Date de création", type=str)        # ISO format, e.g. '2025-01-15'
        commercial_contact_id = select_record(
            "collaborateur",
            lambda: dr.get_all_collaborators(),
            display_field="username"
        )
        if not commercial_contact_id:
            click.echo("Annulation.")
            return

        client = dw.create_client(
            full_name=full_name,
            email=email,
            phone=phone,
            company_name=company_name,
            creation_date=creation_date,
            commercial_contact_id=commercial_contact_id
        )


    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
        return
    except ValueError as ve:
        click.echo(f"Erreur de saisie : {ve}")
        return
    except Exception as e:
        click.echo(f"Erreur lors de la création : {e}")
        return

    click.echo(
        f"Client créé avec succès : ID {client.id}, "
        f"nom='{client.full_name}', email={client.email}, "
        f"tel={client.phone}, entreprise={client.company_name}, "
        f"créé_le={client.creation_date}, commercial_id={client.commercial_contact_id}"
    )

def update_assigned_client(user):
    """
    Modifie un client assigné à `user`.
    Charge les clients assignés et permet modification.
    Vérifie que `user` a la permission.
    """

    dr = DataReader(user)
    dw = DataWriter(user)

    # Select client
    selected_id = select_record(
    "client",
    dr.get_all_clients,
    display_field="full_name"
)
    if selected_id is None:
        return

    try:
        # Get client data
        client_list = dr.get_all_clients()
        target = next((c for c in client_list if c["id"] == selected_id), None)
        if not target:
            click.echo("Client introuvable.")
            return

        # Update client data
        updates = {}

        updates["full_name"] = optional_prompt("Nom complet", target.get("full_name", ""))
        updates["email"] = optional_prompt("Email", target.get("email", ""))
        updates["phone"] = optional_prompt("Téléphone", target.get("phone", ""))
        updates["company_name"] = optional_prompt("Nom entreprise", target.get("company_name", ""))

        # Filter out None values
        changes = {k: v for k, v in updates.items() if v is not None}

        if not changes:
            click.echo("Aucun changement apporté.")
            return

        # Apply updates to client data
        dw.update_client(selected_id, **changes)
        click.echo("→ Client mis à jour.")
        
    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except ValueError as ve:
        click.echo(f"Erreur de saisie : {ve}")
    except Exception as e:
        click.echo(f"Erreur lors de la mise à jour : {e}")