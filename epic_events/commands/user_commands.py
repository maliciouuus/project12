"""
Commandes CLI pour la gestion des utilisateurs.
"""

import click
from sqlalchemy.exc import IntegrityError
from ..models import User, UserRole
from ..database import get_session
from ..event_logging import log_user_action, log_error


@click.group()
def user():
    """Commandes de gestion des utilisateurs."""
    pass


@user.command()
@click.option("--username", required=True, help="Nom d'utilisateur")
@click.option("--email", required=True, help="Adresse email")
@click.option("--password", required=True, help="Mot de passe")
@click.option("--first-name", required=True, help="Prénom")
@click.option("--last-name", required=True, help="Nom")
@click.option(
    "--role",
    type=click.Choice([r[0] for r in UserRole.choices()]),
    required=True,
    help="Rôle de l'utilisateur",
)
@log_user_action("create_user")
def create(username, email, password, first_name, last_name, role):
    """Créer un nouvel utilisateur."""
    session = get_session()

    try:
        # Vérifier si le nom d'utilisateur existe déjà
        if session.query(User).filter_by(username=username).first():
            raise click.ClickException(f"L'utilisateur {username} existe déjà")

        # Vérifier si l'email existe déjà
        if session.query(User).filter_by(email=email).first():
            raise click.ClickException(f"Cette adresse email {email} existe déjà")

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        user.set_password(password)

        session.add(user)
        session.commit()
        click.echo(f"Utilisateur {user.username} créé avec succès.")
        return 0
    except IntegrityError:
        session.rollback()
        log_error(
            "Erreur: Un utilisateur avec ce nom d'utilisateur ou cet email existe déjà.",
            {"username": username, "email": email},
        )
        raise click.ClickException(
            "Erreur: Un utilisateur avec ce nom d'utilisateur ou cet email existe déjà."
        )
    except Exception as e:
        session.rollback()
        log_error(e, {"username": username, "email": email, "role": role})
        raise click.ClickException(
            f"Erreur lors de la création de l'utilisateur: {str(e)}"
        )
    finally:
        session.close()


@user.command()
@click.option("--user-id", type=int, required=True, help="ID de l'utilisateur")
@click.option("--username", help="Nouveau nom d'utilisateur")
@click.option("--email", help="Nouvelle adresse email")
@click.option("--password", help="Nouveau mot de passe")
@click.option("--first-name", help="Nouveau prénom")
@click.option("--last-name", help="Nouveau nom")
@click.option(
    "--role",
    type=click.Choice([r[0] for r in UserRole.choices()]),
    help="Nouveau rôle",
)
@log_user_action("update_user")
def update(user_id, username, email, password, first_name, last_name, role):
    """Mettre à jour un utilisateur."""
    session = get_session()

    try:
        user = session.query(User).get(user_id)
        if not user:
            raise click.ClickException(f"Utilisateur avec ID {user_id} non trouvé")

        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            user.set_password(password)
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if role:
            user.role = role

        session.commit()
        click.echo(f"Utilisateur {user.username} mis à jour avec succès.")
    except Exception as e:
        session.rollback()
        log_error(e, {"user_id": user_id})
        raise click.ClickException(
            f"Erreur lors de la mise à jour de l'utilisateur: {str(e)}"
        )
    finally:
        session.close()


@user.command()
@click.option("--user-id", type=int, required=True, help="ID de l'utilisateur")
@log_user_action("delete_user")
def delete(user_id):
    """Supprimer un utilisateur."""
    session = get_session()

    try:
        user = session.query(User).get(user_id)
        if not user:
            raise click.ClickException(f"Utilisateur avec ID {user_id} non trouvé")

        session.delete(user)
        session.commit()
        click.echo(f"Utilisateur {user.username} supprimé avec succès.")
    except Exception as e:
        session.rollback()
        log_error(e, {"user_id": user_id})
        raise click.ClickException(
            f"Erreur lors de la suppression de l'utilisateur: {str(e)}"
        )
    finally:
        session.close()


@user.command()
@click.option(
    "--role",
    type=click.Choice([r[0] for r in UserRole.choices()]),
    help="Filtrer par rôle",
)
def list(role):
    """Lister les utilisateurs."""
    session = get_session()
    query = session.query(User)

    if role:
        query = query.filter_by(role=role)

    users = query.all()
    if not users:
        click.echo("Aucun utilisateur trouvé.")
        session.close()
        return

    for user in users:
        click.echo(f"ID: {user.id}")
        click.echo(f"Username: {user.username}")
        click.echo(f"Email: {user.email}")
        click.echo(f"Nom complet: {user.full_name}")
        click.echo(f"Rôle: {user.role}")
        click.echo("---")

    session.close()
