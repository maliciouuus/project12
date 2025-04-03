"""
Tests du module d'authentification.

Ce module contient les tests unitaires pour les fonctionnalités
d'authentification et de gestion des sessions de l'application.
Il vérifie le bon fonctionnement des connexions, déconnexions,
gestion des sessions, et vérification des permissions.
"""

import os
import pytest
import json
from datetime import datetime, timedelta
from epic_events.auth import (
    login,
    logout,
    get_current_user,
    require_auth,
    check_permission,
    SESSION_FILE,
    AuthenticationError,
)


class TestAuth:
    """
    Tests pour le module d'authentification.

    Cette classe contient les tests vérifiant le fonctionnement
    du système d'authentification, incluant la connexion, la déconnexion,
    la gestion des sessions et les décorateurs de permission.
    """

    def test_login_success(self, admin_user):
        """
        Teste la connexion réussie d'un utilisateur.

        Vérifie que:
        - La connexion fonctionne avec les identifiants corrects
        - Un fichier de session est créé
        - Le fichier de session contient les informations attendues
        """
        # Supprimer le fichier de session s'il existe déjà
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

        # Se connecter avec les identifiants de l'utilisateur admin
        user = login("admin_test", "password123")

        # Vérifier que la connexion a réussi
        assert user is not None
        assert user.username == "admin_test"

        # Vérifier que le fichier de session a été créé
        assert os.path.exists(SESSION_FILE)

        # Vérifier le contenu du fichier de session
        with open(SESSION_FILE, "r") as f:
            session_data = json.load(f)
            assert session_data["username"] == "admin_test"
            assert session_data["role"] == "admin"
            assert "expires_at" in session_data
            assert "user_id" in session_data

    def test_login_failure(self, admin_user):
        """
        Teste l'échec de connexion avec un mot de passe incorrect.

        Vérifie que le système rejette une tentative de connexion
        avec un mot de passe erroné et lève l'exception appropriée.
        """
        # Tenter de se connecter avec un mot de passe incorrect
        with pytest.raises(AuthenticationError):
            login("admin_test", "wrong_password")

    def test_login_nonexistent_user(self):
        """
        Teste l'échec de connexion avec un utilisateur inexistant.

        Vérifie que le système rejette une tentative de connexion
        avec un nom d'utilisateur qui n'existe pas dans la base de données.
        """
        # Tenter de se connecter avec un utilisateur inexistant
        with pytest.raises(AuthenticationError):
            login("nonexistent_user", "password123")

    def test_logout(self, admin_user):
        """
        Teste la déconnexion d'un utilisateur.

        Vérifie que:
        - La déconnexion fonctionne correctement
        - Le fichier de session est supprimé après déconnexion
        """
        # D'abord se connecter
        login("admin_test", "password123")
        assert os.path.exists(SESSION_FILE)

        # Puis se déconnecter
        result = logout()

        # Vérifier que la déconnexion a réussi
        assert result is True
        assert not os.path.exists(SESSION_FILE)

    def test_get_current_user(self, admin_user, db_session):
        """
        Teste la récupération de l'utilisateur actuellement connecté.

        Vérifie que la fonction retourne correctement l'objet User
        correspondant à l'utilisateur actuellement connecté.
        """
        # D'abord se connecter
        login("admin_test", "password123")

        # Récupérer l'utilisateur courant
        current_user = get_current_user()

        # Vérifier que c'est le bon utilisateur
        assert current_user is not None
        assert current_user.username == "admin_test"
        assert current_user.role == "admin"

    def test_expired_session(self, admin_user, monkeypatch):
        """
        Teste la gestion d'une session expirée.

        Vérifie que:
        - Une session expirée est correctement détectée
        - L'utilisateur n'est plus considéré comme connecté
        - Le fichier de session expiré est supprimé
        """
        # D'abord se connecter
        login("admin_test", "password123")

        # Créer une session expirée manuellement
        with open(SESSION_FILE, "r") as f:
            session_data = json.load(f)

        # Modifier la date d'expiration pour qu'elle soit dans le passé
        session_data["expires_at"] = (datetime.now() - timedelta(hours=1)).isoformat()

        with open(SESSION_FILE, "w") as f:
            json.dump(session_data, f)

        # Vérifier que get_current_user renvoie None pour une session expirée
        assert get_current_user() is None

        # Vérifier que le fichier de session a été supprimé
        assert not os.path.exists(SESSION_FILE)

    def test_corrupt_session(self, admin_user):
        """
        Teste la gestion d'un fichier de session corrompu.

        Vérifie que:
        - Un fichier de session corrompu est correctement géré
        - L'utilisateur n'est plus considéré comme connecté
        - Le fichier de session corrompu est supprimé
        """
        # D'abord se connecter
        login("admin_test", "password123")

        # Corrompre le fichier de session
        with open(SESSION_FILE, "w") as f:
            f.write("This is not valid JSON")

        # Vérifier que get_current_user gère correctement le fichier corrompu
        assert get_current_user() is None

        # Vérifier que le fichier corrompu a été supprimé
        assert not os.path.exists(SESSION_FILE)

    def test_require_auth_decorator(self, admin_user, monkeypatch):
        """
        Teste le décorateur require_auth.

        Vérifie que:
        - Le décorateur autorise l'exécution d'une fonction pour un utilisateur connecté
        - Le décorateur vérifie correctement le rôle de l'utilisateur
        - Le décorateur bloque l'exécution quand l'utilisateur n'a pas le bon rôle
        """
        # Configurer un mock pour get_current_user
        monkeypatch.setattr("epic_events.auth.get_current_user", lambda: admin_user)

        # Fonction de test décorée
        @require_auth()
        def test_function():
            return "Function executed"

        # Vérifier que la fonction s'exécute correctement
        assert test_function() == "Function executed"

        # Tester avec un rôle spécifique (qui correspond)
        @require_auth(role="admin")
        def test_admin_function():
            return "Admin function executed"

        assert test_admin_function() == "Admin function executed"

        # Tester avec un rôle spécifique (qui ne correspond pas)
        @require_auth(role="commercial")
        def test_commercial_function():
            return "Commercial function executed"

        # La fonction ne devrait pas s'exécuter car l'utilisateur n'a pas le bon rôle
        assert test_commercial_function() is None

    def test_check_permission_decorator(
        self, admin_user, commercial_user, test_client, monkeypatch
    ):
        """
        Teste le décorateur check_permission.

        Vérifie que:
        - Le décorateur évalue correctement les permissions avec la fonction fournie
        - Les différents types d'utilisateurs obtiennent les autorisations correctes
        - Le décorateur transmet les arguments à la fonction de vérification
        """
        # Configurer un mock pour get_current_user (admin d'abord)
        monkeypatch.setattr("epic_events.auth.get_current_user", lambda: admin_user)

        # Fonction de vérification des permissions
        def can_manage_this_client(user, client_id):
            return user.can_manage_client(test_client)

        # Fonction de test décorée
        @check_permission(can_manage_this_client)
        def manage_client(client_id):
            return f"Managing client {client_id}"

        # Vérifier que la fonction s'exécute correctement pour l'admin
        assert manage_client(test_client.id) == f"Managing client {test_client.id}"

        # Changer l'utilisateur courant pour un commercial
        monkeypatch.setattr(
            "epic_events.auth.get_current_user", lambda: commercial_user
        )

        # Vérifier que la fonction s'exécute également pour le commercial
        # (car c'est son client)
        assert manage_client(test_client.id) == f"Managing client {test_client.id}"

    def teardown_method(self):
        """
        Nettoie après chaque test.

        Supprime le fichier de session s'il existe pour assurer
        l'indépendance entre les tests.
        """
        # Supprimer le fichier de session s'il existe
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
