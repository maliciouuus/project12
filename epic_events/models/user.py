"""
Modèle de données pour les utilisateurs.

Ce module définit la structure et le comportement des utilisateurs dans l'application.
Il gère les différents rôles (Commercial, Support, Gestion) et leurs permissions.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from ..database import Base


class UserRole:
    """
    Définition des rôles utilisateurs disponibles dans l'application.

    Cette classe contient les constantes des différents rôles :
    - ADMIN : Administrateur système (accès total)
    - COMMERCIAL : Équipe commerciale (gestion des clients et contrats)
    - SUPPORT : Équipe support (gestion des événements assignés)
    - GESTION : Équipe de gestion (supervision globale)
    """

    ADMIN = "admin"
    COMMERCIAL = "commercial"
    SUPPORT = "support"
    GESTION = "gestion"

    @classmethod
    def choices(cls):
        """Retourne les choix possibles pour les rôles."""
        return [
            (role, role.capitalize())
            for role in [cls.ADMIN, cls.COMMERCIAL, cls.SUPPORT, cls.GESTION]
        ]


class User(Base):
    """
    Modèle de données pour les utilisateurs.

    Attributs :
        id (int) : Identifiant unique
        username (str) : Nom d'utilisateur unique
        email (str) : Adresse email unique
        password_hash (str) : Hash du mot de passe
        first_name (str) : Prénom
        last_name (str) : Nom
        role (str) : Rôle de l'utilisateur
        created_at (datetime) : Date de création
        updated_at (datetime) : Date de dernière modification
    """

    __tablename__ = "users"

    # Colonnes de base
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    role = Column(String(20), nullable=False)

    # Horodatage
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations avec les autres tables
    managed_clients = relationship("Client", back_populates="commercial", lazy=True)
    managed_contracts = relationship("Contract", back_populates="commercial", lazy=True)
    managed_events = relationship("Event", back_populates="support", lazy=True)

    def __init__(
        self,
        username,
        email,
        password=None,
        password_hash=None,
        first_name=None,
        last_name=None,
        role=None,
    ):
        """
        Initialise un nouvel utilisateur.

        Args:
            username (str): Nom d'utilisateur unique
            email (str): Adresse email
            password (str, optional): Mot de passe en clair
            password_hash (str, optional): Hash du mot de passe
            first_name (str, optional): Prénom
            last_name (str, optional): Nom
            role (str, optional): Rôle de l'utilisateur
        """
        self.username = username
        self.email = email
        if password:
            self.set_password(password)
        elif password_hash:
            self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.role = role

    def set_password(self, password):
        """
        Définit le mot de passe de l'utilisateur en le hashant.

        Args:
            password (str): Mot de passe en clair
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Vérifie si le mot de passe fourni correspond au hash stocké.

        Args:
            password (str): Mot de passe à vérifier

        Returns:
            bool: True si le mot de passe est correct, False sinon
        """
        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        """
        Vérifie si l'utilisateur a un rôle spécifique.

        Args:
            role (str): Rôle à vérifier

        Returns:
            bool: True si l'utilisateur a le rôle, False sinon
        """
        if isinstance(role, str):
            return self.role == role
        # If role is a UserRole class attribute, get its value
        return self.role == getattr(role, role.name.lower(), role)

    def is_admin(self):
        """
        Vérifie si l'utilisateur est administrateur.

        Returns:
            bool: True si admin, False sinon
        """
        return self.role == UserRole.ADMIN

    def is_commercial(self):
        """
        Vérifie si l'utilisateur est commercial.

        Returns:
            bool: True si commercial, False sinon
        """
        return self.role == UserRole.COMMERCIAL

    def is_support(self):
        """
        Vérifie si l'utilisateur est support.

        Returns:
            bool: True si support, False sinon
        """
        return self.role == UserRole.SUPPORT

    def can_manage_client(self, client):
        """
        Vérifie si l'utilisateur peut gérer un client.

        Un utilisateur peut gérer un client s'il est :
        - De l'équipe de gestion
        - Le commercial assigné au client

        Args:
            client (Client): Client à vérifier

        Returns:
            bool: True si l'utilisateur peut gérer le client, False sinon
        """
        return self.has_role(UserRole.GESTION) or (
            self.has_role(UserRole.COMMERCIAL) and client.commercial_id == self.id
        )

    def can_manage_event(self, event):
        """
        Vérifie si l'utilisateur peut gérer un événement.

        Un utilisateur peut gérer un événement s'il est :
        - De l'équipe de gestion
        - Le support assigné à l'événement
        - Le commercial responsable du contrat lié à l'événement

        Args:
            event (Event): Événement à vérifier

        Returns:
            bool: True si l'utilisateur peut gérer l'événement, False sinon
        """
        return (
            self.has_role(UserRole.GESTION)
            or (self.has_role(UserRole.SUPPORT) and event.support_id == self.id)
            or (self.has_role(UserRole.COMMERCIAL) and event.contract.commercial_id == self.id)
        )

    @property
    def full_name(self):
        """
        Retourne le nom complet de l'utilisateur.

        Returns:
            str: Prénom et nom, ou nom d'utilisateur si non définis
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def __repr__(self):
        """
        Représentation textuelle de l'utilisateur.

        Returns:
            str: Représentation de l'utilisateur
        """
        return f"<User {self.username}>"


def init_admin_user():
    """
    Crée l'utilisateur administrateur par défaut.
    Utilisé lors de l'initialisation de l'application.

    Returns:
        User: Instance de l'utilisateur admin créé
    """
    admin = User(
        username="admin",
        email="admin@example.com",
        first_name="Admin",
        last_name="System",
        role=UserRole.ADMIN,
        password="admin123",
    )
    return admin
