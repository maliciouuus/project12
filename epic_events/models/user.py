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

    # Constantes définissant les rôles disponibles dans l'application
    # Ces constantes sont utilisées à la fois comme valeurs stockées en base
    # et comme identifiants pour les contrôles d'accès
    ADMIN = "admin"
    COMMERCIAL = "commercial"
    SUPPORT = "support"
    GESTION = "gestion"

    @classmethod
    def choices(cls):
        """
        Retourne les choix possibles pour les rôles.

        Cette méthode est utilisée pour générer les options dans les formulaires
        ou les interfaces CLI qui nécessitent de choisir un rôle.

        Returns:
            list: Liste de tuples (valeur, libellé) pour chaque rôle
        """
        return [
            (role, role.capitalize())
            for role in [cls.ADMIN, cls.COMMERCIAL, cls.SUPPORT, cls.GESTION]
        ]


class User(Base):
    """
    Modèle de données pour les utilisateurs.

    Ce modèle représente un utilisateur du système avec son rôle et ses permissions.
    Il gère également le hachage sécurisé des mots de passe et les relations
    avec les clients, contrats et événements.

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
    # Ces champs sont automatiquement mis à jour à la création et modification
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations avec les autres tables
    # Ces relations définissent les liens entre un utilisateur et les entités qu'il gère
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
            password (str, optional): Mot de passe en clair (sera haché)
            password_hash (str, optional): Hash de mot de passe pré-calculé
            first_name (str, optional): Prénom
            last_name (str, optional): Nom
            role (str, optional): Rôle de l'utilisateur
        """
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role = role

        # Gestion du mot de passe
        if password:
            self.set_password(password)
        elif password_hash:
            self.password_hash = password_hash

    def set_password(self, password):
        """
        Définit le mot de passe de l'utilisateur en le hashant.

        Cette méthode prend un mot de passe en clair et stocke sa version
        hashée dans la base de données pour une sécurité renforcée.

        Args:
            password (str): Mot de passe en clair
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Vérifie si le mot de passe fourni correspond au hash stocké.

        Args:
            password (str): Mot de passe en clair à vérifier

        Returns:
            bool: True si le mot de passe est correct, False sinon
        """
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        """
        Vérifie si l'utilisateur a un rôle spécifique.

        Cette méthode est utilisée pour vérifier les permissions.

        Args:
            role (str): Rôle à vérifier

        Returns:
            bool: True si l'utilisateur a le rôle spécifié, False sinon
        """
        return self.role == role

    def is_admin(self):
        """
        Vérifie si l'utilisateur est un administrateur.

        Returns:
            bool: True si l'utilisateur est admin, False sinon
        """
        return self.has_role(UserRole.ADMIN)

    def is_commercial(self):
        """
        Vérifie si l'utilisateur est un commercial.

        Returns:
            bool: True si l'utilisateur est commercial, False sinon
        """
        return self.has_role(UserRole.COMMERCIAL)

    def is_support(self):
        """
        Vérifie si l'utilisateur est un support.

        Returns:
            bool: True si l'utilisateur est support, False sinon
        """
        return self.has_role(UserRole.SUPPORT)

    def can_manage_client(self, client):
        """
        Vérifie si l'utilisateur peut gérer un client spécifique.

        Un utilisateur peut gérer un client s'il est:
        - Un administrateur
        - Un membre de l'équipe de gestion
        - Le commercial assigné au client

        Args:
            client: Instance du modèle Client

        Returns:
            bool: True si l'utilisateur peut gérer le client
        """
        return (
            self.is_admin()
            or self.has_role(UserRole.GESTION)
            or (self.is_commercial() and client.commercial_id == self.id)
        )

    def can_manage_event(self, event):
        """
        Vérifie si l'utilisateur peut gérer un événement spécifique.

        Un utilisateur peut gérer un événement s'il est:
        - Un administrateur
        - Un membre de l'équipe de gestion
        - Le support assigné à l'événement
        - Le commercial responsable du client lié à l'événement

        Args:
            event: Instance du modèle Event

        Returns:
            bool: True si l'utilisateur peut gérer l'événement
        """
        return (
            self.is_admin()
            or self.has_role(UserRole.GESTION)
            or (self.is_support() and event.support_id == self.id)
            or (self.is_commercial() and event.contract.client.commercial_id == self.id)
        )

    @property
    def full_name(self):
        """
        Retourne le nom complet de l'utilisateur.

        Returns:
            str: Prénom et nom concaténés
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def __repr__(self):
        """
        Représentation textuelle de l'utilisateur.

        Utile pour le debugging et les logs.

        Returns:
            str: Représentation de l'utilisateur avec son nom et son rôle
        """
        return f"<User {self.username} ({self.role})>"


def init_admin_user():
    """
    Fonction utilitaire pour créer un utilisateur administrateur.

    Cette fonction est utilisée lors de l'initialisation de l'application
    pour garantir qu'un utilisateur admin est toujours disponible.
    """
    from sqlalchemy.orm import Session
    from ..database import engine

    session = Session(engine)

    # Vérifier si un administrateur existe déjà
    admin = session.query(User).filter_by(role=UserRole.ADMIN).first()
    if not admin:
        # Créer l'utilisateur admin
        admin = User(
            username="admin",
            email="admin@epic-events.fr",
            first_name="Admin",
            last_name="System",
            role=UserRole.ADMIN,
        )
        admin.set_password("admin123")

        session.add(admin)
        session.commit()

    session.close()
