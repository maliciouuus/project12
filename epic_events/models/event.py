"""
Modèle de données pour les événements.

Ce module définit la structure et le comportement des événements dans l'application.
Un événement est lié à un contrat et un client, et est assigné à un membre de l'équipe support.
Il gère les détails de l'événement comme la date, le lieu et les notes.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from .contract import Contract


class Event(Base):
    """
    Modèle de données pour les événements.

    Un événement représente une prestation à réaliser pour un client.
    Il est lié à un contrat et est assigné à un membre de l'équipe support.

    Attributs :
        id (int) : Identifiant unique
        name (str) : Nom de l'événement
        description (str) : Description détaillée
        start_date (datetime) : Date et heure de début
        end_date (datetime) : Date et heure de fin
        location (str) : Lieu de l'événement
        attendees (int) : Nombre de participants
        notes (str) : Notes additionnelles
        contract_id (int) : ID du contrat associé
        client_id (int) : ID du client
        support_id (int) : ID du membre support assigné
        created_at (datetime) : Date de création
        updated_at (datetime) : Date de dernière modification
    """

    __tablename__ = "events"

    # Informations de base
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    location = Column(String(200), nullable=False)
    attendees = Column(Integer)
    notes = Column(Text)

    # Relations avec le contrat, le client et le support
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    contract = relationship("Contract", back_populates="events")

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="events")

    support_id = Column(Integer, ForeignKey("users.id"))
    support = relationship("User", back_populates="managed_events")

    # Horodatage
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_unassigned_events(cls, session):
        """
        Retourne les événements sans support assigné.

        Args:
            session: Session SQLAlchemy

        Returns:
            Query: Requête SQLAlchemy des événements sans support
        """
        return session.query(cls).filter(cls.support_id.is_(None))

    @classmethod
    def get_events_for_support(cls, session, support_id):
        """
        Retourne tous les événements assignés à un membre support spécifique.

        Args:
            session: Session SQLAlchemy
            support_id (int): ID du membre support

        Returns:
            Query: Requête SQLAlchemy des événements filtrés
        """
        return session.query(cls).filter_by(support_id=support_id)

    @classmethod
    def get_events_for_commercial(cls, session, commercial_id):
        """
        Retourne les événements liés aux contrats d'un commercial.

        Args:
            session: Session SQLAlchemy
            commercial_id (int): ID du commercial

        Returns:
            Query: Requête SQLAlchemy des événements filtrés
        """
        return (
            session.query(cls)
            .join(Contract)
            .filter(Contract.commercial_id == commercial_id)
        )

    def can_be_edited_by(self, user):
        """
        Vérifie si un utilisateur peut modifier l'événement.

        Un utilisateur peut modifier un événement s'il est :
        - De l'équipe de gestion
        - Le support assigné à l'événement
        - Le commercial responsable du contrat lié

        Args:
            user (User): Utilisateur à vérifier

        Returns:
            bool: True si l'utilisateur peut modifier l'événement, False sinon
        """
        from ..models import UserRole

        return (
            user.has_role(UserRole.GESTION)
            or (user.has_role(UserRole.SUPPORT) and self.support_id == user.id)
            or (
                user.has_role(UserRole.COMMERCIAL)
                and self.contract.commercial_id == user.id
            )
        )

    def __init__(self, **kwargs):
        """
        Initialise un nouvel événement.

        Args:
            **kwargs: Arguments nommés correspondant aux attributs de l'événement
                     (name, description, start_date, end_date, location, attendees,
                      notes, contract_id, client_id, support_id)
        """
        super().__init__(**kwargs)

    def __repr__(self):
        """
        Représentation textuelle de l'événement.

        Returns:
            str: Représentation de l'événement avec son nom et sa date
        """
        return f"<Event {self.name} - {self.start_date.strftime('%Y-%m-%d')}>"

    @property
    def status(self):
        """Retourne le statut de l'événement."""
        now = datetime.utcnow()
        if self.end_date < now:
            return "Terminé"
        elif self.start_date <= now <= self.end_date:
            return "En cours"
        else:
            return "À venir"

    @property
    def has_support(self):
        """Vérifie si l'événement a un support assigné."""
        return self.support_id is not None

    @property
    def is_past(self):
        """
        Vérifie si l'événement est passé.

        Returns:
            bool: True si la date de fin est passée, False sinon
        """
        return self.end_date < datetime.utcnow()

    @property
    def is_ongoing(self):
        """
        Vérifie si l'événement est en cours.

        Returns:
            bool: True si l'événement est en cours, False sinon
        """
        now = datetime.utcnow()
        return self.start_date <= now <= self.end_date

    @property
    def is_future(self):
        """
        Vérifie si l'événement est à venir.

        Returns:
            bool: True si la date de début n'est pas encore atteinte, False sinon
        """
        return self.start_date > datetime.utcnow()

    @property
    def duration_hours(self):
        """Calcule la durée de l'événement en heures."""
        delta = self.end_date - self.start_date
        return delta.total_seconds() / 3600
