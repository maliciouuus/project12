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
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///epic_events.db")
# Créer un moteur spécifique pour l'application
app_engine = create_engine(
    DATABASE_URL,
    connect_args=({"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}),
)
db_session = scoped_session(sessionmaker(bind=app_engine))

# Import après la configuration pour éviter la référence circulaire
from .database import Base, engine, get_session  # noqa: E402

# Initialisation de Sentry
init_sentry()


def init_db():
    """Initialise la base de données."""
    Base.metadata.create_all(bind=app_engine)


# Nettoyage de la session à la fin des requêtes
@atexit.register
def cleanup():
    db_session.remove()


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
