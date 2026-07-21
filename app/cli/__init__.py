"""Export all handler functions for clean imports."""

from app.cli.handlers.collaborators import (
    create_collaborator,
    update_collaborator,
    delete_collaborator,
)
from app.cli.handlers.clients import (
    create_client,
    update_assigned_client,
)
from app.cli.handlers.contracts import (
    create_contract,
    update_assigned_contract,
)
from app.cli.handlers.events import (
    create_event,
    update_assigned_event,
    assign_event_support,
)
from app.cli.handlers.views import (
    view_all_clients,
    view_all_contracts,
    view_all_events,
    view_client,
    view_contract,
    view_event,
    filter_events_view,
    filter_contracts_view,
)

__all__ = [
    # Collaborators
    "create_collaborator",
    "update_collaborator",
    "delete_collaborator",
    # Clients
    "create_client",
    "update_assigned_client",
    # Contracts
    "create_contract",
    "update_assigned_contract",
    # Events
    "create_event",
    "update_assigned_event",
    "assign_event_support",
    # Views
    "view_all_clients",
    "view_all_contracts",
    "view_all_events",
    "view_client",
    "view_contract",
    "view_event",
    "filter_events_view",
    "filter_contracts_view",
]