import click
from app.controllers.authentication import UserManager, AuthService
from app.controllers.authorizations import get_permissions
from app.controllers.write_data_to_db import DataWriter

user_manager = UserManager()

@click.group()
@click.pass_context
def cli(ctx):
    """Epic Events CRM CLI."""
    ctx.ensure_object(dict)
    ctx.obj["user"] = None

@cli.command()
@click.pass_context
def login(ctx):
    """Connexion via email et mot de passe."""
    email = click.prompt("Email")
    password = click.prompt("Mot de passe", hide_input=True)
    user = user_manager.authenticate(email, password)
    if user is None:
        click.echo("Échec d'authentification.")
        return

    # Sauvegarder token JWT localement (optionnel)
    token = AuthService.create_token(user)
    AuthService.save_token(token)

    ctx.obj["user"] = user
    click.echo(f"Connecté : {user.username} (rôle : {user.role})")
    show_main_menu(ctx)

@cli.command()
def logout():
    """Déconnexion - supprime token local."""
    AuthService.logout()
    click.echo("Vous êtes déconnecté.")

def cli_create_collaborator(writer: DataWriter):
    try:
        username = click.prompt("Nom d'utilisateur")
        email = click.prompt("Email")
        password = click.prompt("Mot de passe", hide_input=True, confirmation_prompt=True)
        department = click.prompt("Département (Gestion, Commercial, Support)")
        collaborator = writer.create_collaborator(username, email, password, department)
        click.echo(f"Collaborateur créé avec ID : {collaborator.id}")
    except Exception as e:
        click.echo(f"Erreur : {e}")

def show_main_menu(ctx):
    user = ctx.obj.get("user")
    if user is None:
        payload = AuthService.get_current_user_info()
        if payload is None:
            click.echo("Veuillez vous connecter d'abord.")
            return
        user = DataWriter(user=None).get_collaborator_by_id(payload["user_id"])
        ctx.obj["user"] = user

    writer = DataWriter(user)
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

        choice = click.prompt("Choisissez une option", type=int)

        if choice < 1 or choice > len(menu_options):
            click.echo("Choix invalide.")
            continue

        perm_chosen, label_chosen = menu_options[choice - 1]

        if perm_chosen == "logout":
            AuthService.logout()
            click.echo("Déconnecté.")
            break

        # Exemple de dispatch simple :
        if perm_chosen == "create_collaborator":
            cli_create_collaborator(writer)
        else:
            click.echo(f"L'option '{label_chosen}' n'est pas encore implémentée.")

if __name__ == "__main__":
    cli()