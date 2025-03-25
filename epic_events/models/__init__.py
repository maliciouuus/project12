"""
Package des modèles de données.

Ce module expose les modèles de données de l'application :
- User : Modèle pour les utilisateurs et leurs rôles
- Client : Modèle pour les clients
- Contract : Modèle pour les contrats
- Event : Modèle pour les événements
"""

from .user import User, UserRole
from .client import Client
from .contract import Contract
from .event import Event

__all__ = ["User", "UserRole", "Client", "Contract", "Event"]
