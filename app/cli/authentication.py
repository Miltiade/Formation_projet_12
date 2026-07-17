"""
Module authentication.py :
Fournit des fonctions pour gérer l'authentification CLI,
interopérant avec UserManager et AuthService.
"""

from app.controllers.authentication import UserManager, AuthService
import click

user_manager = UserManager()

def login() -> object | None:
    """
    Invite l'utilisateur à saisir email et mot de passe,
    tente l'authentification et enregistre le token JWT si succès.

    Returns:
        user authentifié (Collaborator) ou None si échec
    """
    email = click.prompt("Email")
    password = click.prompt("Mot de passe", hide_input=True)

    user = user_manager.authenticate(email, password)
    if user is None:
        click.echo("Échec d'authentification.")
        return None

    token = AuthService.create_token(user)
    AuthService.save_token(token)
    click.echo(f"Connexion réussie. Bienvenue, {user.username} (rôle : {user.role}) !")

    return user

def logout():
    """Déconnecte l'utilisateur en supprimant le token local."""
    AuthService.logout()
    click.echo("Déconnexion réussie.")

def get_current_user() -> object | None:
    """
    Récupère l'utilisateur courant à partir du token JWT sauvegardé.
    Affiche un message si aucun token ou token invalide.
    """
    payload = AuthService.get_current_user_info()
    if payload is None:
        click.echo("Aucun utilisateur connecté. Veuillez vous connecter.")
        return None

    user_id = payload.get("user_id")
    if user_id is None:
        click.echo("Données du token incomplètes.")
        return None

    # Chargement du collaborateur depuis l'ID (via UserManager ou DataWriter)
    user = user_manager.get_all_users()
    for u in user:
        if u.id == user_id:
            return u

    click.echo("Utilisateur introuvable en base de données.")
    return None
