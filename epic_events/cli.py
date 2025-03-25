"""
Point d'entrée principal de l'application CLI Epic Events.
"""

import os
import sys
import click
from sqlalchemy.orm import Session

# Ajouter le répertoire parent au PYTHONPATH
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Importations après avoir ajusté le PYTHONPATH
# noqa: E402 indique à flake8 d'ignorer l'erreur d'importation non en haut du fichier
from epic_events.commands import (  # noqa: E402
    client_commands,
    contract_commands,
    event_commands,
    user_commands,
    seed_commands,
)
from epic_events.database import Base, engine  # noqa: E402
from epic_events.models import User, UserRole  # noqa: E402


@click.group()
def cli():
    """Application de gestion CRM Epic Events."""
    pass


# Enregistrement des groupes de commandes
cli.add_command(client_commands.client)
cli.add_command(contract_commands.contract)
cli.add_command(event_commands.event)
cli.add_command(user_commands.user)
cli.add_command(seed_commands.seed)


@cli.command()
def init():
    """Initialise la base de données."""
    # Créer les tables
    Base.metadata.create_all(engine)

    # Créer une session
    session = Session(engine)

    try:
        # Vérifier si l'utilisateur admin existe déjà
        admin = session.query(User).filter_by(username="admin").first()
        if not admin:
            # Créer l'utilisateur admin par défaut
            admin = User(
                username="admin",
                email="admin@example.com",
                first_name="Admin",
                last_name="System",
                role=UserRole.ADMIN,
            )
            admin.set_password("admin123")
            session.add(admin)
            session.commit()
            click.echo("Utilisateur admin créé avec succès.")

        click.echo("Base de données initialisée avec succès.")
    except Exception as e:
        session.rollback()
        click.echo(f"Erreur lors de l'initialisation : {str(e)}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    cli()
