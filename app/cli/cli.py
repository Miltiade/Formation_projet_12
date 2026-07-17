import click
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