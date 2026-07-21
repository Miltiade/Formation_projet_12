import click
from app.controllers.write_data_to_db import DataWriter
from app.controllers.read_data_from_db import DataReader
from app.cli.cli_utils import select_record, optional_prompt

def create_contract(user):
    """
    Crée un nouveau contrat dans la base.
    Collecte les données nécessaires via prompts CLI.
    Vérifie que `user` a la permission.
    """
    dw = DataWriter(user)
    dr = DataReader(user)

    click.echo("Création d'un nouveau contrat.")

    try:
        total_amount = click.prompt("Montant total", type=float)
        remaining_amount = click.prompt("Reste à payer", type=float)
        creation_date = click.prompt("Date de création (AAA-MM-JJ)", type=str)
        is_signed = click.confirm("Déjà signé ?", default=False)
        
        # Select client from list
        client_id = select_record(
            "client",
            dr.get_all_clients,
            display_field="full_name"
        )
        if not client_id:
            click.echo("Annulation.")
            return
        
        # Select commercial contact from list
        commercial_id = select_record(
            "collaborateur",
            dr.get_all_collaborators,
            display_field="username"
        )
        if not commercial_id:
            click.echo("Annulation.")
            return

        contract = dw.create_contract(
            total_amount, remaining_amount, creation_date,
            is_signed, client_id, commercial_id
        )
        click.echo(f"→ Contrat créé : ID {contract.id}, montant={contract.total_amount}")

    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except ValueError as ve:
        click.echo(f"Erreur de saisie : {ve}")
    except Exception as e:
        click.echo(f"Erreur lors de la création : {e}")

def update_assigned_contract(user):
    """
    Modifie un contrat assigné à `user`.
    Charge les contrats assignés et permet modification.
    Vérifie que `user` a la permission.
    """
    dr = DataReader(user)
    dw = DataWriter(user)

    # Select contract to update
    selected_id = select_record(
        "contrat",
        dr.get_all_contracts,
        display_field="id"  # Or could show client name
    )
    if not selected_id:
        return

    try:
        # Get current data
        contract_list = dr.get_all_contracts()
        target = next((c for c in contract_list if c["id"] == selected_id), None)
        if not target:
            click.echo("Contrat introuvable.")
            return

        # Field-by-field update
        updates = {}

        updates["total_amount"] = optional_prompt(
            "Montant total", target.get("total_amount", ""), float
        )
        updates["remaining_amount"] = optional_prompt(
            "Reste à payer", target.get("remaining_amount", ""), float
        )
        updates["creation_date"] = optional_prompt(
            "Date création", target.get("creation_date", "")
        )
        
        # Boolean handling
        current_signed = target.get("is_signed", False)
        change_signed = click.confirm(
            f"Changer le statut 'signé' ? (actuel: {'Oui' if current_signed else 'Non'})",
            default=False
        )
        if change_signed:
            updates["is_signed"] = click.confirm("Est-il signé ?", default=current_signed)

        # Filter out None values
        changes = {k: v for k, v in updates.items() if v is not None}

        if not changes:
            click.echo("Aucun changement apporté.")
            return

        dw.update_contract(selected_id, **changes)
        click.echo("→ Contrat mis à jour.")

    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except ValueError as ve:
        click.echo(f"Erreur de saisie : {ve}")
    except Exception as e:
        click.echo(f"Erreur lors de la mise à jour : {e}")