"""Shared CLI utilities for user action handlers."""

import click
from typing import Callable, Optional

def select_record(label: str, list_fn: Callable, display_field: str = "name") -> Optional[int]:
    """Display list and let user select one record by ID."""
    try:
        records = list_fn()
    except PermissionError as e:
        click.echo(f"Permission refusée : {e}")
        return None

    if not records:
        click.echo(f"Aucun {label} trouvé.")
        return None

    click.echo(f"\nListe des {label}s :")
    for i, rec in enumerate(records, 1):
        click.echo(f"{i}. ID {rec['id']} - {rec.get(display_field, '')}")

    click.echo(f"{len(records) + 1}. Annuler")

    try:
        choice = click.prompt(f"Sélectionnez un {label}", type=int)
    except (ValueError, click.exceptions.Abort):
        return None

    if choice < 1 or choice > len(records):
        return None

    return records[choice - 1]["id"]

def optional_prompt(label: str, current_value, converter=str) -> Optional[any]:
    """Prompt for optional update. Empty input means 'keep current value'."""
    prompt_text = f"{label} [actuel: {current_value}, entrée vide pour garder]"
    result = click.prompt(prompt_text, type=str, default="", show_default=False)
    
    if not result.strip():
        return None
    
    try:
        return converter(result.strip())
    except ValueError:
        click.echo(f"Format invalide, valeur ignorée.")
        return None
