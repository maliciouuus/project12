"""
Tests des modèles de données.

Ce module contient les tests unitaires pour les modèles de données
définis dans epic_events/models/.
Il permet de vérifier le bon fonctionnement des modèles, de leurs méthodes
et de leurs relations.
"""

# pytest est importé mais non utilisé directement comme import
# Cependant, il est nécessaire pour les fixtures via conftest.py
# Event est importé par les fixtures dans conftest.py
from epic_events.models import User, UserRole, Client, Contract


class TestUserModel:
    """
    Tests pour le modèle User.

    Cette classe contient les tests pour vérifier le fonctionnement du modèle User,
    incluant la création, l'authentification, la gestion des rôles et des permissions.
    """

    def test_create_user(self, db_session):
        """
        Teste la création d'un utilisateur.

        Vérifie que l'utilisateur est correctement créé avec tous ses attributs
        et enregistré dans la base de données.
        """
        # Création d'un utilisateur
        user = User(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role=UserRole.COMMERCIAL,
        )
        user.set_password("password123")

        db_session.add(user)
        db_session.commit()

        # Récupération de l'utilisateur depuis la base de données
        saved_user = db_session.query(User).filter_by(username="testuser").first()

        # Vérifications
        assert saved_user is not None
        assert saved_user.username == "testuser"
        assert saved_user.email == "test@example.com"
        assert saved_user.first_name == "Test"
        assert saved_user.last_name == "User"
        assert saved_user.role == UserRole.COMMERCIAL
        assert saved_user.check_password("password123")

    def test_password_hashing(self, db_session):
        """
        Teste le hachage du mot de passe.

        Vérifie que:
        - Le mot de passe est correctement haché (différent du texte brut)
        - La méthode check_password fonctionne pour valider le mot de passe
        - Les mauvais mots de passe sont rejetés
        """
        user = User(username="hashtest", email="hash@example.com")
        user.set_password("secret123")

        # Vérifier que le hash est différent du mot de passe
        assert user.password_hash != "secret123"

        # Vérifier que check_password fonctionne correctement
        assert user.check_password("secret123")
        assert not user.check_password("wrongpassword")

    def test_user_roles(self, admin_user, commercial_user, support_user, gestion_user):
        """
        Teste les méthodes de vérification des rôles.

        Vérifie que chaque utilisateur a le bon rôle et que
        les méthodes de vérification de rôle fonctionnent correctement.
        """
        # Vérifier les rôles des utilisateurs
        assert admin_user.is_admin()
        assert not admin_user.is_commercial()
        assert not admin_user.is_support()

        assert commercial_user.is_commercial()
        assert not commercial_user.is_admin()
        assert not commercial_user.is_support()

        assert support_user.is_support()
        assert not support_user.is_admin()
        assert not support_user.is_commercial()

        assert gestion_user.has_role(UserRole.GESTION)
        assert not gestion_user.is_admin()
        assert not gestion_user.is_commercial()
        assert not gestion_user.is_support()

    def test_user_full_name(self, admin_user):
        """
        Teste la propriété full_name.

        Vérifie que la propriété full_name retourne correctement
        la concaténation du prénom et du nom de l'utilisateur.
        """
        assert admin_user.full_name == "Admin Test"

    def test_permissions(
        self,
        db_session,
        admin_user,
        commercial_user,
        support_user,
        gestion_user,
        test_client,
        test_event,
    ):
        """
        Teste les méthodes de vérification des permissions.

        Vérifie que les différents types d'utilisateurs ont les permissions
        appropriées pour gérer des clients et des événements selon leur rôle
        et leurs responsabilités.
        """
        # Admin peut gérer n'importe quel client
        assert admin_user.can_manage_client(test_client)

        # Commercial peut gérer ses propres clients
        assert commercial_user.can_manage_client(test_client)

        # Support ne peut pas gérer les clients
        assert not support_user.can_manage_client(test_client)

        # Gestion peut gérer n'importe quel client
        assert gestion_user.can_manage_client(test_client)

        # Vérifier les permissions pour les événements
        assert admin_user.can_manage_event(test_event)
        assert commercial_user.can_manage_event(test_event)
        assert support_user.can_manage_event(
            test_event
        )  # Support assigné à l'événement
        assert gestion_user.can_manage_event(test_event)

        # Créer un autre support non assigné à l'événement
        other_support = User(
            username="other_support",
            email="other_support@example.com",
            first_name="Other",
            last_name="Support",
            role=UserRole.SUPPORT,
        )
        other_support.set_password("password123")
        db_session.add(other_support)
        db_session.commit()

        # Ce support ne devrait pas pouvoir gérer l'événement car il n'y est pas assigné
        assert not other_support.can_manage_event(test_event)


class TestClientModel:
    """
    Tests pour le modèle Client.

    Cette classe contient les tests pour vérifier le fonctionnement du modèle Client,
    incluant la création et les relations avec les autres modèles.
    """

    def test_create_client(self, db_session, commercial_user):
        """
        Teste la création d'un client.

        Vérifie que le client est correctement créé avec tous ses attributs
        et enregistré dans la base de données.
        """
        # Création d'un client
        client = Client(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+33612345678",
            company_name="ACME Corp",
            commercial_id=commercial_user.id,
        )

        db_session.add(client)
        db_session.commit()

        # Récupération du client depuis la base de données
        saved_client = (
            db_session.query(Client).filter_by(email="john.doe@example.com").first()
        )

        # Vérifications
        assert saved_client is not None
        assert saved_client.first_name == "John"
        assert saved_client.last_name == "Doe"
        assert saved_client.email == "john.doe@example.com"
        assert saved_client.phone == "+33612345678"
        assert saved_client.company_name == "ACME Corp"
        assert saved_client.commercial_id == commercial_user.id
        assert saved_client.full_name == "John Doe"

    def test_client_commercial_relationship(self, db_session, commercial_user):
        """
        Teste la relation entre client et commercial.

        Vérifie que la relation bidirectionnelle entre un client et
        son commercial est correctement établie.
        """
        client = Client(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone="+33687654321",
            commercial_id=commercial_user.id,
        )

        db_session.add(client)
        db_session.commit()

        # Vérifier que le client est associé au bon commercial
        assert client.commercial.id == commercial_user.id
        assert client.commercial.username == commercial_user.username

        # Vérifier que le commercial a ce client dans sa liste
        assert client in commercial_user.managed_clients


class TestContractModel:
    """
    Tests pour le modèle Contract.

    Cette classe contient les tests pour vérifier le fonctionnement du modèle Contract,
    incluant la création, les relations et les méthodes de paiement.
    """

    def test_create_contract(self, db_session, test_client, commercial_user):
        """
        Teste la création d'un contrat.

        Vérifie que le contrat est correctement créé avec tous ses attributs
        et enregistré dans la base de données.
        """
        # Création d'un contrat
        contract = Contract(
            name="Annual Conference",
            description="Organization of the annual company conference",
            client_id=test_client.id,
            commercial_id=commercial_user.id,
            total_amount=10000.0,
            is_signed=True,
            is_paid=False,
        )

        db_session.add(contract)
        db_session.commit()

        # Récupération du contrat depuis la base de données
        saved_contract = (
            db_session.query(Contract).filter_by(name="Annual Conference").first()
        )

        # Vérifications
        assert saved_contract is not None
        assert saved_contract.name == "Annual Conference"
        assert (
            saved_contract.description
            == "Organization of the annual company conference"
        )
        assert saved_contract.client_id == test_client.id
        assert saved_contract.commercial_id == commercial_user.id
        assert saved_contract.total_amount == 10000.0
        assert saved_contract.remaining_amount == 10000.0  # Défaut = total_amount
        assert saved_contract.is_signed
        assert not saved_contract.is_paid

    def test_contract_relationships(self, test_contract, test_client, commercial_user):
        """
        Teste les relations entre contrat, client et commercial.

        Vérifie que les relations bidirectionnelles entre un contrat,
        son client et son commercial sont correctement établies.
        """
        # Vérifier que le contrat est associé au bon client et commercial
        assert test_contract.client_id == test_client.id
        assert test_contract.commercial_id == commercial_user.id

        # Vérifier les relations bidirectionnelles
        assert test_contract in test_client.contracts
        assert test_contract in commercial_user.managed_contracts

    def test_contract_payment_methods(self, db_session, test_contract):
        """
        Teste les méthodes de paiement du contrat.

        Vérifie le fonctionnement des méthodes de paiement, notamment:
        - Le calcul du montant restant à payer
        - L'enregistrement des paiements partiels
        - Le marquage du contrat comme entièrement payé
        - La validation des montants de paiement
        """
        # Vérifier l'état initial
        assert test_contract.remaining_amount == 5000.0
        assert not test_contract.is_fully_paid()

        # Enregistrer un paiement partiel
        assert test_contract.record_payment(db_session, 2000.0)
        assert test_contract.remaining_amount == 3000.0
        assert not test_contract.is_fully_paid()

        # Enregistrer le paiement final
        assert test_contract.record_payment(db_session, 3000.0)
        assert test_contract.remaining_amount == 0.0
        assert test_contract.is_fully_paid()

        # Tester qu'on ne peut pas payer plus que le montant restant
        assert not test_contract.record_payment(db_session, 1000.0)


class TestEventModel:
    """
    Tests pour le modèle Event.

    Cette classe contient les tests pour vérifier le fonctionnement du modèle Event,
    incluant les propriétés calculées et les états temporels de l'événement.
    """

    def test_event_properties(self, test_event):
        """
        Teste les propriétés calculées de l'événement.

        Vérifie les propriétés et les méthodes de l'événement, notamment:
        - Les propriétés de base (nom, lieu, participants)
        - Les propriétés temporelles (futur, en cours, passé)
        - Le statut affiché de l'événement
        - La présence d'un contact support
        """
        from datetime import datetime, timedelta

        # Vérifier les propriétés standard
        assert test_event.name == "Test Event"
        assert test_event.location == "Test Location"
        assert test_event.attendees == 100

        # Vérifier l'état de l'événement (à venir)
        assert test_event.is_future
        assert not test_event.is_ongoing
        assert not test_event.is_past
        assert test_event.status == "À venir"
        assert test_event.has_support

        # Modifier les dates pour tester d'autres états
        now = datetime.now()

        # Événement en cours
        test_event.start_date = now - timedelta(hours=1)
        test_event.end_date = now + timedelta(hours=1)
        assert not test_event.is_future
        assert test_event.is_ongoing
        assert not test_event.is_past
        assert test_event.status == "En cours"

        # Événement passé
        test_event.start_date = now - timedelta(days=2)
        test_event.end_date = now - timedelta(days=1)
        assert not test_event.is_future
        assert not test_event.is_ongoing
        assert test_event.is_past
        assert test_event.status == "Terminé"
