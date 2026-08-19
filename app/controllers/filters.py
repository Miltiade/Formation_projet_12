"""
Filter functions for events and contracts.
Each function takes a Collaborator and returns (sql_where_clause, params_tuple).
These are referenced by permission string in authorizations.py via the FILTERS registry.
"""

from app.models.classes import Collaborator


# ==================== EVENT FILTERS ====================

def filter_unassigned_events(user: Collaborator) -> tuple[str, tuple]:
    """Events with no support contact assigned (Gestion)."""
    return "support_contact IS NULL", ()


def filter_own_events(user: Collaborator) -> tuple[str, tuple]:
    """Events assigned to the current user (Support)."""
    return "support_contact = %s", (user.id,)


# ==================== CONTRACT FILTERS ====================

def filter_unsigned_contracts(user: Collaborator) -> tuple[str, tuple]:
    """Contracts not yet signed."""
    return "is_signed = FALSE", ()


def filter_unpaid_contracts(user: Collaborator) -> tuple[str, tuple]:
    """Contracts with remaining amount owed."""
    return "remaining_amount > 0", ()


# ==================== REGISTRY ====================

FILTERS: dict[str, callable] = {
    "filter_unassigned_events": filter_unassigned_events,
    "filter_own_events": filter_own_events,
    "filter_unsigned_contracts": filter_unsigned_contracts,
    "filter_unpaid_contracts": filter_unpaid_contracts,
}