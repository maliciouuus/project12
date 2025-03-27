"""
Package principal de l'application Epic Events CRM.

Ce module initialise l'application et expose les composants principaux :
- Base de données
- Modèles
- Commandes CLI
- Journalisation
"""

import os
import atexit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import User, UserRole, Client, Contract, Event
from .event_logging import init_sentry

# Configuration de la base de données
# Utilise une URL de base de données depuis les variables d'environnement
# ou replie sur SQLite par défaut
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///epic_events.db")

# Crée un moteur spécifique pour l'application
# L'argument connect_args est spécifique à SQLite pour permettre
# les accès concurrents à la base de données
app_engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    ),
)

# Crée une session avec scope pour gérer la durée de vie des sessions
# Cette approche permet de gérer automatiquement les sessions dans les requêtes web
db_session = scoped_session(sessionmaker(bind=app_engine))

# Import après la configuration pour éviter la référence circulaire
# Ces importations récupèrent les objets définis dans database.py
from .database import Base, engine, get_session  # noqa: E402

# Initialisation de Sentry pour la journalisation des événements
# Cette fonction configure Sentry avec les paramètres du fichier .env
init_sentry()


def init_db():
    """
    Initialise la base de données.

    Cette fonction crée toutes les tables définies dans les modèles
    en utilisant le moteur de base de données principal.
    """
    Base.metadata.create_all(bind=app_engine)


# Nettoyage de la session à la fin des requêtes
# Cette fonction est appelée automatiquement à la fin du programme
# pour éviter les fuites de ressources
@atexit.register
def cleanup():
    """
    Nettoie les ressources de la base de données à la fin de l'exécution.
    """
    db_session.remove()


# Liste des éléments exposés par ce module
# Ces éléments sont accessibles directement par import depuis epic_events
__all__ = [
    "Base",
    "engine",
    "get_session",
    "User",
    "UserRole",
    "Client",
    "Contract",
    "Event",
]
