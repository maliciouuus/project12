"""
Configuration pytest pour Epic Events.

Ce module définit les fixtures et la configuration nécessaires pour les tests.
Il configure l'environnement de test, crée une base de données en mémoire,
et fournit des objets préfabriqués pour faciliter les tests unitaires et d'intégration.
"""

import os
import sys
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker,
)  # Suppression de l'import non utilisé de Session

# Définir l'environnement de test pour désactiver Sentry et autres services externes
os.environ["EPIC_EVENTS_ENV"] = "test"
os.environ["SENTRY_DSN"] = ""

# Ajouter le répertoire parent au sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import après avoir configuré l'environnement
# Note: Ces imports sont placés ici intentionnellement pour éviter des problèmes
# avec la configuration de l'environnement de test qui doit être faite avant
from epic_events.database import Base, set_session  # noqa: E402
from epic_events.models import User, Client, Contract, Event, UserRole  # noqa: E402


@pytest.fixture(scope="session")
def test_engine():
    """
    Crée un moteur de base de données SQLite en mémoire pour les tests.

    Cette fixture crée une base de données temporaire en mémoire qui sera
    utilisée pour tous les tests. Cela permet d'exécuter les tests rapidement
    sans avoir besoin d'une base de données persistante.

    Returns:
        Engine: Moteur SQLAlchemy pour les tests
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def db_session(test_engine):
    """
    Crée une nouvelle session de base de données pour chaque test.

    Cette fixture isole chaque test en fournissant une session de base de données
    propre dans une transaction qui sera annulée après le test. Cela assure que
    les tests n'interfèrent pas entre eux.

    Args:
        test_engine: Fixture pour le moteur de base de données

    Yields:
        Session: Session SQLAlchemy
    """
    # Créer une session
    connection = test_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()

    # Configurer la session pour les tests
    set_session(session)

    # Fournir la session au test
    yield session

    # Nettoyer après le test
    set_session(None)
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def admin_user(db_session):
    """
    Crée un utilisateur administrateur pour les tests.

    Args:
        db_session: Fixture pour la session de base de données

    Returns:
        User: Utilisateur administrateur
    """
    user = User(
        username="admin_test",
        email="admin@test.com",
        first_name="Admin",
        last_name="Test",
        role=UserRole.ADMIN,
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def commercial_user(db_session):
    """
    Crée un utilisateur commercial pour les tests.

    Args:
        db_session: Fixture pour la session de base de données

    Returns:
        User: Utilisateur commercial
    """
    user = User(
        username="commercial_test",
        email="commercial@test.com",
        first_name="Commercial",
        last_name="Test",
        role=UserRole.COMMERCIAL,
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def support_user(db_session):
    """
    Crée un utilisateur support pour les tests.

    Args:
        db_session: Fixture pour la session de base de données

    Returns:
        User: Utilisateur support
    """
    user = User(
        username="support_test",
        email="support@test.com",
        first_name="Support",
        last_name="Test",
        role=UserRole.SUPPORT,
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def gestion_user(db_session):
    """
    Crée un utilisateur gestion pour les tests.

    Args:
        db_session: Fixture pour la session de base de données

    Returns:
        User: Utilisateur gestion
    """
    user = User(
        username="gestion_test",
        email="gestion@test.com",
        first_name="Gestion",
        last_name="Test",
        role=UserRole.GESTION,
    )
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_client(db_session, commercial_user):
    """
    Crée un client de test.

    Args:
        db_session: Fixture pour la session de base de données
        commercial_user: Fixture pour l'utilisateur commercial

    Returns:
        Client: Client de test
    """
    client = Client(
        first_name="Client",
        last_name="Test",
        email="client@test.com",
        phone="0123456789",
        company_name="Test Company",
        commercial=commercial_user,
    )
    db_session.add(client)
    db_session.commit()
    return client


@pytest.fixture
def test_contract(db_session, test_client, commercial_user):
    """
    Crée un contrat de test.

    Args:
        db_session: Fixture pour la session de base de données
        test_client: Fixture pour le client de test
        commercial_user: Fixture pour l'utilisateur commercial

    Returns:
        Contract: Contrat de test
    """
    contract = Contract(
        name="Test Contract",
        client=test_client,
        commercial=commercial_user,
        total_amount=10000.0,
        remaining_amount=5000.0,
        status="SIGNED",
    )
    db_session.add(contract)
    db_session.commit()
    return contract


@pytest.fixture
def test_event(db_session, test_contract, test_client, support_user):
    """
    Crée un événement de test.

    Args:
        db_session: Fixture pour la session de base de données
        test_contract: Fixture pour le contrat de test
        test_client: Fixture pour le client de test
        support_user: Fixture pour l'utilisateur support

    Returns:
        Event: Événement de test
    """
    # Date de début et date de fin (+ 1 jour)
    start_date = datetime.now()
    end_date = start_date + timedelta(days=1)

    event = Event(
        name="Test Event",
        description="Description for test event",
        contract=test_contract,
        client=test_client,
        support=support_user,
        start_date=start_date,
        end_date=end_date,
        location="Test Location",
        attendees=100,
    )
    db_session.add(event)
    db_session.commit()
    return event
