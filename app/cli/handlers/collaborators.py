import click
from app.controllers.write_data_to_db import DataWriter
from app.controllers.read_data_from_db import DataReader
from app.cli.cli_utils import select_record, optional_prompt

def create_collaborator(user):
    """
    Crée un nouveau collaborateur.
    Invite à saisir nom, email, mot de passe, département, etc.
    Vérifie que `user` a la permission.
    """
    dw = DataWriter(user)

    click.echo("Création d'un nouveau collaborateur.")

    try:
        username = click.prompt("Nom d'utilisateur", type=str)
        email = click.prompt("Email", type=str)
        password = click.prompt("Mot de passe", hide_input=True, confirmation_prompt=True)
        
        valid_departments = ["Gestion", "Commercial", "Support"]
        dept_str = click.prompt(
            f"Département ({', '.join(valid_departments)})",
            type=click.Choice(valid_departments, case_sensitive=False)
        )
        department_name = dept_str.capitalize()

        collaborator = dw.create_collaborator(username, email, password, department_name)
        click.echo(f"→ Collaborateur créé : ID {collaborator.id}, {collaborator.username}")

    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except ValueError as ve:
        click.echo(f"Erreur de saisie : {ve}")
    except Exception as e:
        click.echo(f"Erreur lors de la création : {e}")

def update_collaborator(user):
    """
    Modifie un collaborateur existant.
    Propose une sélection, puis invite à modifier champs.
    Vérifie que `user` a la permission.
    """
    dr = DataReader(user)
    dw = DataWriter(user)

    # Select collaborator
    selected_id = select_record(
        "collaborateur",
        dr.get_all_collaborators,
        display_field="username"
    )
    if not selected_id:
        return

    try:
        # Get current data
        collab_list = dr.get_all_collaborators()
        target = next((c for c in collab_list if c["id"] == selected_id), None)
        if not target:
            click.echo("Collaborateur introuvable.")
            return

        # Field-by-field update
        updates = {}

        updates["username"] = optional_prompt(
            "Username", target.get("username", "")
        )
        updates["email"] = optional_prompt(
            "Email", target.get("email", "")
        )
        updates["department_name"] = optional_prompt(
            "Département", target.get("department", ""),
            lambda x: x.capitalize()
        )

        # Password is special - separate prompt
        change_pwd = click.confirm("Modifier le mot de passe ?", default=False)
        if change_pwd:
            updates["password"] = click.prompt(
                "Nouveau mot de passe", hide_input=True, confirmation_prompt=True
            )

        # Filter out None values
        changes = {k: v for k, v in updates.items() if v is not None}

        if not changes:
            click.echo("Aucun changement apporté.")
            return

        dw.update_collaborator(selected_id, **changes)
        click.echo("→ Collaborateur mis à jour.")

    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except ValueError as ve:
        click.echo(f"Erreur de saisie : {ve}")
    except Exception as e:
        click.echo(f"Erreur lors de la mise à jour : {e}")

def delete_collaborator(user):
    """
    Supprime un collaborateur.
    Propose une sélection, puis demande confirmation.
    Vérifie que `user` a la permission.
    """
    # NOTE: Needs delete_collaborator() method in DataWriter first
    dr = DataReader(user)

    selected_id = select_record(
        "collaborateur",
        dr.get_all_collaborators,
        display_field="username"
    )
    if not selected_id:
        return

    if not click.confirm(f"Êtes-vous sûr de vouloir supprimer ce collaborateur (ID {selected_id}) ?"):
        click.echo("Annulé.")
        return

    try:
        # TODO: Implement delete_collaborator() in DataWriter
        dw = DataWriter(user)
        # dw.delete_collaborator(selected_id)
        click.echo("Fonctionnalité 'delete_collaborator' manquante dans DataWriter - à implémenter.")
    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except Exception as e:
        click.echo(f"Erreur lors de la suppression : {e}")