"""
Commandes CLI pour générer des données de test.
"""

import click
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session
from ..models import User, Client, Contract, Event, UserRole
from ..database import engine

fake = Faker(["fr_FR"])


def get_session():
    return Session(engine)


def create_test_users(session):
    """Crée des utilisateurs de test pour chaque rôle."""
    users = []
    roles = [UserRole.COMMERCIAL, UserRole.SUPPORT, UserRole.GESTION]

    # Créer le fichier login.txt
    with open("login.txt", "w") as f:
        f.write("Identifiants de connexion Epic Events CRM\n")
        f.write("=====================================\n\n")

        for role in roles:
            f.write(f"\nUtilisateurs {role.capitalize()}\n")
            f.write("-" * len(f"Utilisateurs {role.capitalize()}") + "\n")
            for i in range(3):  # 3 utilisateurs par rôle
                username = f"{role}_{i+1}"
                email = f"{username}@epic-events.fr"
                user = User(
                    username=username,
                    email=email,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    role=role,
                    password="password123",
                )
                users.append(user)
                session.add(user)
                f.write(f"Username: {username}\n")
                f.write(f"Email: {email}\n")
                f.write("Password: password123\n")
                f.write("\n")

    session.commit()
    return users


def create_test_clients(session, commercials):
    """Crée des clients de test."""
    clients = []
    for _ in range(20):  # 20 clients
        client = Client(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            phone=fake.phone_number(),
            company_name=fake.company(),
            commercial_id=random.choice(commercials).id,
        )
        clients.append(client)
        session.add(client)

    session.commit()
    return clients


def create_test_contracts(session, clients, commercials):
    """Crée des contrats de test."""
    contracts = []
    for client in clients:
        # 1 à 3 contrats par client
        for _ in range(random.randint(1, 3)):
            is_signed = random.choice([True, False])
            is_paid = is_signed and random.choice([True, False])
            total_amount = random.randint(1000, 50000)

            contract = Contract(
                name=f"Contrat {fake.word()} {fake.word()}",
                description=fake.text(),
                client_id=client.id,
                commercial_id=client.commercial_id,
                total_amount=total_amount,
                remaining_amount=0 if is_paid else total_amount,
                is_signed=is_signed,
                is_paid=is_paid,
            )
            contracts.append(contract)
            session.add(contract)

    session.commit()
    return contracts


def create_test_events(session, contracts, support_users):
    """Crée des événements de test."""
    events = []
    for contract in contracts:
        if contract.is_signed:
            # 1 à 2 événements par contrat signé
            for _ in range(random.randint(1, 2)):
                start_date = fake.date_time_between(
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=180),
                )
                end_date = start_date + timedelta(hours=random.randint(2, 8))

                event = Event(
                    name=f"Événement {fake.word()} {fake.word()}",
                    contract_id=contract.id,
                    client_id=contract.client_id,
                    support_id=random.choice(support_users).id,
                    start_date=start_date,
                    end_date=end_date,
                    location=fake.address(),
                    attendees=random.randint(10, 200),
                    notes=fake.text(),
                )
                events.append(event)
                session.add(event)

    session.commit()
    return events


@click.group()
def seed():
    """Commandes de génération de données de test."""
    pass


@seed.command()
def create_all():
    """Génère toutes les données de test."""
    session = get_session()

    try:
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
        session.rollback()
        click.echo(f"Erreur lors de la génération des données: {str(e)}")
    finally:
        session.close()


@seed.command()
def reset_all():
    """Supprime toutes les données de test."""
    session = get_session()
    try:
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
