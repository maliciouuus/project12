"""
Configuration de la base de données avec SQLAlchemy.

Ce module définit les éléments fondamentaux de la connexion à la base de données
et fournit des utilitaires pour manipuler les sessions SQLAlchemy.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# Récupérer l'URL de la base de données depuis les variables d'environnement
# ou utiliser SQLite par défaut
# Cette approche permet de changer facilement de SGBD en production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///epic_events.db")

# Créer le moteur de base de données
# Le moteur est l'interface de bas niveau pour exécuter des requêtes SQL
engine = create_engine(DATABASE_URL)

# Créer une classe de base pour les modèles
# Tous les modèles de l'application hériteront de cette classe
# pour bénéficier des fonctionnalités ORM
Base = declarative_base()

# Créer une fabrique de sessions avec scope
# Les sessions permettent de regrouper les opérations dans des transactions
# et de les valider ou les annuler ensemble
SessionLocal = scoped_session(sessionmaker(bind=engine))

# Variable globale pour stocker la session de test
# Cette variable permet d'injecter une session de test pour les tests unitaires
_test_session = None


def set_session(session):
    """
    Définit la session de test globale.

    Cette fonction est utilisée pour l'injection de dépendances dans les tests,
    permettant de remplacer la session réelle par une session de test.

    Args:
        session: Session SQLAlchemy à utiliser pour les tests
    """
    global _test_session
    _test_session = session


def get_session():
    """
    Crée une nouvelle session de base de données ou retourne la session de test.

    Cette fonction est le point d'entrée principal pour obtenir une session
    dans toute l'application. Elle permet de masquer la complexité de la gestion
    des sessions et facilite les tests.

    Returns:
        Session SQLAlchemy: Une session pour interagir avec la base de données
    """
    if _test_session is not None:
        return _test_session
    return SessionLocal()


def init_db():
    """
    Initialise la base de données en créant toutes les tables.

    Cette fonction doit être appelée au démarrage de l'application pour
    s'assurer que toutes les tables nécessaires existent dans la base de données.
    """
    Base.metadata.create_all(engine)


def cleanup_db():
    """
    Nettoie les ressources de la base de données.

    Cette fonction doit être appelée à la fin de l'application pour
    libérer les ressources et éviter les fuites de mémoire.
    """
    SessionLocal.remove()
