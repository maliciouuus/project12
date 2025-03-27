"""
Modèle de données pour les contrats.

Ce module définit la structure et le comportement des contrats dans l'application.
Un contrat lie un client à un commercial et peut être associé à un ou plusieurs événements.
Il gère également le statut du paiement et le montant total.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ..database import Base


class Contract(Base):
    """
    Modèle de données pour les contrats.

    Un contrat représente un accord commercial entre un client et l'entreprise.
    Il est géré par un commercial et peut donner lieu à un ou plusieurs événements.

    Attributs :
        id (int) : Identifiant unique
        client_id (int) : ID du client lié au contrat
        commercial_id (int) : ID du commercial responsable
        total_amount (float) : Montant total du contrat
        remaining_amount (float) : Montant restant à payer
        is_signed (bool) : Indique si le contrat est signé
        is_paid (bool) : Indique si le contrat est entièrement payé
        status (str) : Statut du contrat (signé ou non)
        created_at (datetime) : Date de création
        updated_at (datetime) : Date de dernière modification
    """

    __tablename__ = "contracts"

    # Informations de base
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    total_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)
    is_signed = Column(Boolean, default=False)
    is_paid = Column(Boolean, default=False)
    status = Column(String(20), nullable=False, default="pending")

    # Relations avec le client et le commercial
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    client = relationship("Client", back_populates="contracts")

    commercial_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    commercial = relationship("User", back_populates="managed_contracts")

    # Horodatage
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations avec les événements
    # cascade="all, delete-orphan" signifie que la suppression d'un contrat
    # entraîne la suppression de tous ses événements
    events = relationship(
        "Event", back_populates="contract", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        """
        Initialise un nouveau contrat.

        Args:
            **kwargs: Arguments nommés correspondant aux attributs du contrat
                     (client_id, commercial_id, total_amount, remaining_amount, status)
        """
        if "remaining_amount" not in kwargs and "total_amount" in kwargs:
            kwargs["remaining_amount"] = kwargs["total_amount"]
        super().__init__(**kwargs)

    @classmethod
    def get_contracts_for_commercial(cls, session, commercial_id):
        """
        Retourne tous les contrats gérés par un commercial spécifique.

        Args:
            session: Session SQLAlchemy
            commercial_id (int): ID du commercial

        Returns:
            Query: Requête SQLAlchemy des contrats filtrés
        """
        return session.query(cls).filter_by(commercial_id=commercial_id)

    def can_be_edited_by(self, user):
        """
        Vérifie si un utilisateur peut modifier le contrat.

        Un utilisateur peut modifier un contrat s'il est :
        - De l'équipe de gestion
        - Le commercial assigné au contrat

        Args:
            user (User): Utilisateur à vérifier

        Returns:
            bool: True si l'utilisateur peut modifier le contrat, False sinon
        """
        from ..models import UserRole

        return user.has_role(UserRole.GESTION) or (
            user.has_role(UserRole.COMMERCIAL) and self.commercial_id == user.id
        )

    def is_fully_paid(self):
        """
        Vérifie si le contrat est entièrement payé.

        Returns:
            bool: True si le montant restant est nul, False sinon
        """
        return self.remaining_amount <= 0

    def record_payment(self, session, amount):
        """
        Enregistre un paiement pour le contrat.

        Args:
            session: Session SQLAlchemy
            amount (float): Montant du paiement à enregistrer

        Returns:
            bool: True si le paiement a été enregistré avec succès, False sinon
        """
        if amount <= 0 or amount > self.remaining_amount:
            return False

        self.remaining_amount -= amount
        session.commit()
        return True

    def __repr__(self):
        """
        Représentation textuelle du contrat.

        Returns:
            str: Représentation du contrat avec son ID et son nom
        """
        return f"<Contract {self.name} - ID: {self.id}>"
