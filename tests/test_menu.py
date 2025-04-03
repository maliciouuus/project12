"""
Tests du menu interactif.

Ce module contient les tests unitaires pour les fonctionnalités
du menu interactif de l'application.
Ces tests vérifient le bon fonctionnement des fonctions d'affichage,
de navigation et d'exécution de commandes du menu.
"""

# import pytest  # Non utilisé, supprimé
from unittest.mock import MagicMock  # Suppression de patch non utilisé
from epic_events.menu import clear_screen, run_command, print_header


class TestMenu:
    """
    Tests pour le module de menu interactif.

    Cette classe contient des tests unitaires pour les différentes
    fonctions du module menu, en utilisant des mocks pour simuler
    l'environnement et les dépendances externes.
    """

    def test_clear_screen(self, monkeypatch):
        """
        Teste la fonction clear_screen.

        Vérifie que la fonction appelle correctement la commande
        d'effacement d'écran appropriée selon le système d'exploitation.
        """
        # Configurer un mock pour os.system
        mock_system = MagicMock()
        monkeypatch.setattr("os.system", mock_system)

        # Appeler la fonction
        clear_screen()

        # Vérifier que os.system a été appelé avec la bonne commande
        if mock_system.call_args[0][0] == "cls":
            # Windows
            mock_system.assert_called_once_with("cls")
        else:
            # Linux/Mac
            mock_system.assert_called_once_with("clear")

    def test_run_command(self, monkeypatch):
        """
        Teste la fonction run_command.

        Vérifie que la commande est correctement formatée et exécutée
        via le module subprocess.
        """
        # Configurer un mock pour subprocess.run
        mock_run = MagicMock()
        monkeypatch.setattr("subprocess.run", mock_run)

        # Appeler la fonction
        run_command("test command")

        # Vérifier que subprocess.run a été appelé avec la bonne commande
        mock_run.assert_called_once_with(
            "python -m epic_events.cli test command", shell=True
        )

    def test_run_command_exception(self, monkeypatch):
        """
        Teste la gestion des exceptions dans run_command.

        Vérifie que les exceptions levées pendant l'exécution d'une
        commande sont correctement capturées et que le message d'erreur
        est affiché à l'utilisateur.
        """
        # Configurer un mock pour subprocess.run qui lève une exception
        mock_run = MagicMock(side_effect=Exception("Command failed"))
        monkeypatch.setattr("subprocess.run", mock_run)

        # Configurer un mock pour click.echo
        mock_echo = MagicMock()
        monkeypatch.setattr("click.echo", mock_echo)

        # Appeler la fonction
        run_command("test command")

        # Vérifier que click.echo a été appelé avec le bon message d'erreur
        mock_echo.assert_called_once_with(
            "Erreur: Command failed"
        )

    def test_print_header(self, monkeypatch):
        """
        Teste la fonction print_header.

        Vérifie que l'en-tête du menu est correctement affiché,
        avec une variante selon que l'utilisateur est connecté ou non.
        """
        # Configurer un mock pour clear_screen
        mock_clear_screen = MagicMock()
        monkeypatch.setattr("epic_events.menu.clear_screen", mock_clear_screen)

        # Configurer un mock pour click.echo
        mock_echo = MagicMock()
        monkeypatch.setattr("click.echo", mock_echo)

        # Configurer un mock pour get_current_user
        # Cas 1: Utilisateur connecté
        mock_user = MagicMock()
        mock_user.full_name = "Test User"
        mock_user.role = "admin"
        monkeypatch.setattr("epic_events.menu.get_current_user", lambda: mock_user)

        # Appeler la fonction
        print_header()

        # Vérifier que clear_screen a été appelé
        mock_clear_screen.assert_called_once()

        # Vérifier que click.echo a été appelé avec les bonnes valeurs
        assert mock_echo.call_count >= 4
        mock_echo.assert_any_call("=" * 60)
        mock_echo.assert_any_call("               EPIC EVENTS CRM - MENU")
        mock_echo.assert_any_call("=" * 60)
        mock_echo.assert_any_call("Utilisateur: Test User (admin)")

        # Cas 2: Utilisateur non connecté
        mock_clear_screen.reset_mock()
        mock_echo.reset_mock()
        monkeypatch.setattr("epic_events.menu.get_current_user", lambda: None)

        # Appeler la fonction
        print_header()

        # Vérifier les appels pour le cas d'un utilisateur non connecté
        mock_echo.assert_any_call("Non connecté")


# Note de test supplémentaire:
"""
Pour tester les menus principaux de manière plus complète,
il serait nécessaire d'utiliser une bibliothèque comme `pexpect`
pour simuler l'interaction utilisateur avec le CLI.
Ces tests plus avancés dépassent le cadre de cette suite de tests unitaires.
"""
