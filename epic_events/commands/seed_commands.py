"""
Commandes CLI pour générer des données de test.

Ce module fournit des utilitaires pour créer rapidement des données de test
représentatives pour le système CRM Epic Events : utilisateurs de différents rôles,
clients, contrats et événements. Il facilite le développement et les démonstrations.
"""

import click
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session
from ..models import User, Client, Contract, Event, UserRole
from ..database import engine

# Initialisation de la bibliothèque Faker pour générer des données fictives françaises
fake = Faker(["fr_FR"])


def get_session():
    """
    Crée et retourne une nouvelle session de base de données.

    Returns:
        Session: Une session SQLAlchemy pour interagir avec la base de données
    """
    return Session(engine)


def create_test_users(session):
    """
    Crée des utilisateurs de test pour tous les rôles.

    Cette fonction génère:
    - 3 commerciaux
    - 3 supports
    - 2 gestionnaires
    Les identifiants sont sauvegardés dans un fichier login.txt
    pour faciliter les tests.

    Args:
        session: Session SQLAlchemy active

    Returns:
        list: Liste des utilisateurs créés
    """
    users = []
    # Créer des utilisateurs pour chaque rôle
    roles = [
        (UserRole.COMMERCIAL, 3),  # 3 commerciaux
        (UserRole.SUPPORT, 3),  # 3 supports
        (UserRole.GESTION, 2),  # 2 gestionnaires
    ]

    # Ouvrir un fichier pour sauvegarder les identifiants
    with open("login.txt", "w") as f:
        f.write("=== INFORMATIONS DE CONNEXION POUR LES TESTS ===\n\n")

        # Pour chaque rôle, créer le nombre spécifié d'utilisateurs
        for role, count in roles:
            f.write(f"\n=== {role.upper()} ===\n")
            for i in range(1, count + 1):
                # Générer des informations fictives mais cohérentes
                first_name = fake.first_name()
                last_name = fake.last_name()
                username = f"{role}_{i}"
                email = f"{role}_{i}@epic-events.com"
                password = "password123"  # Mot de passe simple pour les tests

                # Créer l'utilisateur et définir son mot de passe
                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                )
                user.set_password(password)
                users.append(user)
                session.add(user)

                # Sauvegarder les identifiants dans le fichier
                f.write(f"Username: {username}\n")
                f.write(f"Password: {password}\n")
                f.write(f"Nom: {first_name} {last_name}\n")
                f.write(f"Email: {email}\n\n")

    # Valider la création des utilisateurs
    session.commit()
    return users


def create_test_clients(session, commercials):
    """
    Crée des clients de test associés aux commerciaux existants.

    Cette fonction crée 20 clients fictifs répartis aléatoirement
    entre les commerciaux disponibles.

    Args:
        session: Session SQLAlchemy active
        commercials: Liste des utilisateurs avec le rôle commercial

    Returns:
        list: Liste des clients créés
    """
    clients = []
    for _ in range(20):  # 20 clients au total
        # Générer des données clients fictives
        client = Client(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            phone=fake.phone_number(),
            company_name=fake.company(),
            commercial_id=random.choice(
                commercials
            ).id,  # Assigner aléatoirement à un commercial
        )
        clients.append(client)
        session.add(client)

    # Valider la création des clients
    session.commit()
    return clients


def create_test_contracts(session, clients, commercials):
    """
    Crée des contrats de test associés aux clients.

    Cette fonction génère entre 1 et 3 contrats pour chaque client,
    avec des statuts variés (signés ou non, payés ou non) et
    des montants réalistes.

    Args:
        session: Session SQLAlchemy active
        clients: Liste des clients existants
        commercials: Liste des commerciaux existants

    Returns:
        list: Liste des contrats créés
    """
    contracts = []
    for client in clients:
        # 1 à 3 contrats par client
        for _ in range(random.randint(1, 3)):
            # Générer un montant aléatoire entre 1000 et 50000€
            total_amount = round(random.uniform(1000, 50000), 2)

            # Décider aléatoirement si le contrat est signé et/ou payé
            is_signed = random.choice([True, False])
            is_paid = is_signed and random.choice([True, False])

            # Si le contrat est payé, le montant restant est 0
            # Sinon, c'est un pourcentage aléatoire du montant total
            remaining_amount = (
                0 if is_paid else round(total_amount * random.uniform(0.3, 1.0), 2)
            )

            # Créer le contrat
            contract = Contract(
                name=f"Contrat {fake.word()} {fake.word()}",
                description=fake.text(max_nb_chars=200),
                client_id=client.id,
                commercial_id=client.commercial_id,  # Même commercial que le client
                total_amount=total_amount,
                remaining_amount=remaining_amount,
                is_signed=is_signed,
                is_paid=is_paid,
            )
            contracts.append(contract)
            session.add(contract)

    # Valider la création des contrats
    session.commit()
    return contracts


def create_test_events(session, contracts, support_users):
    """
    Crée des événements de test associés aux contrats signés.

    Cette fonction génère 1 à 2 événements pour chaque contrat signé,
    avec des dates futures, des lieux et des nombres de participants variés.
    Chaque événement est assigné à un membre de l'équipe support.

    Args:
        session: Session SQLAlchemy active
        contracts: Liste des contrats existants
        support_users: Liste des utilisateurs avec le rôle support

    Returns:
        list: Liste des événements créés
    """
    events = []
    for contract in contracts:
        # Ne créer des événements que pour les contrats signés
        if contract.is_signed:
            # 1 à 2 événements par contrat signé
            for _ in range(random.randint(1, 2)):
                # Générer des dates dans les 6 prochains mois
                start_date = fake.date_time_between(
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=180),
                )
                # Durée de l'événement entre 2 et 8 heures
                end_date = start_date + timedelta(hours=random.randint(2, 8))

                # Créer l'événement
                event = Event(
                    name=f"Événement {fake.word()} {fake.word()}",
                    contract_id=contract.id,
                    client_id=contract.client_id,
                    support_id=random.choice(support_users).id,  # Assigner à un support
                    start_date=start_date,
                    end_date=end_date,
                    location=fake.address(),
                    attendees=random.randint(10, 200),  # Entre 10 et 200 participants
                    notes=fake.text(),
                )
                events.append(event)
                session.add(event)

    # Valider la création des événements
    session.commit()
    return events


@click.group()
def seed():
    """
    Commandes de génération de données de test.

    Ce groupe contient les commandes pour créer ou supprimer des données
    de test complètes pour l'application Epic Events.
    """
    pass


@seed.command()
def create_all():
    """
    Génère toutes les données de test.

    Cette commande crée un ensemble complet de données de test:
    - Des utilisateurs pour chaque rôle (commercial, support, gestion)
    - Des clients associés aux commerciaux
    - Des contrats associés aux clients
    - Des événements associés aux contrats signés

    Les identifiants de connexion sont sauvegardés dans login.txt.
    """
    session = get_session()

    try:
        # Création en cascade de toutes les entités
        click.echo("Création des utilisateurs de test...")
        users = create_test_users(session)
        commercials = [u for u in users if u.role == UserRole.COMMERCIAL]
        support_users = [u for u in users if u.role == UserRole.SUPPORT]

        click.echo("Création des clients de test...")
        clients = create_test_clients(session, commercials)

        click.echo("Création des contrats de test...")
        contracts = create_test_contracts(session, clients, commercials)

        click.echo("Création des événements de test...")
        events = create_test_events(session, contracts, support_users)

        # Afficher un récapitulatif des données créées
        click.echo(
            f"""
Données générées avec succès:
- {len([u for u in users if u.role == UserRole.COMMERCIAL])} commerciaux
- {len([u for u in users if u.role == UserRole.SUPPORT])} supports
- {len([u for u in users if u.role == UserRole.GESTION])} gestionnaires
- {len(clients)} clients
- {len(contracts)} contrats
- {len(events)} événements

Les identifiants ont été sauvegardés dans le fichier login.txt
"""
        )
    except Exception as e:
        # En cas d'erreur, annuler toutes les modifications
        session.rollback()
        click.echo(f"Erreur lors de la génération des données: {str(e)}")
    finally:
        # Toujours fermer la session
        session.close()


@seed.command()
def reset_all():
    """
    Supprime toutes les données de test.

    Cette commande supprime toutes les données de l'application,
    à l'exception de l'utilisateur administrateur. Elle est utile pour
    repartir d'une base propre avant de créer de nouvelles données.

    Attention: Cette action est irréversible!
    """
    session = get_session()
    try:
        # Supprimer les données dans l'ordre inverse de leur création
        # pour respecter les contraintes d'intégrité
        session.query(Event).delete()
        session.query(Contract).delete()
        session.query(Client).delete()
        session.query(User).filter(User.username != "admin").delete()
        session.commit()
        click.echo("Toutes les données de test ont été supprimées.")
    except Exception as e:
        session.rollback()
        click.echo(f"Erreur lors de la suppression des données: {str(e)}")
    finally:
        session.close()
