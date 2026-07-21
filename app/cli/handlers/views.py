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
            click.echo(f"ID {client['id']}: {client.get('full_name', client.get('name', ''))} | {client.get('email', '')} | {client.get('company_name', '')}")
            
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
            name = event.get('name', event.get('title', ''))
            click.echo(f"ID {event['id']}: '{name}' | {event.get('date_start', '')} au {event.get('end_date', event.get('date_end', ''))}")
            
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
        click.echo(f"Contact commercial ID : {client.get('commercial_contact', '')}")
            
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
        click.echo(f"Nom : {event.get('name', event.get('title', ''))}")
        click.echo(f"Client : {event.get('client_name', '')}")
        click.echo(f"Contact client : {event.get('client_contact', '')}")
        click.echo(f"Période : {event.get('date_start', '')} au {event.get('date_end', '')}")
        click.echo(f"Lieu : {event.get('location', '')}")
        click.echo(f"Convives : {event.get('attendees', '')}")
        click.echo(f"Notes : {event.get('notes', '')}")
        click.echo(f"Contrat ID : {event.get('contract_id', '')}")
        click.echo(f"Support ID : {event.get('support_contact') or 'Non assigné'}")
            
    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except LookupError as le:
        click.echo(f"Événement introuvable : {le}")
    except Exception as e:
        click.echo(f"Erreur : {e}")

# ==================== FILTERED VIEWS ====================

def filter_events_view(user):
    """Affiche une liste filtrée d'événements selon des critères."""
    dr = DataReader(user)
    
    try:
        all_events = dr.get_all_events()
        if not all_events:
            click.echo("Aucun événement trouvé.")
            return
        
        # Show filter options
        click.echo("\nCritères de filtrage :")
        click.echo("1. Tous les événements")
        click.echo("2. Événements sans support assigné")
        click.echo("3. Événements par période de date")
        
        choice = click.prompt("Choisissez un critère", type=int)
        
        filtered_events = all_events
        
        if choice == 2:
            filtered_events = [e for e in all_events if e.get('support_contact') is None]
            click.echo(f"Filtrage : événements sans support ({len(filtered_events)} trouvé(s))")
        elif choice == 3:
            start_filter = click.prompt("Date début filtre (AAA-MM-JJ)", type=str)
            end_filter = click.prompt("Date fin filtre (AAA-MM-JJ)", type=str)
            filtered_events = [
                e for e in all_events 
                if start_filter <= e.get('date_start', '') <= end_filter
            ]
            click.echo(f"Filtrage : période {start_filter} à {end_filter} ({len(filtered_events)} trouvé(s))")
        
        # Display results
        if filtered_events:
            click.echo(f"\n{'='*60}")
            click.echo(f"Événements filtrés ({len(filtered_events)})")
            click.echo(f"{'='*60}")
            for event in filtered_events:
                name = event.get('name', event.get('title', ''))
                click.echo(f"ID {event['id']}: '{name}' | {event.get('date_start', '')} au {event.get('date_end', '')}")
        else:
            click.echo("Aucun événement correspond au filtre.")
            
    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except Exception as e:
        click.echo(f"Erreur : {e}")

def filter_contracts_view(user):
    """Affiche une liste filtrée des contrats selon des critères."""
    dr = DataReader(user)
    
    try:
        all_contracts = dr.get_all_contracts()
        if not all_contracts:
            click.echo("Aucun contrat trouvé.")
            return
        
        # Show filter options
        click.echo("\nCritères de filtrage :")
        click.echo("1. Tous les contrats")
        click.echo("2. Contrats non signés")
        click.echo("3. Contrats non entièrement payés")
        
        choice = click.prompt("Choisissez un critère", type=int)
        
        filtered_contracts = all_contracts
        
        if choice == 2:
            filtered_contracts = [c for c in all_contracts if not c.get('is_signed', True)]
            click.echo(f"Filtrage : contrats non signés ({len(filtered_contracts)} trouvé(s))")
        elif choice == 3:
            filtered_contracts = [c for c in all_contracts if c.get('remaining_amount', 0) > 0]
            click.echo(f"Filtrage : contrats non entièrement payés ({len(filtered_contracts)} trouvé(s))")
        
        # Display results
        if filtered_contracts:
            click.echo(f"\n{'='*60}")
            click.echo(f"Contrats filtrés ({len(filtered_contracts)})")
            click.echo(f"{'='*60}")
            for contract in filtered_contracts:
                status = "✓ Signé" if contract.get('is_signed', False) else "✗ Non signé"
                click.echo(f"ID {contract['id']}: {contract.get('total_amount', 0)}€ | {status} | Reste: {contract.get('remaining_amount', 0)}€")
        else:
            click.echo("Aucun contrat correspond au filtre.")
            
    except PermissionError as pe:
        click.echo(f"Permission refusée : {pe}")
    except Exception as e:
        click.echo(f"Erreur : {e}")