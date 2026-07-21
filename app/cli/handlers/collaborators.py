# === Gestion des collaborateurs ===

import click
from app.controllers.write_data_to_db import DataWriter


def create_collaborator(user):
    """
    Crée un nouveau collaborateur.
    Invite à saisir nom, email, mot de passe, département, etc.
    Vérifie que `user` a la permission.
    """
    dw = DataWriter(user)

    click.echo("Création d’un nouveau collaborateur.")

    try:
        username = click.prompt("Nom d'utilisateur", type=str)
        email = click.prompt("Email", type=str)
        password = click.prompt("Mot de passe", hide_input=True, confirmation_prompt=True)
        
        # Proposer choix de département
        valid_departments = ["Gestion", "Commercial", "Support"]
        dept_str = click.prompt(
            f"Département ({', '.join(valid_departments)})",
            type=click.Choice(valid_departments, case_sensitive=False)
        )
        # Normaliser pour correspondre à Department
        department_name = dept_str.capitalize()

        collaborator = dw.create_collaborator(username, email, password, department_name)
    
    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
        return
    except ValueError as ve:
        click.echo(f"Erreur de saisie : {ve}")
        return
    except Exception as e:
        click.echo(f"Erreur lors de la création : {e}")
        return

    click.echo(f"Collaborateur créé avec succès : ID {collaborator.id}, username {collaborator.username}, département {collaborator.department.name}")

def update_collaborator(user):
    """
    Modifie un collaborateur existant.
    Propose une sélection, puis invite à modifier champs.
    Vérifie que `user` a la permission.
    """
    # On affiche la liste de tous les collaborateurs ; on l'invite à désigner un collaborateur à modifier
    # On montre chaque champ, l'un après l'autre, à l'utilisateur ; pour chaque champ, il est invité à saisir une nouvelle valeur ou à laisser le champ vide
    # On vérifie que l'utilisateur a la permission

def delete_collaborator(user):
    """
    Supprime un collaborateur.
    Propose une sélection, puis demande confirmation.
    Vérifie que `user` a la permission.
    """
    # On affiche la liste de tous les collaborateurs ; on l'invite à désigner un collaborateur à supprimer
    # On demande confirmation
    # On vérifie que l'utilisateur a la permission
