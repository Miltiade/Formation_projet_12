"""
Data models for the Epic Events CRM application.
SQL injection rule: ALWAYS use %s placeholders and pass values
as a separate tuple to cursor.execute(). NEVER (EVER) use f-strings
or string concatenation in SQL queries.
"""
import hmac
from argon2 import PasswordHasher, exceptions

ph = PasswordHasher()

# ---------------------------------

class Department:
    """
    A department within the organization.
    Allowed: Gestion, Commercial, Support.
    Each department maps to a role.
    """

    ROLES = {
        "Gestion": "gestion",
        "Commercial": "commercial",
        "Support": "support",
    }

    def __init__(self, name: str):
        if name not in self.ROLES:
            allowed = ", ".join(self.ROLES)
            raise ValueError(f"Unknown department '{name}'. Allowed: {allowed}")
        self.name = name

    @property
    def role(self) -> str:
        """Role derived from department name."""
        return self.ROLES[self.name]

    def __repr__(self):
        return f"Department(name={self.name!r})"

# ---------------------------------

class Collaborator:
    """An employee of Epic Events.
    Password is name-mangled (__password) and never exposed.
    Use verify_password() to check a candidate against the stored hash.
    """

    def __init__(self, id: int, username: str, email:str, password: str, department: Department):
        self.id = id
        self.username = username
        self.email = email
        self.__password_hash = ph.hash(password)  # data stored is password's hash, not password itself
        self.department = department

    @property
    def role(self) -> str:
        """Role derived from department (gestion/commercial/support)."""
        return self.department.role

    def verify_password(self, candidate: str) -> bool:
        """Check candidate password's hash against stored password's hash."""
        try:
            return ph.verify(self.__password_hash, candidate)
        except exceptions.VerifyMismatchError:
            return False

    def __repr__(self):
        return f"Collaborator(id={self.id}, username={self.username!r}, role={self.role!r})"

# ---------------------------------

class Client:
    """A client of Epic Events, managed by a commercial collaborator."""
    def __init__(self, full_name: str, email: str, phone: str,
                company_name: str, creation_date: str, last_update_date: str,
                commercial_contact: Collaborator):
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.company_name = company_name
        self.creation_date = creation_date        # ISO format, e.g. '2025-01-15'
        self.last_update_date = last_update_date  # ISO format
        self.commercial_contact = commercial_contact

    def __repr__(self):
        return f"Client(full_name={self.full_name!r}, company={self.company_name!r})"

# ---------------------------------

class Contract:
    """A contract between Epic Events and a client. May be signed or unsigned.
    Per the spec, the 'commercial contact' 
    (i.e.: commercial collaborator associated with the client) 
    is stored directly on the contract.    
    """

    def __init__(self, id: int, total_amount: float, remaining_amount: float,
                creation_date: str, is_signed: bool, client: Client,
                commercial_contact: Collaborator):
        self.id = id
        self.total_amount = total_amount
        self.remaining_amount = remaining_amount
        self.creation_date = creation_date  # ISO format
        self.is_signed = is_signed
        self.client = client
        self.commercial_contact = commercial_contact  # spec: "Contact commercial pour le contrat"

    def __repr__(self):
        return f"Contract(id={self.id}, total={self.total_amount}, signed={self.is_signed})"

# ---------------------------------

class Event:
    """An event organized by Epic Events, created from a signed contract.
    Per the spec, the event carries its own 'client_name' and 'client_contact'
    fields, as well as a 'name'. 'support_contact' may be None if not yet assigned.
    """

    def __init__(self, name: str, id: int, client_name: str,
                client_contact: str, date_start: str, date_end: str,
                location: str, attendees: int, notes: str,
                contract: Contract, support_contact: Collaborator = None):
        self.name = name                    # e.g. "John Ouick Wedding"
        self.id = id                        # Event ID
        self.client_name = client_name      # spec: "Client name"
        self.client_contact = client_contact  # spec: "Client contact" (email + phone)
        self.date_start = date_start        # ISO datetime
        self.date_end = date_end            # ISO datetime
        self.location = location
        self.attendees = attendees
        self.notes = notes
        self.contract = contract
        self.support_contact = support_contact  # None = unassigned

    def __repr__(self):
        return f"Event(name={self.name!r}, id={self.id}, start={self.date_start!r})"
