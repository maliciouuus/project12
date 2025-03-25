"""
Commandes CLI pour la gestion des clients.
"""

import click
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models import Client, User
from ..database import engine


def get_session():
    return Session(engine)


@click.group()
def client():
    """Commandes de gestion des clients."""
    pass


@client.command()
@click.option("--first-name", required=True, help="Prénom du client")
@click.option("--last-name", required=True, help="Nom du client")
@click.option("--email", required=True, help="Email du client")
@click.option("--phone", required=True, help="Numéro de téléphone du client")
@click.option("--company", help="Nom de l'entreprise")
@click.option("--commercial-id", type=int, required=True, help="ID du commercial assigné")
def create(first_name, last_name, email, phone, company, commercial_id):
    """Créer un nouveau client."""
    session = get_session()

    try:
        # Vérifier que le commercial existe
        commercial = session.get(User, commercial_id)
        if not commercial or commercial.role != "commercial":
            click.echo("Erreur: Commercial non trouvé ou utilisateur non commercial.")
            return 1

        # Vérifier si l'email existe déjà
        if session.query(Client).filter_by(email=email).first():
            click.echo("Erreur: Cette adresse email existe déjà.")
            return 1

        client = Client(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company_name=company,
            commercial_id=commercial_id,
        )

        session.add(client)
        session.commit()
        click.echo(f"Client {client.full_name} créé avec succès.")
        return 0
    except IntegrityError:
        session.rollback()
        click.echo("Erreur: Un client avec cette adresse email existe déjà.")
        return 1
    except Exception as e:
        session.rollback()
        click.echo(f"Erreur lors de la création du client: {str(e)}")
        return 1
    finally:
        session.close()


@client.command()
@click.option("--client-id", type=int, required=True, help="ID du client")
def delete(client_id):
    """Supprimer un client."""
    session = get_session()
    client = session.query(Client).get(client_id)
    if not client:
        click.echo("Erreur: Client non trouvé.")
        return

    try:
        session.delete(client)
        session.commit()
        click.echo(f"Client {client.full_name} supprimé avec succès.")
    except Exception as e:
        session.rollback()
        click.echo(f"Erreur lors de la suppression du client: {str(e)}")
    finally:
        session.close()


@client.command()
@click.option("--client-id", type=int, required=True, help="ID du client")
@click.option("--first-name", help="Nouveau prénom")
@click.option("--last-name", help="Nouveau nom")
@click.option("--email", help="Nouvel email")
@click.option("--phone", help="Nouveau numéro de téléphone")
@click.option("--company", help="Nouveau nom d'entreprise")
def update(client_id, first_name, last_name, email, phone, company):
    """Mettre à jour les informations d'un client."""
    session = get_session()
    client = session.query(Client).get(client_id)
    if not client:
        click.echo("Erreur: Client non trouvé.")
        return

    if first_name:
        client.first_name = first_name
    if last_name:
        client.last_name = last_name
    if email:
        client.email = email
    if phone:
        client.phone = phone
    if company:
        client.company_name = company

    try:
        session.commit()
        click.echo(f"Client {client.full_name} mis à jour avec succès.")
    except Exception as e:
        session.rollback()
        click.echo(f"Erreur lors de la mise à jour du client: {str(e)}")
    finally:
        session.close()


@client.command()
@click.option("--commercial-id", type=int, help="Filtrer par commercial")
def list(commercial_id):
    """Lister tous les clients."""
    session = get_session()
    query = session.query(Client)
    if commercial_id:
        query = query.filter_by(commercial_id=commercial_id)

    clients = query.all()
    if not clients:
        click.echo("Aucun client trouvé.")
        return

    for client in clients:
        commercial = session.query(User).get(client.commercial_id)
        click.echo(f"ID: {client.id}")
        click.echo(f"Nom: {client.full_name}")
        click.echo(f"Email: {client.email}")
        click.echo(f"Téléphone: {client.phone}")
        click.echo(f"Entreprise: {client.company_name or 'N/A'}")
        click.echo(f"Commercial: {commercial.full_name}")
        click.echo("---")

    session.close()
