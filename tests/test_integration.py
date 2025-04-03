"""
Tests d'intégration pour Epic Events.

Ce module contient des tests qui vérifient l'intégration des différents
composants de l'application et les flux de travail complets.
L'objectif est de simuler des scénarios d'utilisation réels pour assurer
que toutes les parties de l'application fonctionnent correctement ensemble.
"""

# import os  # Non utilisé, supprimé
import pytest
from datetime import datetime

# from sqlalchemy.orm import Session  # Non utilisé, supprimé

from epic_events.models import User, UserRole, Client, Contract, Event
from epic_events.auth import login, logout, get_current_user


@pytest.mark.integration
class TestCompleteWorkflow:
    """
    Tests d'intégration visant à vérifier les flux de travail complets de l'application.

    Ces tests simulent des interactions réelles entre les différents composants
    du système (modèles, authentification, permissions) pour s'assurer que
    le flux de travail complet fonctionne correctement.
    """

    def test_complete_client_contract_event_workflow(
        self, db_session, admin_user, commercial_user, support_user, gestion_user
    ):
        """
        Test du flux complet: création d'un client, d'un contrat et d'un événement.

        Ce test simule le parcours complet d'un client dans l'application:
        1. Un commercial crée un client
        2. Il crée un contrat pour ce client
        3. Un gestionnaire crée un événement lié au contrat
        4. Il assigne un support à l'événement
        5. Le support met à jour les informations de l'événement

        Le test vérifie les permissions et les relations entre les objets.
        """
        # Stocker uniquement les noms d'utilisateur pour les utiliser plus tard
        commercial_username = commercial_user.username
        support_username = support_user.username
        gestion_username = gestion_user.username

        # S'assurer qu'aucun utilisateur n'est connecté
        logout()

        # 1. Connexion en tant que commercial
        user = login(commercial_username, "password123")
        assert user is not None
        current_user = get_current_user()
        assert current_user is not None
        assert current_user.username == commercial_username
        assert current_user.role == UserRole.COMMERCIAL

        # 2. Création d'un client
        client = Client(
            first_name="Jean",
            last_name="Dupont",
            email="jean.dupont@example.com",
            phone="0123456789",
            company_name="Entreprise ABC",
            commercial=current_user,
        )
        db_session.add(client)
        db_session.commit()

        # Récupérer l'ID du client pour une utilisation ultérieure
        client_id = client.id

        # Vérifier que le client a été créé
        saved_client = (
            db_session.query(Client).filter_by(email="jean.dupont@example.com").first()
        )
        assert saved_client is not None
        assert saved_client.full_name == "Jean Dupont"
        assert saved_client.commercial.username == commercial_username

        # 3. Création d'un contrat pour ce client
        contract = Contract(
            name="Contrat événementiel",
            client=saved_client,
            commercial=current_user,
            total_amount=10000.0,
            remaining_amount=10000.0,
            status="SIGNED",
        )
        db_session.add(contract)
        db_session.commit()

        # Récupérer l'ID du contrat pour une utilisation ultérieure
        contract_id = contract.id

        # Vérifier que le contrat a été créé
        saved_contract = (
            db_session.query(Contract).filter_by(client_id=saved_client.id).first()
        )
        assert saved_contract is not None
        assert saved_contract.total_amount == 10000.0
        assert saved_contract.status == "SIGNED"

        # 4. Se déconnecter et se connecter en tant que gestionnaire
        logout()
        db_session.close()  # Fermer la session actuelle

        # Ouvrir une nouvelle session et se connecter en tant que gestionnaire
        user = login(gestion_username, "password123")
        assert user is not None
        current_user = get_current_user()
        assert current_user.username == gestion_username

        # Récupérer le client et le contrat avec la nouvelle session
        client = db_session.query(Client).filter_by(id=client_id).first()
        contract = db_session.query(Contract).filter_by(id=contract_id).first()

        # 5. Créer un événement pour le contrat
        start_date = datetime.strptime("2023-12-01 09:00:00", "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime("2023-12-01 18:00:00", "%Y-%m-%d %H:%M:%S")

        event = Event(
            contract=contract,
            client=client,
            name="Conférence annuelle",
            description="Une grande conférence pour l'entreprise",
            start_date=start_date,
            end_date=end_date,
            location="Paris",
            attendees=100,
        )
        db_session.add(event)
        db_session.commit()

        # Récupérer l'ID de l'événement pour une utilisation ultérieure
        event_id = event.id

        # Vérifier que l'événement a été créé
        saved_event = db_session.query(Event).filter_by(id=event_id).first()
        assert saved_event is not None
        assert saved_event.name == "Conférence annuelle"
        assert saved_event.support is None  # Pas encore assigné

        # Trouver l'utilisateur support dans la base de données
        support_user_db = (
            db_session.query(User).filter_by(username=support_username).first()
        )

        # 6. Assigner un support à l'événement
        saved_event.support = support_user_db
        db_session.commit()

        # 7. Se déconnecter et se connecter en tant que support
        logout()
        db_session.close()  # Fermer la session actuelle

        # Ouvrir une nouvelle session et se connecter en tant que support
        user = login(support_username, "password123")
        assert user is not None
        current_user = get_current_user()
        assert current_user.username == support_username

        # 8. Mettre à jour l'événement en tant que support
        event = db_session.query(Event).filter_by(id=event_id).first()
        event.notes = "Tout est prêt pour l'événement"
        db_session.commit()

        # Vérifier les modifications
        updated_event = db_session.query(Event).filter_by(id=event_id).first()
        assert updated_event.notes == "Tout est prêt pour l'événement"
        assert updated_event.support.username == support_username

        # Vérifier que l'utilisateur support a accès à cet événement
        assert current_user.can_manage_event(updated_event) is True
