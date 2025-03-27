"""
Commandes CLI pour la gestion des clients.

Ce module définit l'interface en ligne de commande pour manipuler les clients
dans l'application Epic Events. Il permet la création, modification,
suppression et liste des clients, avec validation des données saisies.
"""

import click
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models import Client, User
from ..database import engine


def get_session():
    """
    Crée et retourne une nouvelle session de base de données.

    Returns:
        Session: Une session SQLAlchemy pour interagir avec la base de données
    """
    return Session(engine)


@click.group()
def client():
    """
    Commandes de gestion des clients.

    Ce groupe contient toutes les commandes relatives aux clients:
    - création (create)
    - suppression (delete)
    - mise à jour (update)
    - liste et filtrage (list)

    Ces commandes sont accessibles via: python -m epic_events.cli client [COMMANDE]
    """
    pass


@client.command()
@click.option("--first-name", required=True, help="Prénom du client")
@click.option("--last-name", required=True, help="Nom du client")
@click.option("--email", required=True, help="Email du client")
@click.option("--phone", required=True, help="Numéro de téléphone du client")
@click.option("--company", help="Nom de l'entreprise")
@click.option(
    "--commercial-id", type=int, required=True, help="ID du commercial assigné"
)
def create(first_name, last_name, email, phone, company, commercial_id):
    """
    Créer un nouveau client.

    Cette commande permet de créer un nouveau client dans la base de données.
    Elle effectue plusieurs validations métier:
    - L'email doit être unique
    - Le commercial spécifié doit exister et avoir le rôle "commercial"

    Le client créé sera automatiquement associé au commercial spécifié.

    Exemple:
        python -m epic_events.cli client create --first-name "Jean" --last-name "Dupont"
        --email "jean@example.com" --phone "0123456789" --company "ACME" --commercial-id 2
    """
    session = get_session()

    try:
        # Vérifier que le commercial existe et a bien le rôle commercial
        # Cette validation est essentielle car chaque client doit être
        # associé à un commercial existant
        commercial = session.get(User, commercial_id)
        if not commercial or commercial.role != "commercial":
            click.echo("Erreur: Commercial non trouvé ou utilisateur non commercial.")
            return 1

        # Vérifier si l'email existe déjà pour éviter les doublons
        # L'email est une clé unique dans le modèle Client
        if session.query(Client).filter_by(email=email).first():
            click.echo("Erreur: Cette adresse email existe déjà.")
            return 1

        # Création du client avec les informations fournies
        client = Client(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company_name=company,
            commercial_id=commercial_id,
        )

        # Persistance en base de données
        session.add(client)
        session.commit()
        click.echo(f"Client {client.full_name} créé avec succès.")
        return 0
    except IntegrityError:
        # Gestion spécifique des erreurs d'intégrité (contraintes uniques)
        session.rollback()
        click.echo("Erreur: Un client avec cette adresse email existe déjà.")
        return 1
    except Exception as e:
        # Gestion générique des autres erreurs
        session.rollback()
        click.echo(f"Erreur lors de la création du client: {str(e)}")
        return 1
    finally:
        # Nettoyage des ressources
        session.close()


@client.command()
@click.option("--client-id", type=int, required=True, help="ID du client")
def delete(client_id):
    """
    Supprimer un client.

    Cette commande supprime un client identifié par son ID.
    Attention: La suppression d'un client entraîne également la suppression
    de tous ses contrats et événements associés (cascade delete).

    Exemple:
        python -m epic_events.cli client delete --client-id 5
    """
    session = get_session()

    # Récupération du client à supprimer
    client = session.query(Client).get(client_id)
    if not client:
        click.echo("Erreur: Client non trouvé.")
        return

    try:
        # Suppression du client
        # Grâce à la configuration cascade="all, delete-orphan" dans le modèle,
        # tous les contrats et événements liés seront également supprimés
        session.delete(client)
        session.commit()
        click.echo(f"Client {client.full_name} supprimé avec succès.")
    except Exception as e:
        # En cas d'erreur, annulation de la transaction
        session.rollback()
        click.echo(f"Erreur lors de la suppression du client: {str(e)}")
    finally:
        # Nettoyage des ressources
        session.close()


@client.command()
@click.option("--client-id", type=int, required=True, help="ID du client")
@click.option("--first-name", help="Nouveau prénom")
@click.option("--last-name", help="Nouveau nom")
@click.option("--email", help="Nouvel email")
@click.option("--phone", help="Nouveau numéro de téléphone")
@click.option("--company", help="Nouveau nom d'entreprise")
def update(client_id, first_name, last_name, email, phone, company):
    """
    Mettre à jour les informations d'un client.

    Cette commande permet de modifier les propriétés d'un client existant.
    Seules les propriétés spécifiées dans les options seront modifiées.

    Exemple:
        python -m epic_events.cli client update --client-id 3 --email "nouveau@example.com"
        --phone "0987654321"
    """
    session = get_session()

    # Récupération du client à mettre à jour
    client = session.query(Client).get(client_id)
    if not client:
        click.echo("Erreur: Client non trouvé.")
        return

    # Mise à jour conditionnelle des champs
    # On ne modifie que les champs pour lesquels une valeur a été fournie
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
        # Validation des modifications
        session.commit()
        click.echo(f"Client {client.full_name} mis à jour avec succès.")
    except Exception as e:
        # En cas d'erreur, annulation de la transaction
        session.rollback()
        click.echo(f"Erreur lors de la mise à jour du client: {str(e)}")
    finally:
        # Nettoyage des ressources
        session.close()


@client.command()
@click.option("--commercial-id", type=int, help="Filtrer par commercial")
def list(commercial_id):
    """
    Lister tous les clients avec filtre optionnel.

    Cette commande affiche tous les clients ou seulement ceux
    gérés par un commercial spécifique si l'option --commercial-id est fournie.

    Exemple:
        python -m epic_events.cli client list
        python -m epic_events.cli client list --commercial-id 2
    """
    session = get_session()

    # Construction de la requête avec filtre optionnel
    query = session.query(Client)
    if commercial_id:
        query = query.filter_by(commercial_id=commercial_id)

    # Exécution de la requête
    clients = query.all()
    if not clients:
        click.echo("Aucun client trouvé.")
        return

    # Affichage des informations de chaque client
    for client in clients:
        commercial = session.query(User).get(client.commercial_id)
        click.echo(f"ID: {client.id}")
        click.echo(f"Nom: {client.full_name}")
        click.echo(f"Email: {client.email}")
        click.echo(f"Téléphone: {client.phone}")
        click.echo(f"Entreprise: {client.company_name or 'N/A'}")
        click.echo(f"Commercial: {commercial.full_name}")
        click.echo("---")

    # Nettoyage des ressources
    session.close()
