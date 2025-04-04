"""
Tests pour les commandes de gestion des clients.

Ce module contient les tests unitaires pour les commandes client
définies dans epic_events/commands/client_commands.py.
"""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from epic_events.commands.client_commands import client, create, update, delete, list

class TestClientCommands:
    """
    Tests pour les commandes de gestion des clients.
    
    Cette classe contient les tests pour vérifier le fonctionnement 
    des commandes de gestion des clients (création, mise à jour, suppression, liste).
    """
    
    def test_client_group(self):
        """
        Teste que le groupe de commandes client est correctement défini.
        """
        runner = CliRunner()
        result = runner.invoke(client, ["--help"])
        assert result.exit_code == 0
        assert "Commandes de gestion des clients" in result.output
        assert "create" in result.output
        assert "delete" in result.output
        assert "update" in result.output
        assert "list" in result.output
    
    @patch('epic_events.commands.client_commands.get_session')
    def test_create_client_success(self, mock_get_session):
        """
        Teste la création réussie d'un client.
        """
        # Configuration des mocks
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_commercial = MagicMock()
        mock_commercial.role = "commercial"
        mock_session.get.return_value = mock_commercial
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        runner = CliRunner()
        result = runner.invoke(create, [
            "--first-name", "Jean",
            "--last-name", "Dupont",
            "--email", "jean@example.com",
            "--phone", "0123456789",
            "--company", "ACME",
            "--commercial-id", "1"
        ])
        
        # Vérifications
        assert result.exit_code == 0
        assert "créé avec succès" in result.output
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @patch('epic_events.commands.client_commands.get_session')
    def test_create_client_commercial_not_found(self, mock_get_session):
        """
        Teste la création d'un client avec un commercial inexistant.
        """
        # Configuration des mocks
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_session.get.return_value = None
        
        runner = CliRunner()
        result = runner.invoke(create, [
            "--first-name", "Jean",
            "--last-name", "Dupont",
            "--email", "jean@example.com",
            "--phone", "0123456789",
            "--company", "ACME",
            "--commercial-id", "999"
        ])
        
        # Vérifications
        assert "Commercial non trouvé" in result.output
        mock_session.add.assert_not_called()
    
    @patch('epic_events.commands.client_commands.get_session')
    def test_create_client_email_exists(self, mock_get_session):
        """
        Teste la création d'un client avec un email déjà existant.
        """
        # Configuration des mocks
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_commercial = MagicMock()
        mock_commercial.role = "commercial"
        mock_session.get.return_value = mock_commercial
        mock_session.query.return_value.filter_by.return_value.first.return_value = MagicMock()
        
        runner = CliRunner()
        result = runner.invoke(create, [
            "--first-name", "Jean",
            "--last-name", "Dupont",
            "--email", "existant@example.com",
            "--phone", "0123456789",
            "--commercial-id", "1"
        ])
        
        # Vérifications
        assert "adresse email existe déjà" in result.output
        mock_session.add.assert_not_called()
    
    @patch('epic_events.commands.client_commands.get_session')
    def test_update_client_success(self, mock_get_session):
        """
        Teste la mise à jour réussie d'un client.
        """
        # Configuration des mocks
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_client = MagicMock()
        mock_client.full_name = "Jean Dupont"
        mock_session.query.return_value.get.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(update, [
            "--client-id", "1",
            "--email", "nouveau@example.com",
            "--phone", "0987654321"
        ])
        
        # Vérifications
        assert result.exit_code == 0
        assert "mis à jour avec succès" in result.output
        assert mock_client.email == "nouveau@example.com"
        assert mock_client.phone == "0987654321"
        mock_session.commit.assert_called_once()
    
    @patch('epic_events.commands.client_commands.get_session')
    def test_update_client_not_found(self, mock_get_session):
        """
        Teste la mise à jour d'un client inexistant.
        """
        # Configuration des mocks
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_session.query.return_value.get.return_value = None
        
        runner = CliRunner()
        result = runner.invoke(update, [
            "--client-id", "999",
            "--email", "nouveau@example.com"
        ])
        
        # Vérifications
        assert "Client non trouvé" in result.output
        mock_session.commit.assert_not_called()
    
    @patch('epic_events.commands.client_commands.get_session')
    def test_delete_client_success(self, mock_get_session):
        """
        Teste la suppression réussie d'un client.
        """
        # Configuration des mocks
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_client = MagicMock()
        mock_client.full_name = "Jean Dupont"
        mock_session.query.return_value.get.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(delete, ["--client-id", "1"])
        
        # Vérifications
        assert result.exit_code == 0
        assert "supprimé avec succès" in result.output
        mock_session.delete.assert_called_once_with(mock_client)
        mock_session.commit.assert_called_once()
    
    @patch('epic_events.commands.client_commands.get_session')
    def test_delete_client_not_found(self, mock_get_session):
        """
        Teste la suppression d'un client inexistant.
        """
        # Configuration des mocks
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_session.query.return_value.get.return_value = None
        
        runner = CliRunner()
        result = runner.invoke(delete, ["--client-id", "999"])
        
        # Vérifications
        assert "Client non trouvé" in result.output
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()
    
    @patch('epic_events.commands.client_commands.get_session')
    def test_list_clients(self, mock_get_session):
        """
        Teste la liste des clients.
        """
        # Configuration des mocks
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_client1 = MagicMock()
        mock_client1.id = 1
        mock_client1.full_name = "Jean Dupont"
        mock_client1.email = "jean@example.com"
        mock_client1.phone = "0123456789"
        mock_client1.company_name = "ACME"
        mock_client1.commercial.full_name = "Commercial Test"
        
        mock_client2 = MagicMock()
        mock_client2.id = 2
        mock_client2.full_name = "Marie Martin"
        mock_client2.email = "marie@example.com"
        mock_client2.phone = "0987654321"
        mock_client2.company_name = "XYZ Inc"
        mock_client2.commercial.full_name = "Commercial Test"
        
        mock_session.query.return_value.all.return_value = [mock_client1, mock_client2]
        
        runner = CliRunner()
        result = runner.invoke(list)
        
        # Vérifications
        assert result.exit_code == 0
        assert "Jean Dupont" in result.output
        assert "Marie Martin" in result.output
        assert "jean@example.com" in result.output
        assert "marie@example.com" in result.output
        # On vérifie seulement que query a bien été appelé, sans vérifier le nombre d'appels
        mock_session.query.assert_called() 