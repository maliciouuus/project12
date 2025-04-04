"""
Tests pour le module de journalisation d'événements.

Ce module contient les tests unitaires pour le module event_logging
qui gère la journalisation des événements et des erreurs via Sentry.
"""

import pytest
from unittest.mock import patch, MagicMock, call
import os
import logging
from epic_events.event_logging import (
    init_sentry,
    log_user_action,
    log_contract_signature,
    log_error,
)


class TestEventLogging:
    """
    Tests pour le module de journalisation d'événements.
    
    Cette classe contient les tests pour vérifier le fonctionnement
    des fonctions de journalisation des événements via Sentry.
    """
    
    @patch('epic_events.event_logging.sentry_sdk')
    def test_init_sentry_test_env(self, mock_sentry_sdk):
        """
        Teste l'initialisation de Sentry en environnement de test.
        """
        # Simuler l'environnement de test
        os.environ["EPIC_EVENTS_ENV"] = "test"
        
        # Appeler la fonction
        init_sentry()
        
        # Vérifications
        mock_sentry_sdk.init.assert_called_once()
        # Vérifier que le DSN est None en mode test
        args, kwargs = mock_sentry_sdk.init.call_args
        assert kwargs["dsn"] is None
        assert kwargs["environment"] == "test"
    
    @patch('epic_events.event_logging.sentry_sdk')
    def test_init_sentry_with_dsn(self, mock_sentry_sdk):
        """
        Teste l'initialisation de Sentry avec un DSN défini.
        """
        # Configurer l'environnement
        os.environ["EPIC_EVENTS_ENV"] = "production"
        os.environ["SENTRY_DSN"] = "https://test@sentry.example.com/1"
        
        # Appeler la fonction
        init_sentry()
        
        # Vérifications
        mock_sentry_sdk.init.assert_called_once()
        args, kwargs = mock_sentry_sdk.init.call_args
        assert kwargs["dsn"] == "https://test@sentry.example.com/1"
        assert kwargs["environment"] == "production"
    
    @patch('epic_events.event_logging.sentry_sdk')
    def test_log_user_action_success(self, mock_sentry_sdk):
        """
        Teste le décorateur log_user_action en cas de succès.
        """
        # Configurer les mocks
        mock_push_scope = MagicMock()
        mock_scope = MagicMock()
        mock_push_scope.__enter__.return_value = mock_scope
        mock_sentry_sdk.push_scope.return_value = mock_push_scope
        
        # Créer une fonction de test décorée
        @log_user_action("test_action")
        def test_function(user_id, action="test"):
            return f"Success: {user_id}"
        
        # Appeler la fonction décorée
        result = test_function(123, action="login")
        
        # Vérifications
        assert result == "Success: 123"
        mock_sentry_sdk.push_scope.assert_called_once()
        mock_scope.set_tag.assert_has_calls([
            call("component", "user_management"),
            call("action_type", "test_action")
        ])
        mock_sentry_sdk.capture_message.assert_called_once_with(
            "Action utilisateur: test_action",
            level="info"
        )
    
    @patch('epic_events.event_logging.sentry_sdk')
    def test_log_user_action_exception(self, mock_sentry_sdk):
        """
        Teste le décorateur log_user_action en cas d'exception.
        """
        # Configurer les mocks
        mock_push_scope = MagicMock()
        mock_scope = MagicMock()
        mock_push_scope.__enter__.return_value = mock_scope
        mock_sentry_sdk.push_scope.return_value = mock_push_scope
        
        # Créer une fonction de test décorée qui génère une exception
        @log_user_action("test_action")
        def test_function_with_error():
            raise ValueError("Test error")
        
        # Appeler la fonction décorée
        with pytest.raises(ValueError):
            test_function_with_error()
        
        # Vérifications
        mock_sentry_sdk.push_scope.assert_called_once()
        mock_scope.set_tag.assert_has_calls([
            call("component", "user_management"),
            call("action_type", "test_action"),
            call("error_type", "ValueError")
        ])
        mock_sentry_sdk.capture_exception.assert_called_once()
    
    @patch('epic_events.event_logging.sentry_sdk')
    def test_log_contract_signature(self, mock_sentry_sdk):
        """
        Teste le décorateur log_contract_signature.
        """
        # Configurer les mocks
        mock_push_scope = MagicMock()
        mock_scope = MagicMock()
        mock_push_scope.__enter__.return_value = mock_scope
        mock_sentry_sdk.push_scope.return_value = mock_push_scope
        
        # Créer une fonction de test décorée
        @log_contract_signature
        def sign_contract(contract_id, name, client_id, total_amount, is_signed=False):
            return f"Contract {contract_id} signed: {is_signed}"
        
        # Appeler la fonction décorée avec is_signed=True
        result = sign_contract(
            contract_id=1,
            name="Test Contract",
            client_id=2,
            total_amount=1000.0,
            is_signed=True
        )
        
        # Vérifications
        assert result == "Contract 1 signed: True"
        mock_sentry_sdk.push_scope.assert_called_once()
        mock_scope.set_tag.assert_has_calls([
            call("component", "contract_management"),
            call("event_type", "contract_signature")
        ])
        mock_sentry_sdk.capture_message.assert_called_once_with(
            "Signature de contrat",
            level="info"
        )
    
    @patch('epic_events.event_logging.sentry_sdk')
    def test_log_error(self, mock_sentry_sdk):
        """
        Teste la fonction log_error.
        """
        # Configurer les mocks
        mock_push_scope = MagicMock()
        mock_scope = MagicMock()
        mock_push_scope.__enter__.return_value = mock_scope
        mock_sentry_sdk.push_scope.return_value = mock_push_scope
        
        # Créer une erreur de test
        test_error = ValueError("Test error")
        test_context = {"user_id": 123, "action": "test_action"}
        
        # Appeler la fonction
        log_error(test_error, test_context)
        
        # Vérifications
        mock_sentry_sdk.push_scope.assert_called_once()
        mock_scope.set_tag.assert_called_with("error_type", "ValueError")
        mock_scope.set_context.assert_called_with("additional_context", test_context)
        mock_sentry_sdk.capture_exception.assert_called_once_with(test_error) 