# === Gestion des événements ===

import click
from app.controllers.write_data_to_db import DataWriter

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
    # On affiche la liste de tous les événements de l'utilisateur ; on invite à désigner un événement à modifier  
    # On montre chaque champ, l'un après l'autre, à l'utilisateur ; pour chaque champ, il est invité à saisir une nouvelle valeur ou à laisser le champ vide
    # On vérifie que l'utilisateur a la permission


def assign_event_support(user):
    """
    Assigne un collaborateur support à un événement spécifique.
    Vérifie que `user` a la permission.
    """
    # On affiche la liste de tous les événements ; on invite à désigner un événement à modifier  
    # On montre le champ support_contact à l'utilisateur ; il est invité à saisir une nouvelle valeur ou à laisser le champ vide
    # On vérifie que l'utilisateur a la permission