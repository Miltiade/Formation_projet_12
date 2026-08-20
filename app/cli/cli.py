"""
Entry: python -m app.cli.cli
How it works:
-- User must authenticate to access app
-- Main menu calls user actions (using "handlers" and "utils" for clarity)
"""

import click
import sentry_sdk
from utils.config import SENTRY_DSN

# ── Sentry initialization ──────────────────────────────────────────
# Must run BEFORE any app code so Sentry hooks are active early.
sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=1.0, # sends all performance traces
    send_default_pii=False,  # Do NOT send personally identifiable info
)

from app.cli.welcome import run_welcome_loop

@click.group()
def cli():
    """Epic Events CRM CLI."""
    pass

@cli.command()
def start():
    """Démarrer la CLI Epic Events."""
    run_welcome_loop()

if __name__ == "__main__":
    # cli()
    start()