"""
Module de journalisation des événements avec Sentry.

Ce module gère la configuration de Sentry et fournit des décorateurs
pour journaliser automatiquement les événements importants.
"""

import os
import functools
from datetime import datetime
import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Charger les variables d'environnement depuis .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def init_sentry():
    """Initialise Sentry avec la configuration depuis les variables d'environnement."""
    dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("ENVIRONMENT", "development")
    send_pii = os.getenv("SENTRY_SEND_PII", "false").lower() == "true"

    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            integrations=[
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=1.0,
            send_default_pii=send_pii,
            # Configuration additionnelle pour une meilleure traçabilité
            attach_stacktrace=True,
            max_breadcrumbs=50,
            debug=environment == "development",
            # Inclure les variables d'environnement sûres
            include_local_variables=True,
            # Configuration des échantillons de performance
            profiles_sample_rate=1.0,
            # Définir les informations de release si disponibles
            release=os.getenv("APP_VERSION", "1.0.0"),
        )

        # Ajouter des tags globaux
        sentry_sdk.set_tag("app_name", "Epic Events CRM")
        sentry_sdk.set_tag("environment", environment)

        # Test d'initialisation
        print("Sentry initialisé avec succès")
    else:
        print("Sentry non configuré: DSN manquant")


def log_user_action(action_type):
    """
    Décorateur pour journaliser les actions sur les utilisateurs.

    Args:
        action_type (str): Type d'action (create_user, update_user, delete_user)
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)

                # Journaliser l'action
                with sentry_sdk.push_scope() as scope:
                    # Ajouter des tags spécifiques à l'action
                    scope.set_tag("action_type", action_type)
                    scope.set_tag("component", "user_management")

                    # Ajouter le contexte de l'utilisateur si disponible
                    if "username" in kwargs:
                        scope.set_user({"username": kwargs["username"]})
                    if "email" in kwargs:
                        scope.set_user({"email": kwargs["email"]})

                    sentry_sdk.capture_message(
                        f"Action utilisateur: {action_type}",
                        level="info",
                        extras={
                            "timestamp": datetime.utcnow().isoformat(),
                            "action": action_type,
                            "parameters": kwargs,
                        },
                    )

                return result
            except Exception as e:
                # En cas d'erreur, capturer l'exception avec le contexte
                with sentry_sdk.push_scope() as scope:
                    scope.set_tag("action_type", action_type)
                    scope.set_tag("error_type", type(e).__name__)
                    scope.set_extra("parameters", kwargs)
                    sentry_sdk.capture_exception(e)
                raise

        return wrapper

    return decorator


def log_contract_signature(func):
    """
    Décorateur pour journaliser les signatures de contrats.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)

            # Si le contrat est signé, journaliser l'événement
            if kwargs.get("is_signed"):
                with sentry_sdk.push_scope() as scope:
                    # Ajouter des tags spécifiques au contrat
                    scope.set_tag("component", "contract_management")
                    scope.set_tag("event_type", "contract_signature")

                    # Ajouter le contexte du contrat
                    scope.set_context(
                        "contract",
                        {
                            "name": kwargs.get("name"),
                            "client_id": kwargs.get("client_id"),
                            "total_amount": kwargs.get("total_amount"),
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    )

                    sentry_sdk.capture_message(
                        "Signature de contrat",
                        level="info",
                    )

            return result
        except Exception as e:
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("component", "contract_management")
                scope.set_tag("error_type", type(e).__name__)
                scope.set_context("contract_data", kwargs)
                sentry_sdk.capture_exception(e)
            raise

    return wrapper


def log_error(error, context=None):
    """
    Journalise une erreur avec son contexte.

    Args:
        error: L'erreur à journaliser
        context (dict, optional): Contexte supplémentaire
    """
    if context is None:
        context = {}

    with sentry_sdk.push_scope() as scope:
        # Ajouter des tags pour faciliter le filtrage
        scope.set_tag("error_type", type(error).__name__)
        scope.set_tag("component", context.get("component", "unknown"))

        # Ajouter le contexte de l'erreur
        scope.set_context("error_context", {"timestamp": datetime.utcnow().isoformat(), **context})

        # Capturer l'exception
        sentry_sdk.capture_exception(error)
