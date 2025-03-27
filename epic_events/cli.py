"""
Point d'entrée principal de l'application CLI Epic Events.

Ce module définit la structure globale de l'interface en ligne de commande
et intègre les différents sous-commandements (clients, contrats, événements, utilisateurs).
Il sert également de point de démarrage pour initialiser la base de données.
"""

import os
import sys
import click
from sqlalchemy.orm import Session

# Ajouter le répertoire parent au PYTHONPATH
# Cette configuration permet d'importer des modules depuis le répertoire parent
# ce qui est nécessaire pour les imports relatifs dans le package
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
    """
    Application de gestion CRM Epic Events.

    Cette application permet de gérer les clients, contrats, événements et utilisateurs
    d'une entreprise d'événementiel via une interface en ligne de commande.
    """
    pass


# Initialisation de la base de données
@cli.command()
def init():
    """
    Initialiser la base de données et créer un utilisateur administrateur.

    Cette commande crée toutes les tables nécessaires dans la base de données
    et ajoute un utilisateur administrateur initial si aucun n'existe.

    Utilisation: python -m epic_events.cli init
    """
    # Création des tables
    Base.metadata.create_all(bind=engine)
    click.echo("Base de données initialisée.")

    # Création d'un utilisateur administrateur si aucun n'existe
    session = Session(engine)
    if session.query(User).count() == 0:
        admin = User(
            username="admin",
            email="admin@epic-events.com",
            first_name="Admin",
            last_name="System",
            role=UserRole.ADMIN,
        )
        admin.set_password("admin123")
        session.add(admin)
        session.commit()
        click.echo("Utilisateur administrateur créé.")
    session.close()


# Enregistrement des commandes des différents modules
# Chaque module définit un groupe de commandes spécifiques
cli.add_command(client_commands.client)
cli.add_command(contract_commands.contract)
cli.add_command(event_commands.event)
cli.add_command(user_commands.user)
cli.add_command(seed_commands.seed)


if __name__ == "__main__":
    # Point d'entrée lorsque le script est exécuté directement
    cli()
