"""
Module welcome.py :
Affiche le message d'accueil, gère la boucle d'authentification,
puis redirige vers le menu principal après connexion.
"""

import click
from app.controllers.authentication import UserManager, AuthService
from app.cli.main_menu import show_main_menu

user_manager = UserManager()

def run_welcome_loop():
    """Boucle d'accueil + authentification ou sortie."""

    click.echo("Bienvenue sur Epic Events CRM CLI !")

    while True:
        click.echo("\nOptions :")
        click.echo("  1 - Connexion")
        click.echo("  2 - Quitter")

        choice = click.prompt("Choisissez une option", type=int)

        if choice == 1:
            email = click.prompt("Email")
            password = click.prompt("Mot de passe", hide_input=True)

            user = user_manager.authenticate(email, password)
            if user is None:
                click.echo("Échec d'authentification. Veuillez réessayer.")
                continue

            # Sauvegarde du token JWT (optionnel)
            token = AuthService.create_token(user)
            AuthService.save_token(token)

            click.echo(f"Connexion réussie. Bienvenue, {user.username} (rôle : {user.role}) !\n")

            # Appel du menu principal avec l'utilisateur authentifié
            show_main_menu(user)

            # À la sortie du menu, on termine la CLI
            break

        elif choice == 2:
            click.echo("Au revoir !")
            break

        else:
            click.echo("Option invalide, merci de choisir 1 ou 2.")