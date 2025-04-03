"""
Module de journalisation des événements pour Epic Events.

Ce module gère la journalisation des actions utilisateurs et des erreurs
à l'aide de Sentry. Il fournit des décorateurs pour faciliter la journalisation
des événements importants comme les connexions, les actions sur les contrats, etc.
"""

import os
import functools
import logging
from datetime import datetime
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

# Configuration du logging pour éviter les erreurs en fin d'exécution
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Désactiver les logs de debug de Sentry
sentry_logger = logging.getLogger("sentry_sdk")
sentry_logger.setLevel(logging.WARNING)


def init_sentry():
    """
    Initialise Sentry pour la journalisation des événements.

    Cette fonction configure Sentry avec le DSN fourni dans les variables
    d'environnement ou n'active pas Sentry si aucun DSN n'est fourni.
    Pour les environnements de test, Sentry est désactivé.
    """
    # Récupérer les variables d'environnement
    dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("EPIC_EVENTS_ENV", "development")

    # Ne pas initialiser Sentry si on est en mode test ou si pas de DSN configuré
    if environment == "test" or not dsn:
        # En mode test, on configure Sentry avec un transport qui ne fait rien
        sentry_sdk.init(
            dsn=None,  # Pas de DSN = pas d'envoi à Sentry
            environment=environment,
            traces_sample_rate=0.0,
            debug=False,
            integrations=[
                LoggingIntegration(
                    level=logging.INFO,  # Capture les logs de niveau INFO et supérieur
                    event_level=logging.ERROR,  # Envoie les logs de niveau ERROR comme événements
                )
            ],
        )
        logger.info(f"Sentry est désactivé (Environnement: {environment})")
        return

    # Configurer Sentry avec le DSN et les options
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        traces_sample_rate=0.1,  # Échantillonnage des traces
        debug=False,  # Désactiver le mode debug pour éviter les logs excessifs
        integrations=[
            LoggingIntegration(
                level=logging.INFO,  # Capture les logs de niveau INFO et supérieur
                event_level=logging.ERROR,  # Envoie les logs de niveau ERROR comme événements
            )
        ],
    )

    logger.info(f"Sentry est initialisé (Environnement: {environment})")


def log_user_action(action_type):
    """
    Décorateur pour journaliser les actions des utilisateurs.

    Ce décorateur capture l'action effectuée par un utilisateur dans Sentry
    avec le contexte approprié pour faciliter le suivi et l'analyse.

    Args:
        action_type (str): Type d'action (ex: "login", "create_user", etc.)

    Returns:
        function: Décorateur configuré
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Exécuter la fonction originale
                result = func(*args, **kwargs)

                # Journaliser l'action
                with sentry_sdk.push_scope() as scope:
                    # Ajouter des tags pour faciliter la recherche
                    scope.set_tag("component", "user_management")
                    scope.set_tag("action_type", action_type)

                    # Ajouter le contexte de l'action
                    scope.set_context(
                        "action_details",
                        {
                            "args": str(args),
                            "kwargs": {
                                k: v for k, v in kwargs.items() if k != "password"
                            },
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    )

                    # Capturer un message informatif
                    sentry_sdk.capture_message(
                        f"Action utilisateur: {action_type}",
                        level="info",
                    )

                return result
            except Exception as e:
                # En cas d'erreur, capturer l'exception avec le contexte
                with sentry_sdk.push_scope() as scope:
                    scope.set_tag("component", "user_management")
                    scope.set_tag("action_type", action_type)
                    scope.set_tag("error_type", type(e).__name__)
                    scope.set_context(
                        "action_context",
                        {
                            "args": str(args),
                            "kwargs": {
                                k: v for k, v in kwargs.items() if k != "password"
                            },
                        },
                    )
                    sentry_sdk.capture_exception(e)
                raise  # Re-lever l'exception pour le traitement normal

        return wrapper

    return decorator


def log_contract_signature(func):
    """
    Décorateur pour journaliser les signatures de contrats.

    Ce décorateur capture les événements de signature de contrats dans Sentry
    pour permettre le suivi des contrats dans la plateforme.

    Args:
        func (function): Fonction à décorer

    Returns:
        function: Fonction décorée
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Exécuter la fonction originale
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

                    # Capturer un message informatif
                    sentry_sdk.capture_message(
                        "Signature de contrat",
                        level="info",
                    )

            return result
        except Exception as e:
            # En cas d'erreur, capturer l'exception avec le contexte
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("component", "contract_management")
                scope.set_tag("error_type", type(e).__name__)
                scope.set_context("contract_data", kwargs)
                sentry_sdk.capture_exception(e)
            raise  # Re-lever l'exception pour le traitement normal

    return wrapper


def log_error(error, context=None):
    """
    Journalise une erreur dans Sentry avec le contexte fourni.

    Args:
        error (Exception): Erreur à journaliser
        context (dict, optional): Contexte additionnel. Defaults to None.
    """
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("error_type", type(error).__name__)
        if context:
            scope.set_context("additional_context", context)
        sentry_sdk.capture_exception(error)
        logger.error(f"Erreur: {error}")
