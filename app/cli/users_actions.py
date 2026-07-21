"""
Module users_actions.py :
Contient les fonctions correspondant aux actions CLI disponibles selon les permissions.

Architecture générale :  
- Gestion des collaborateurs  
- Gestion des clients  
- Gestion des contrats  
- Gestion des événements  
- Filtres et vues spécifiques

Chaque fonction reçoit un objet `user` (utilisateur authentifié) 
et effectue une action en interaction avec la base via les contrôleurs.
Le code sera développé fonction par fonction pour limiter les risques.
"""

import click
from app.controllers.write_data_to_db import DataWriter
from app.models.classes import Department


# === Gestion des collaborateurs ===

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
    Propose une sélection, puis invites à modifier champs.
    Vérifie que `user` a la permission.
    """

def delete_collaborator(user):
    """
    Supprime un collaborateur.
    Propose une sélection, puis demande confirmation.
    Vérifie que `user` a la permission.
    """

# === Gestion des clients ===

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

# === Gestion des contrats ===

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

# === Gestion des événements ===

def create_event(user):
    """
    Crée un nouvel événement dans la base
    Invite à saisir les informations nécessaires.
    Vérifie que `user` a la permission.
    """
    dw = DataWriter(user)

    click.echo("Création d’un nouvel événement.")

    try:
        client_name = click.prompt("Nom complet du client", type=str)
        client_contact = click.prompt("Coordonnées du client (email+téléphone)", type=str) 
        date_start = click.prompt("Date de début", type=str) 
        date_end = click.prompt("Date de fin", type=str)
        location = click.prompt("Lieu", type=str) 
        attendees = click.prompt("Nombre de convives", type=int) 
        notes = click.prompt("Remarques", type=str)
        contract = click.prompt("Contrat associé à cet événement", type=str) # type is contract ID
        support_contact = click.prompt("Contact support chez Epic Event", type=str) # type is collaborator ID
        
        event = dw.create_event(id, client_name, client_contact, date_start, date_end, location, attendees, notes, contract, support_contact)
    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
        return
    except ValueError as ve:
        click.echo(f"Erreur de saisie : {ve}")
        return
    except Exception as e:
        click.echo(f"Erreur lors de la création : {e}")
        return

    click.echo(f"Evénement créé avec succès : ID {event.id}, client_name{event.client_name}, client_contact{event.client_contact}, date_start{event.date_start}, date_end{event.date_end}, location{event.location}, attendees{event.attendees}, notes{event.notes}, contract{event.contract}, support_contact{event.support_contact}")


def update_assigned_event(user):
    """
    Modifie un événement assigné à `user`.
    Charge les événements assignés et propose édition.
    Vérifie que `user` a la permission.
    """

def assign_event_support(user):
    """
    Assigne un collaborateur support à un événement spécifique.
    Vérifie que `user` a la permission.
    """

# === Filtres et vues spécifiques ===

def filter_events_view(user):
    """
    Affiche une liste filtrée d’événements selon des critères.
    Vérifie que `user` a la permission.
    """

def filter_contracts_view(user):
    """
    Affiche une liste filtrée des contrats selon des critères.
    Vérifie que `user` a la permission.
    """