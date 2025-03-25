"""
Configuration de la base de données avec SQLAlchemy.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# Récupérer l'URL de la base de données depuis les variables d'environnement
# ou utiliser SQLite par défaut
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///epic_events.db")

# Créer le moteur de base de données
engine = create_engine(DATABASE_URL)

# Créer une classe de base pour les modèles
Base = declarative_base()

# Créer une fabrique de sessions avec scope
SessionLocal = scoped_session(sessionmaker(bind=engine))

# Variable globale pour stocker la session de test
_test_session = None


def set_session(session):
    """Définit la session de test globale."""
    global _test_session
    _test_session = session


def get_session():
    """Crée une nouvelle session de base de données ou retourne la session de test."""
    if _test_session is not None:
        return _test_session
    return SessionLocal()


def init_db():
    """Initialise la base de données."""
    Base.metadata.create_all(engine)


def cleanup_db():
    """Nettoie les ressources de la base de données."""
    SessionLocal.remove()
