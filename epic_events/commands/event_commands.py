"""
Commandes CLI pour la gestion des événements.

Ce module définit l'interface en ligne de commande pour manipuler les événements
dans l'application Epic Events. Il gère le cycle de vie complet des événements,
de leur création à leur assignation à des membres de l'équipe support.
"""

import click
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Event, Contract, User
from ..database import engine


def get_session():
    """
    Crée et retourne une nouvelle session de base de données.

    Returns:
        Session: Une session SQLAlchemy pour interagir avec la base de données
    """
    return Session(engine)


@click.group()
def event():
    """
    Commandes de gestion des événements.

    Ce groupe contient toutes les commandes relatives aux événements:
    - création (create)
    - assignation de support (assign_support)
    - mise à jour (update)
    - liste et filtrage (list)

    Ces commandes sont accessibles via: python -m epic_events.cli event [COMMANDE]
    """
    pass


@event.command()
@click.option("--name", required=True, help="Nom de l'événement")
@click.option("--contract-id", type=int, required=True, help="ID du contrat")
@click.option(
    "--start-date", required=True, help="Date et heure de début (YYYY-MM-DD HH:MM)"
)
@click.option(
    "--end-date", required=True, help="Date et heure de fin (YYYY-MM-DD HH:MM)"
)
@click.option("--location", required=True, help="Lieu de l'événement")
@click.option("--attendees", type=int, required=True, help="Nombre de participants")
@click.option("--notes", help="Notes sur l'événement")
def create(name, contract_id, start_date, end_date, location, attendees, notes):
    """
    Créer un nouvel événement.

    Cette commande permet de créer un nouvel événement lié à un contrat signé.
    Elle effectue plusieurs validations métier:
    - Le contrat doit exister et être signé
    - La date de fin doit être postérieure à la date de début
    - Les dates doivent être au format valide

    L'événement est automatiquement associé au client du contrat.

    Exemple:
        python -m epic_events.cli event create --name "Séminaire Annuel" --contract-id 1
        --start-date "2023-10-15 09:00" --end-date "2023-10-15 17:00"
        --location "Hotel Royal" --attendees 50 --notes "Prévoir matériel audio"
    """
    session = get_session()

    try:
        # Analyse des dates
        # Utilisation du format standard ISO sans timezone pour plus de clarté
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
            end = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
        except ValueError:
            click.echo("Erreur: Format de date invalide. Utilisez YYYY-MM-DD HH:MM")
            return 1

        # Validation des dates: la fin doit être après le début
        if end <= start:
            click.echo("Erreur: La date de fin doit être après la date de début.")
            return 1

        # Validation du contrat: doit exister et être signé
        contract = session.get(Contract, contract_id)
        if not contract:
            click.echo("Erreur: Contrat non trouvé.")
            return 1
        if not contract.is_signed:
            click.echo("Erreur: Le contrat doit être signé pour créer un événement.")
            return 1

        # Création de l'événement
        # Association automatique au client du contrat
        event = Event(
            name=name,
            contract_id=contract_id,
            client_id=contract.client_id,  # Lié au client du contrat
            start_date=start,
            end_date=end,
            location=location,
            attendees=attendees,
            notes=notes,
        )

        # Sauvegarde de l'événement en base
        session.add(event)
        session.commit()
        click.echo(f"Événement {event.name} créé avec succès.")
        return 0
    except Exception as e:
        # Gestion des erreurs
        session.rollback()
        click.echo(f"Erreur lors de la création de l'événement: {str(e)}")
        return 1
    finally:
        # Libération des ressources
        session.close()


@event.command()
@click.option("--event-id", type=int, required=True, help="ID de l'événement")
@click.option("--support-id", type=int, required=True, help="ID du support")
def assign_support(event_id, support_id):
    """
    Assigner un support à un événement.

    Cette commande permet d'assigner un membre de l'équipe support à un événement.
    Elle vérifie que:
    - L'événement existe
    - L'utilisateur support existe et a bien le rôle "support"

    C'est une fonctionnalité clé pour la répartition du travail dans l'équipe.

    Exemple:
        python -m epic_events.cli event assign_support --event-id 1 --support-id 3
    """
    session = get_session()

    try:
        # Vérification de l'existence de l'événement
        event = session.query(Event).get(event_id)
        if not event:
            click.echo("Erreur: Événement non trouvé.")
            return

        # Vérification de l'existence du support et de son rôle
        support = session.query(User).get(support_id)
        if not support or support.role != "support":
            click.echo("Erreur: Support non trouvé ou utilisateur non support.")
            return

        # Assignation du support à l'événement
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
    """
    Mettre à jour un événement.

    Cette commande permet de modifier les propriétés d'un événement existant.
    Seules les propriétés spécifiées dans les options seront modifiées.
    Les dates, si fournies, doivent être au format valide.

    Exemple:
        python -m epic_events.cli event update --event-id 1 --name "Nouveau nom"
        --location "Nouveau lieu"
    """
    session = get_session()

    try:
        # Vérification de l'existence de l'événement
        event = session.query(Event).get(event_id)
        if not event:
            click.echo("Erreur: Événement non trouvé.")
            return

        # Mise à jour conditionnelle des champs
        # On ne modifie que les champs pour lesquels une valeur a été fournie
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

        # Validation des modifications
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
    """
    Lister les événements avec filtres.

    Cette commande affiche les événements en fonction des filtres spécifiés.
    Les filtres peuvent être combinés pour affiner la recherche.
    Trois types de filtres sont disponibles:
    - Par responsable (support assigné ou événements non assignés)
    - Par statut temporel (passés, à venir, en cours)

    Exemples:
        python -m epic_events.cli event list
        python -m epic_events.cli event list --support-id 3
        python -m epic_events.cli event list --unassigned --upcoming
    """
    session = get_session()
    query = session.query(Event)

    # Application des filtres par responsable
    if support_id:
        query = query.filter_by(support_id=support_id)
    if unassigned:
        query = query.filter(Event.support_id.is_(None))

    # Récupération des événements (sans filtrage temporel)
    events = query.all()
    if not events:
        click.echo("Aucun événement trouvé.")
        session.close()
        return

    # Affichage des événements avec filtrage temporel si nécessaire
    events_displayed = 0
    for event in events:
        # Filtrage par statut temporel - appliqué après la requête
        # car ces statuts sont calculés dynamiquement
        if past and not event.is_past:
            continue
        if upcoming and not event.is_future:
            continue
        if ongoing and not event.is_ongoing:
            continue

        # Récupération des informations associées
        client = session.query(Contract).get(event.contract_id).client
        support = (
            session.query(User).get(event.support_id) if event.support_id else None
        )

        # Affichage formaté des informations de l'événement
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
        events_displayed += 1

    # Indiquer si les filtres temporels ont masqué tous les résultats
    if events_displayed == 0:
        click.echo("Aucun événement ne correspond aux filtres temporels.")

    session.close()
