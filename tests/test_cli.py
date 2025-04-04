"""
Tests pour l'interface en ligne de commande.

Ce module contient les tests unitaires pour le module cli.py
qui définit l'interface en ligne de commande principale de l'application.
"""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from epic_events.cli import cli, init, menu, test as cli_test_command

class TestCLI:
    """
    Tests pour l'interface en ligne de commande.
    
    Cette classe contient les tests pour vérifier le fonctionnement 
    de l'interface CLI principale, notamment les commandes de base.
    """
    
    def test_cli_group(self):
        """
        Teste que le groupe de commandes CLI est correctement défini.
        """
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Application de gestion CRM Epic Events" in result.output
        
    @patch('epic_events.cli.Base')
    @patch('epic_events.cli.Session')
    def test_init_command(self, mock_session, mock_base):
        """
        Teste la commande d'initialisation de la base de données.
        """
        # Configuration des mocks
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.query.return_value.count.return_value = 0
        
        runner = CliRunner()
        result = runner.invoke(init)
        
        # Vérifications
        assert result.exit_code == 0
        assert "Base de données initialisée" in result.output
        assert "Utilisateur administrateur créé" in result.output
        mock_base.metadata.create_all.assert_called_once()
        mock_session_instance.add.assert_called_once()
        mock_session_instance.commit.assert_called_once()
        mock_session_instance.close.assert_called_once()
        
    @patch('epic_events.cli.start_menu')
    def test_menu_command(self, mock_start_menu):
        """
        Teste la commande qui lance le menu interactif.
        """
        runner = CliRunner()
        result = runner.invoke(menu)
        
        assert result.exit_code == 0
        mock_start_menu.assert_called_once()
        
    @patch('epic_events.cli.subprocess.run')
    def test_test_command(self, mock_run):
        """
        Teste la commande qui exécute les tests.
        """
        # Configuration du mock
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        runner = CliRunner()
        
        # Test sans options
        result = runner.invoke(cli_test_command)
        assert result.exit_code == 0
        mock_run.assert_called_with("pytest", shell=True)
        
        # Test avec options
        mock_run.reset_mock()
        result = runner.invoke(cli_test_command, ["--verbose", "--coverage", "tests/test_auth.py"])
        assert result.exit_code == 0
        mock_run.assert_called_with(
            "pytest -v --cov=epic_events --cov-report=term-missing tests/test_auth.py", 
            shell=True
        )
        
        # Test avec erreur
        mock_run.reset_mock()
        mock_process.returncode = 1
        result = runner.invoke(cli_test_command)
        assert result.exit_code == 1 