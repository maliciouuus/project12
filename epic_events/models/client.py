"""
Modèle de données pour les clients.

Ce module définit la structure et le comportement des clients dans l'application.
Chaque client est associé à un commercial et peut avoir plusieurs contrats et événements.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .user import UserRole
from ..database import Base


class Client(Base):
    """
    Modèle de données pour les clients.

    Un client représente une entité avec laquelle l'entreprise fait affaire.
    Il est toujours associé à un commercial qui le gère.

    Attributs :
        id (int) : Identifiant unique
        first_name (str) : Prénom du client
        last_name (str) : Nom du client
        email (str) : Adresse email unique
        phone (str) : Numéro de téléphone
        company_name (str) : Nom de l'entreprise (optionnel)
        commercial_id (int) : ID du commercial responsable
        created_at (datetime) : Date de création
        updated_at (datetime) : Date de dernière modification
    """

    __tablename__ = "clients"

    # Informations de base
    id = Column(Integer, primary_key=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    company_name = Column(String(100))

    # Relation avec le commercial
    commercial_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    commercial = relationship("User", back_populates="managed_clients")

    # Horodatage
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations avec les contrats et événements
    # cascade="all, delete-orphan" signifie que la suppression d'un client
    # entraîne la suppression de tous ses contrats et événements
    contracts = relationship("Contract", back_populates="client", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="client", cascade="all, delete-orphan")

    @classmethod
    def get_clients_for_commercial(cls, session, commercial_id):
        """
        Retourne tous les clients gérés par un commercial spécifique.

        Args:
            session: Session SQLAlchemy
            commercial_id (int): ID du commercial

        Returns:
            Query: Requête SQLAlchemy des clients filtrés
        """
        return session.query(cls).filter_by(commercial_id=commercial_id)

    def can_be_edited_by(self, user):
        """
        Vérifie si un utilisateur peut modifier le client.

        Un utilisateur peut modifier un client s'il est :
        - De l'équipe de gestion
        - Le commercial assigné au client

        Args:
            user (User): Utilisateur à vérifier

        Returns:
            bool: True si l'utilisateur peut modifier le client, False sinon
        """
        return user.has_role(UserRole.GESTION) or (
            user.has_role(UserRole.COMMERCIAL) and self.commercial_id == user.id
        )

    def __init__(self, **kwargs):
        """
        Initialise un nouveau client.

        Args:
            **kwargs: Arguments nommés correspondant aux attributs du client
                     (first_name, last_name, email, phone, company_name, commercial_id)
        """
        super().__init__(**kwargs)

    @property
    def full_name(self):
        """
        Retourne le nom complet du client.

        Returns:
            str: Prénom et nom du client concaténés
        """
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        """
        Représentation textuelle du client.

        Returns:
            str: Représentation du client avec son nom complet
        """
        return f"<Client {self.full_name}>"
