"""
Modèle de données pour les utilisateurs.

Ce module définit la structure et le comportement des utilisateurs de l'application,
notamment les rôles et les permissions.
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
        Retourne la liste des rôles disponibles.

        Returns:
            list: Liste des tuples (valeur, libellé) pour les rôles
        """
        return [
            (cls.ADMIN, "Administrateur"),
            (cls.COMMERCIAL, "Commercial"),
            (cls.SUPPORT, "Support"),
            (cls.GESTION, "Gestion"),
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
            email (str): Adresse email unique
            password (str, optional): Mot de passe (sera haché). Defaults to None.
            password_hash (str, optional): Hash du mot de passe. Defaults to None.
            first_name (str, optional): Prénom. Defaults to None.
            last_name (str, optional): Nom. Defaults to None.
            role (str, optional): Rôle de l'utilisateur. Defaults to None.
        """
        self.username = username
        self.email = email
        self.first_name = first_name or ""
        self.last_name = last_name or ""
        self.role = role or UserRole.COMMERCIAL

        if password:
            self.set_password(password)
        elif password_hash:
            self.password_hash = password_hash

    def set_password(self, password):
        """
        Définit le mot de passe haché pour l'utilisateur.

        Cette méthode prend le mot de passe en clair et le transforme
        en hash sécurisé avant de le stocker dans la base de données.
        Le mot de passe original n'est jamais stocké.

        Args:
            password (str): Mot de passe en clair
        """
        # Utiliser une méthode de hachage compatible avec toutes les versions
        # La méthode 'pbkdf2:sha256' est compatible avec la plupart des versions d'OpenSSL
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        """
        Vérifie si le mot de passe fourni correspond au hash stocké.

        Cette méthode permet de vérifier si le mot de passe fourni
        correspond au hash stocké dans la base de données, sans jamais
        manipuler le mot de passe original.

        Args:
            password (str): Mot de passe à vérifier

        Returns:
            bool: True si le mot de passe est correct, False sinon
        """
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        """
        Vérifie si l'utilisateur a un rôle spécifique.

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
        Vérifie si l'utilisateur est un membre du support.

        Returns:
            bool: True si l'utilisateur est support, False sinon
        """
        return self.has_role(UserRole.SUPPORT)

    def can_manage_client(self, client):
        """
        Vérifie si l'utilisateur peut gérer un client spécifique.

        Un utilisateur peut gérer un client s'il est :
        - De l'équipe de gestion
        - Un administrateur
        - Le commercial assigné au client

        Args:
            client (Client): Client à vérifier

        Returns:
            bool: True si l'utilisateur peut gérer le client, False sinon
        """
        if self.is_admin() or self.has_role(UserRole.GESTION):
            return True

        if self.is_commercial():
            return client.commercial_id == self.id

        return False

    def can_manage_event(self, event):
        """
        Vérifie si l'utilisateur peut gérer un événement spécifique.

        Un utilisateur peut gérer un événement s'il est :
        - De l'équipe de gestion
        - Un administrateur
        - Le commercial associé au contrat de l'événement
        - Le support assigné à l'événement

        Args:
            event (Event): Événement à vérifier

        Returns:
            bool: True si l'utilisateur peut gérer l'événement, False sinon
        """
        if self.is_admin() or self.has_role(UserRole.GESTION):
            return True

        if self.is_commercial():
            return event.contract.commercial_id == self.id

        if self.is_support():
            return event.support_id == self.id

        return False

    @property
    def full_name(self):
        """
        Retourne le nom complet de l'utilisateur.

        Returns:
            str: Prénom et nom concaténés
        """
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        """
        Représentation textuelle de l'utilisateur.

        Returns:
            str: Représentation de l'utilisateur avec son nom d'utilisateur et son rôle
        """
        return f"<User {self.username} ({self.role})>"


def init_admin_user():
    """
    Crée un utilisateur administrateur si aucun n'existe.

    Cette fonction est utilisée lors de l'initialisation de l'application
    pour s'assurer qu'il y a toujours au moins un utilisateur administrateur
    qui peut gérer le système.
    """
    from sqlalchemy.orm import Session
    from ..database import engine

    session = Session(engine)
    try:
        # Vérifier si un admin existe déjà
        admin = session.query(User).filter_by(role=UserRole.ADMIN).first()
        if not admin:
            # Créer un nouvel administrateur
            admin = User(
                username="admin",
                email="admin@epic-events.com",
                first_name="Admin",
                last_name="System",
                role=UserRole.ADMIN,
            )
            admin.set_password("admin123")
            session.add(admin)
            session.commit()
            print("Admin user created.")
    finally:
        session.close()
