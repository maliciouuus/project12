"""
Module d'authentification pour Epic Events CRM.

Ce module gère l'authentification des utilisateurs et le stockage
de la session courante. Il fournit des fonctions pour se connecter,
se déconnecter et vérifier les permissions de l'utilisateur actuel.
"""

import os
import json
import click
from datetime import datetime, timedelta
from .models import User
from .database import get_session

# Fichier pour stocker la session utilisateur courante
SESSION_FILE = os.path.expanduser("~/.epic_events_session")

# Durée de validité de la session en heures
SESSION_DURATION = 12


class AuthenticationError(Exception):
    """Exception levée lors d'une erreur d'authentification."""

    pass


def login(username, password):
    """
    Authentifie un utilisateur et crée une session.

    Args:
        username (str): Nom d'utilisateur
        password (str): Mot de passe

    Returns:
        User: L'utilisateur authentifié

    Raises:
        AuthenticationError: Si l'authentification échoue
    """
    session = get_session()
    try:
        # Rechercher l'utilisateur par nom d'utilisateur
        user = session.query(User).filter_by(username=username).first()

        # Vérifier que l'utilisateur existe et que le mot de passe est correct
        if not user or not user.check_password(password):
            raise AuthenticationError("Nom d'utilisateur ou mot de passe incorrect")

        # Créer une session utilisateur
        session_data = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "expires_at": (
                datetime.now() + timedelta(hours=SESSION_DURATION)
            ).isoformat(),
        }

        # Enregistrer la session dans un fichier
        with open(SESSION_FILE, "w") as f:
            json.dump(session_data, f)

        click.echo(f"Connexion réussie. Bienvenue, {user.full_name} ({user.role}).")
        return user
    finally:
        session.close()


def logout():
    """
    Déconnecte l'utilisateur actuel en supprimant le fichier de session.

    Returns:
        bool: True si la déconnexion a réussi, False sinon
    """
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
            click.echo("Déconnexion réussie.")
            return True
        else:
            click.echo("Vous n'êtes pas connecté.")
            return False
    except Exception as e:
        click.echo(f"Erreur lors de la déconnexion: {str(e)}")
        return False


def get_current_user():
    """
    Récupère l'utilisateur actuellement connecté.

    Returns:
        User: L'utilisateur connecté ou None si aucun utilisateur n'est connecté
              ou si la session a expiré
    """
    if not os.path.exists(SESSION_FILE):
        return None

    try:
        # Lire les données de session
        with open(SESSION_FILE, "r") as f:
            session_data = json.load(f)

        # Vérifier si la session a expiré
        expires_at = datetime.fromisoformat(session_data["expires_at"])
        if datetime.now() > expires_at:
            logout()
            return None

        # Récupérer l'utilisateur depuis la base de données
        session = get_session()
        try:
            return session.get(User, session_data["user_id"])
        finally:
            session.close()
    except (json.JSONDecodeError, KeyError, ValueError):
        # En cas d'erreur, supprimer le fichier de session corrompu
        logout()
        return None


def require_auth(role=None):
    """
    Décorateur pour vérifier qu'un utilisateur est connecté
    et a éventuellement un rôle spécifique.

    Args:
        role (str, optional): Rôle requis, si None, vérifie juste la connexion

    Returns:
        function: Décorateur configuré
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                click.echo(
                    "Vous devez être connecté pour accéder à cette fonctionnalité."
                )
                return

            if role and not user.has_role(role):
                click.echo(
                    f"Vous devez avoir le rôle '{role}' pour accéder à cette fonctionnalité."
                )
                return

            return func(*args, **kwargs)

        return wrapper

    return decorator


def check_permission(permission_check):
    """
    Décorateur pour vérifier qu'un utilisateur a une permission spécifique.

    Args:
        permission_check (function): Fonction qui vérifie la permission
                                    en prenant l'utilisateur et les arguments
                                    de la fonction décorée

    Returns:
        function: Décorateur configuré
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                click.echo(
                    "Vous devez être connecté pour accéder à cette fonctionnalité."
                )
                return

            if not permission_check(user, *args, **kwargs):
                click.echo(
                    "Vous n'avez pas les permissions nécessaires pour cette opération."
                )
                return

            return func(*args, **kwargs)

        return wrapper

    return decorator
