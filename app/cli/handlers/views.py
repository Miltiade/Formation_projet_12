"""Handler for read-only views and filtered listings."""

import click
from app.controllers.read_data_from_db import DataReader
from app.cli.cli_utils import select_record

# ==================== COMMON VIEWS ====================

def view_all_clients(user):
    """Affiche la liste de tous les clients."""
    dr = DataReader(user)
    
    try:
        clients = dr.get_all_clients()
        if not clients:
            click.echo("Aucun client trouvé.")
            return
        
        click.echo(f"\n{'='*60}")
        click.echo(f"Tous les clients ({len(clients)})")
        click.echo(f"{'='*60}")
        
        for client in clients:
            click.echo(f"ID {client['id']}: {client.get('full_name', '')} | {client.get('email', '')} | {client.get('company_name', '')}")
            
    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except Exception as e:
        click.echo(f"Erreur : {e}")

def view_all_contracts(user):
    """Affiche la liste de tous les contrats."""
    dr = DataReader(user)
    
    try:
        contracts = dr.get_all_contracts()
        if not contracts:
            click.echo("Aucun contrat trouvé.")
            return
        
        click.echo(f"\n{'='*60}")
        click.echo(f"Tous les contrats ({len(contracts)})")
        click.echo(f"{'='*60}")
        
        for contract in contracts:
            status = "✓ Signé" if contract.get('is_signed', False) else "✗ Non signé"
            click.echo(f"ID {contract['id']}: {contract.get('total_amount', 0)}€ | {status} | Reste: {contract.get('remaining_amount', 0)}€")
            
    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except Exception as e:
        click.echo(f"Erreur : {e}")

def view_all_events(user):
    """Affiche la liste de tous les événements."""
    dr = DataReader(user)
    
    try:
        events = dr.get_all_events()
        if not events:
            click.echo("Aucun événement trouvé.")
            return
        
        click.echo(f"\n{'='*60}")
        click.echo(f"Tous les événements ({len(events)})")
        click.echo(f"{'='*60}")

        for event in events:
            name = event.get('name', '')
            click.echo(f"ID {event['id']}: '{name}' | {event.get('date_start', '')} au {event.get('date_end', '')}")
            
    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except Exception as e:
        click.echo(f"Erreur : {e}")

def view_client(user):
    """Affiche un client spécifique."""
    dr = DataReader(user)
    
    selected_id = select_record("client", dr.get_all_clients, display_field="full_name")
    if not selected_id:
        return
    
    try:
        client = dr.get_client_by_id(selected_id)
        click.echo(f"\n{'='*60}")
        click.echo(f"Détails du client ID {client['id']}")
        click.echo(f"{'='*60}")
        click.echo(f"Nom complet : {client.get('full_name', '')}")
        click.echo(f"Email : {client.get('email', '')}")
        click.echo(f"Téléphone : {client.get('phone', '')}")
        click.echo(f"Entreprise : {client.get('company_name', '')}")
        click.echo(f"Créé le : {client.get('creation_date', '')}")
        click.echo(f"Contact commercial ID : {client.get('commercial_contact_id', 'N/A')}")
            
    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except LookupError as le:
        click.echo(f"Client introuvable : {le}")
    except Exception as e:
        click.echo(f"Erreur : {e}")

def view_contract(user):
    """Affiche un contrat spécifique."""
    dr = DataReader(user)
    
    selected_id = select_record("contrat", dr.get_all_contracts, display_field="id")
    if not selected_id:
        return
    
    try:
        contract = dr.get_contract_by_id(selected_id)
        click.echo(f"\n{'='*60}")
        click.echo(f"Détails du contrat ID {contract['id']}")
        click.echo(f"{'='*60}")
        click.echo(f"Montant total : {contract.get('total_amount', 0)}€")
        click.echo(f"Reste à payer : {contract.get('remaining_amount', 0)}€")
        click.echo(f"Date création : {contract.get('creation_date', '')}")
        click.echo(f"Statut : {'✓ Signé' if contract.get('is_signed', False) else '✗ Non signé'}")
        click.echo(f"Client ID : {contract.get('client_id', '')}")
        click.echo(f"Contact commercial ID : {contract.get('commercial_contact_id', '')}")
            
    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except LookupError as le:
        click.echo(f"Contrat introuvable : {le}")
    except Exception as e:
        click.echo(f"Erreur : {e}")

def view_event(user):
    """Affiche un événement spécifique."""
    dr = DataReader(user)
    
    selected_id = select_record("événement", dr.get_all_events, display_field="name")
    if not selected_id:
        return
    
    try:
        event = dr.get_event_by_id(selected_id)
        click.echo(f"\n{'='*60}")
        click.echo(f"Détails de l'événement ID {event['id']}")
        click.echo(f"{'='*60}")
        click.echo(f"Nom : {event.get('name', '')}")
        click.echo(f"Client : {event.get('client_name', '')}")
        click.echo(f"Contact client : {event.get('client_contact', '')}")
        click.echo(f"Période : {event.get('date_start', '')} au {event.get('date_end', '')}")
        click.echo(f"Lieu : {event.get('location', '')}")
        click.echo(f"Convives : {event.get('attendees', '')}")
        click.echo(f"Notes : {event.get('notes', '')}")
        click.echo(f"Contrat ID : {event.get('contract_id', '')}")
        click.echo(f"Support ID : {event.get('support_contact_id') or 'Non assigné'}")
            
    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except LookupError as le:
        click.echo(f"Événement introuvable : {le}")
    except Exception as e:
        click.echo(f"Erreur : {e}")

# ==================== FILTERED VIEWS ====================

def filter_events_view(user, permission: str):
    """Affiche les événements filtrés selon la permission (logique SQL dans filters.py)."""
    dr = DataReader(user)

    try:
        events = dr.get_filtered_events(permission)
        if not events:
            click.echo("Aucun événement trouvé.")
            return

        click.echo(f"\n{'='*60}")
        click.echo(f"Événements filtrés ({len(events)})")
        click.echo(f"{'='*60}")

        for event in events:
            name = event.get('name', '')
            support = event.get('support_contact_id') or 'Non assigné'
            click.echo(f"ID {event['id']}: '{name}' | {event.get('date_start', '')} au {event.get('date_end', '')} | Support: {support}")

    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except Exception as e:
        click.echo(f"Erreur : {e}")


def filter_contracts_view(user, permission: str):
    """Affiche les contrats filtrés selon la permission (logique SQL dans filters.py)."""
    dr = DataReader(user)

    try:
        contracts = dr.get_filtered_contracts(permission)
        if not contracts:
            click.echo("Aucun contrat trouvé.")
            return

        click.echo(f"\n{'='*60}")
        click.echo(f"Contrats filtrés ({len(contracts)})")
        click.echo(f"{'='*60}")

        for contract in contracts:
            status = "✓ Signé" if contract.get('is_signed', False) else "✗ Non signé"
            click.echo(f"ID {contract['id']}: {contract.get('total_amount', 0)}€ | {status} | Reste: {contract.get('remaining_amount', 0)}€")

    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except Exception as e:
        click.echo(f"Erreur : {e}")