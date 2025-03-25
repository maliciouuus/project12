"""
Commandes CLI pour la gestion des événements.
"""

import click
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Event, Contract, User
from ..database import engine


def get_session():
    return Session(engine)


@click.group()
def event():
    """Commandes de gestion des événements."""
    pass


@event.command()
@click.option("--name", required=True, help="Nom de l'événement")
@click.option("--contract-id", type=int, required=True, help="ID du contrat")
@click.option("--start-date", required=True, help="Date et heure de début (YYYY-MM-DD HH:MM)")
@click.option("--end-date", required=True, help="Date et heure de fin (YYYY-MM-DD HH:MM)")
@click.option("--location", required=True, help="Lieu de l'événement")
@click.option("--attendees", type=int, required=True, help="Nombre de participants")
@click.option("--notes", help="Notes sur l'événement")
def create(name, contract_id, start_date, end_date, location, attendees, notes):
    """Créer un nouvel événement."""
    session = get_session()

    try:
        # Parser les dates
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
            end = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
        except ValueError:
            click.echo("Erreur: Format de date invalide. Utilisez YYYY-MM-DD HH:MM")
            return 1

        # Vérifier que la date de fin est après la date de début
        if end <= start:
            click.echo("Erreur: La date de fin doit être après la date de début.")
            return 1

        # Vérifier que le contrat existe et est signé
        contract = session.get(Contract, contract_id)
        if not contract:
            click.echo("Erreur: Contrat non trouvé.")
            return 1
        if not contract.is_signed:
            click.echo("Erreur: Le contrat doit être signé pour créer un événement.")
            return 1

        # Créer l'événement
        event = Event(
            name=name,
            contract_id=contract_id,
            client_id=contract.client_id,
            start_date=start,
            end_date=end,
            location=location,
            attendees=attendees,
            notes=notes,
        )

        session.add(event)
        session.commit()
        click.echo(f"Événement {event.name} créé avec succès.")
        return 0
    except Exception as e:
        session.rollback()
        click.echo(f"Erreur lors de la création de l'événement: {str(e)}")
        return 1
    finally:
        session.close()


@event.command()
@click.option("--event-id", type=int, required=True, help="ID de l'événement")
@click.option("--support-id", type=int, required=True, help="ID du support")
def assign_support(event_id, support_id):
    """Assigner un support à un événement."""
    session = get_session()

    try:
        event = session.query(Event).get(event_id)
        if not event:
            click.echo("Erreur: Événement non trouvé.")
            return

        support = session.query(User).get(support_id)
        if not support or support.role != "support":
            click.echo("Erreur: Support non trouvé ou utilisateur non support.")
            return

        event.support_id = support_id
        session.commit()
        click.echo(f"Support {support.full_name} assigné à l'événement {event.name}.")
    except Exception as e:
        session.rollback()
        click.echo(f"Erreur lors de l'assignation du support: {str(e)}")
    finally:
        session.close()


@event.command()
@click.option("--event-id", type=int, required=True, help="ID de l'événement")
@click.option("--name", help="Nouveau nom")
@click.option("--start-date", help="Nouvelle date de début (YYYY-MM-DD HH:MM)")
@click.option("--end-date", help="Nouvelle date de fin (YYYY-MM-DD HH:MM)")
@click.option("--location", help="Nouveau lieu")
@click.option("--attendees", type=int, help="Nouveau nombre de participants")
@click.option("--notes", help="Nouvelles notes")
def update(event_id, name, start_date, end_date, location, attendees, notes):
    """Mettre à jour un événement."""
    session = get_session()

    try:
        event = session.query(Event).get(event_id)
        if not event:
            click.echo("Erreur: Événement non trouvé.")
            return

        if name:
            event.name = name
        if start_date:
            event.start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        if end_date:
            event.end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
        if location:
            event.location = location
        if attendees is not None:
            event.attendees = attendees
        if notes:
            event.notes = notes

        session.commit()
        click.echo(f"Événement {event.name} mis à jour avec succès.")
    except Exception as e:
        session.rollback()
        click.echo(f"Erreur lors de la mise à jour de l'événement: {str(e)}")
    finally:
        session.close()


@event.command()
@click.option("--support-id", type=int, help="Filtrer par support")
@click.option("--unassigned", is_flag=True, help="Afficher les événements sans support")
@click.option("--past", is_flag=True, help="Afficher les événements passés")
@click.option("--upcoming", is_flag=True, help="Afficher les événements à venir")
@click.option("--ongoing", is_flag=True, help="Afficher les événements en cours")
def list(support_id, unassigned, past, upcoming, ongoing):
    """Lister les événements avec filtres."""
    session = get_session()
    query = session.query(Event)

    if support_id:
        query = query.filter_by(support_id=support_id)
    if unassigned:
        query = query.filter(Event.support_id.is_(None))

    events = query.all()
    if not events:
        click.echo("Aucun événement trouvé.")
        session.close()
        return

    for event in events:
        # Filtrer selon le statut temporel
        if past and not event.is_past:
            continue
        if upcoming and not event.is_future:
            continue
        if ongoing and not event.is_ongoing:
            continue

        client = session.query(Contract).get(event.contract_id).client
        support = session.query(User).get(event.support_id) if event.support_id else None

        click.echo(f"ID: {event.id}")
        click.echo(f"Nom: {event.name}")
        click.echo(f"Client: {client.full_name}")
        click.echo(f"Support: {support.full_name if support else 'Non assigné'}")
        click.echo(f"Date début: {event.start_date}")
        click.echo(f"Date fin: {event.end_date}")
        click.echo(f"Lieu: {event.location}")
        click.echo(f"Participants: {event.attendees}")
        click.echo(f"Statut: {event.status}")
        if event.notes:
            click.echo(f"Notes: {event.notes}")
        click.echo("---")

    session.close()
