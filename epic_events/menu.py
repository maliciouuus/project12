"""
Menu interactif pour Epic Events CRM.
"""

import os
import click
import subprocess
from .auth import get_current_user, login, logout
from .models import UserRole
import sys


def clear_screen():
    """Nettoie l'écran"""
    os.system("cls" if os.name == "nt" else "clear")


def run_command(command):
    """Lance une commande CLI"""
    try:
        cmd = f"python -m epic_events.cli {command}"
        subprocess.run(cmd, shell=True)
    except Exception as e:
        click.echo(f"Erreur: {str(e)}")


def print_header():
    """Affiche l'en-tête du menu"""
    clear_screen()
    click.echo("=" * 60)
    click.echo("               EPIC EVENTS CRM - MENU")
    click.echo("=" * 60)
    user = get_current_user()
    if user:
        click.echo(f"Utilisateur: {user.full_name} ({user.role})")
    else:
        click.echo("Non connecté")
    click.echo("-" * 60)


def login_menu():
    """Menu de connexion"""
    print_header()
    click.echo("CONNEXION")
    click.echo("-" * 60)

    username = click.prompt("Nom d'utilisateur")
    password = click.prompt("Mot de passe", hide_input=True)

    try:
        login(username, password)
        click.pause("Appuyez sur une touche pour continuer...")
    except Exception as e:
        click.echo(f"Erreur: {str(e)}")
        click.pause("Appuyez sur une touche pour continuer...")


def user_menu():
    """Menu utilisateurs"""
    while True:
        print_header()
        click.echo("MENU UTILISATEURS")
        click.echo("-" * 60)
        click.echo("1. Créer un utilisateur")
        click.echo("2. Lister les utilisateurs")
        click.echo("3. Modifier un utilisateur")
        click.echo("4. Supprimer un utilisateur")
        click.echo("0. Retour")
        click.echo("-" * 60)

        choice = click.prompt("Votre choix", type=int)

        if choice == 0:
            break
        elif choice == 1:
            username = click.prompt("Nom d'utilisateur")
            email = click.prompt("Email")
            password = click.prompt("Mot de passe", hide_input=True)
            first_name = click.prompt("Prénom")
            last_name = click.prompt("Nom")
            role = click.prompt(
                "Rôle",
                type=click.Choice(
                    [
                        UserRole.ADMIN,
                        UserRole.COMMERCIAL,
                        UserRole.SUPPORT,
                        UserRole.GESTION,
                    ]
                ),
            )

            cmd = (
                f"user create --username '{username}' --email '{email}' "
                f"--password '{password}' --first-name '{first_name}' "
                f"--last-name '{last_name}' --role '{role}'"
            )

            run_command(cmd)
        elif choice == 2:
            run_command("user list")
        elif choice == 3:
            user_id = click.prompt("ID de l'utilisateur", type=int)
            click.echo("Laissez vide si pas de changement")
            username = click.prompt("Nouveau nom", default="", show_default=False)
            email = click.prompt("Nouvel email", default="", show_default=False)
            texte_first = "Nouveau mot de passe"
            password = click.prompt(texte_first, default="", show_default=False, hide_input=True)
            first_name = click.prompt("Nouveau prénom", default="", show_default=False)
            last_name = click.prompt("Nouveau nom", default="", show_default=False)

            cmd = f"user update --user-id {user_id}"
            if username:
                cmd += f" --username '{username}'"
            if email:
                cmd += f" --email '{email}'"
            if password:
                cmd += f" --password '{password}'"
            if first_name:
                cmd += f" --first-name '{first_name}'"
            if last_name:
                cmd += f" --last-name '{last_name}'"

            run_command(cmd)
        elif choice == 4:
            user_id = click.prompt("ID de l'utilisateur", type=int)
            if click.confirm(f"Supprimer l'utilisateur {user_id}?"):
                run_command(f"user delete --user-id {user_id}")
        else:
            click.echo("Choix invalide.")

        click.pause("Appuyez sur une touche pour continuer...")


def client_menu():
    """Menu clients"""
    while True:
        print_header()
        click.echo("MENU CLIENTS")
        click.echo("-" * 60)
        click.echo("1. Créer un client")
        click.echo("2. Lister les clients")
        click.echo("3. Modifier un client")
        click.echo("4. Supprimer un client")
        click.echo("0. Retour")
        click.echo("-" * 60)

        choice = click.prompt("Votre choix", type=int)

        if choice == 0:
            break
        elif choice == 1:
            first_name = click.prompt("Prénom")
            last_name = click.prompt("Nom")
            email = click.prompt("Email")
            phone = click.prompt("Téléphone")
            company = click.prompt("Entreprise", default="", show_default=False)
            commercial_id = click.prompt("ID commercial", type=int)

            cmd = (
                f"client create --first-name '{first_name}' "
                f"--last-name '{last_name}' --email '{email}' "
                f"--phone '{phone}' --commercial-id {commercial_id}"
            )
            if company:
                cmd += f" --company '{company}'"

            run_command(cmd)
        elif choice == 2:
            user = get_current_user()
            if user and user.is_commercial():
                if click.confirm("Voir seulement vos clients?"):
                    run_command(f"client list --commercial-id {user.id}")
                    continue
            run_command("client list")
        elif choice == 3:
            client_id = click.prompt("ID du client", type=int)
            click.echo("Laissez vide si pas de changement")
            first_name = click.prompt("Nouveau prénom", default="", show_default=False)
            last_name = click.prompt("Nouveau nom", default="", show_default=False)
            email = click.prompt("Nouvel email", default="", show_default=False)
            phone = click.prompt("Nouveau téléphone", default="", show_default=False)
            company = click.prompt("Nouvelle entreprise", default="", show_default=False)

            cmd = f"client update --client-id {client_id}"
            if first_name:
                cmd += f" --first-name '{first_name}'"
            if last_name:
                cmd += f" --last-name '{last_name}'"
            if email:
                cmd += f" --email '{email}'"
            if phone:
                cmd += f" --phone '{phone}'"
            if company:
                cmd += f" --company '{company}'"

            run_command(cmd)
        elif choice == 4:
            client_id = click.prompt("ID du client", type=int)
            if click.confirm(f"Supprimer le client {client_id}?"):
                run_command(f"client delete --client-id {client_id}")
        else:
            click.echo("Choix invalide.")

        click.pause("Appuyez sur une touche pour continuer...")


def contract_menu():
    """Menu contrats"""
    while True:
        print_header()
        click.echo("MENU CONTRATS")
        click.echo("-" * 60)
        click.echo("1. Créer un contrat")
        click.echo("2. Lister les contrats")
        click.echo("3. Modifier un contrat")
        click.echo("4. Supprimer un contrat")
        click.echo("0. Retour")
        click.echo("-" * 60)

        choice = click.prompt("Votre choix", type=int)

        if choice == 0:
            break
        elif choice == 1:
            name = click.prompt("Nom du contrat")
            description = click.prompt("Description", default="", show_default=False)
            client_id = click.prompt("ID du client", type=int)
            total_amount = click.prompt("Montant total", type=float)
            is_signed = click.confirm("Contrat signé?")
            is_paid = click.confirm("Contrat payé?")

            cmd = (
                f"contract create --name '{name}' --client-id {client_id} "
                f"--total-amount {total_amount}"
            )
            if description:
                cmd += f" --description '{description}'"
            if is_signed:
                cmd += " --is-signed"
            if is_paid:
                cmd += " --is-paid"

            run_command(cmd)
        elif choice == 2:
            print_header()
            click.echo("FILTRES CONTRATS")
            click.echo("-" * 60)
            click.echo("1. Tous les contrats")
            click.echo("2. Par client")
            click.echo("3. Par commercial")
            click.echo("4. Contrats signés")
            click.echo("5. Contrats non signés")
            click.echo("6. Contrats payés")
            click.echo("7. Contrats non payés")
            click.echo("-" * 60)

            filter_choice = click.prompt("Votre choix", type=int)

            if filter_choice == 1:
                run_command("contract list")
            elif filter_choice == 2:
                client_id = click.prompt("ID client", type=int)
                run_command(f"contract list --client-id {client_id}")
            elif filter_choice == 3:
                commercial_id = click.prompt("ID commercial", type=int)
                run_command(f"contract list --commercial-id {commercial_id}")
            elif filter_choice == 4:
                run_command("contract list --signed-only")
            elif filter_choice == 5:
                run_command("contract list --unsigned-only")
            elif filter_choice == 6:
                run_command("contract list --paid-only")
            elif filter_choice == 7:
                run_command("contract list --unpaid-only")
            else:
                click.echo("Choix invalide.")
        elif choice == 3:
            update_contract()
        elif choice == 4:
            contract_id = click.prompt("ID du contrat", type=int)
            if click.confirm(f"Supprimer le contrat {contract_id}?"):
                run_command(f"contract delete --contract-id {contract_id}")
        else:
            click.echo("Choix invalide.")

        click.pause("Appuyez sur une touche pour continuer...")


def event_menu():
    """Menu événements"""
    while True:
        print_header()
        click.echo("MENU ÉVÉNEMENTS")
        click.echo("-" * 60)
        click.echo("1. Créer un événement")
        click.echo("2. Lister les événements")
        click.echo("3. Assigner un support")
        click.echo("4. Modifier un événement")
        click.echo("0. Retour")
        click.echo("-" * 60)

        choice = click.prompt("Votre choix", type=int)

        if choice == 0:
            break
        elif choice == 1:
            name = click.prompt("Nom de l'événement")
            contract_id = click.prompt("ID du contrat", type=int)
            start_date = click.prompt("Date début (YYYY-MM-DD HH:MM)")
            end_date = click.prompt("Date fin (YYYY-MM-DD HH:MM)")
            location = click.prompt("Lieu")
            attendees = click.prompt("Nombre participants", type=int)
            notes = click.prompt("Notes", default="", show_default=False)

            cmd = (
                f"event create --name '{name}' --contract-id {contract_id} "
                f"--start-date '{start_date}' --end-date '{end_date}' "
                f"--location '{location}' --attendees {attendees}"
            )
            if notes:
                cmd += f" --notes '{notes}'"

            run_command(cmd)
        elif choice == 2:
            list_events()
        elif choice == 3:
            event_id = click.prompt("ID événement", type=int)
            support_id = click.prompt("ID support", type=int)
            run_command(
                f"event assign_support --event-id {event_id} --support-id {support_id}"
            )
        elif choice == 4:
            update_event()
        else:
            click.echo("Choix invalide.")

        click.pause("Appuyez sur une touche pour continuer...")


def main_menu():
    """Menu principal"""
    while True:
        print_header()

        user = get_current_user()

        if user:
            click.echo("MENU PRINCIPAL")
            click.echo("-" * 60)
            click.echo("1. Gestion utilisateurs")
            click.echo("2. Gestion clients")
            click.echo("3. Gestion contrats")
            click.echo("4. Gestion événements")
            click.echo("5. Se déconnecter")
            click.echo("0. Quitter")
            click.echo("-" * 60)

            choice = click.prompt("Votre choix", type=int)

            if choice == 0:
                if click.confirm("Vraiment quitter?"):
                    break
            elif choice == 1:
                if user.is_admin() or user.has_role(UserRole.GESTION):
                    user_menu()
                else:
                    click.echo("Vous n'avez pas les permissions nécessaires.")
                    click.pause("Appuyez sur une touche pour continuer...")
            elif choice == 2:
                client_menu()
            elif choice == 3:
                contract_menu()
            elif choice == 4:
                event_menu()
            elif choice == 5:
                logout()
            else:
                click.echo("Choix invalide.")
                click.pause("Appuyez sur une touche pour continuer...")
        else:
            click.echo("BIENVENUE SUR EPIC EVENTS CRM")
            click.echo("-" * 60)
            click.echo("1. Se connecter")
            click.echo("0. Quitter")
            click.echo("-" * 60)

            choice = click.prompt("Votre choix", type=int)

            if choice == 0:
                if click.confirm("Vraiment quitter?"):
                    break
            elif choice == 1:
                login_menu()
            else:
                click.echo("Choix invalide.")
                click.pause("Appuyez sur une touche pour continuer...")


def start_menu():
    """Démarrage du menu"""
    try:
        main_menu()
    except KeyboardInterrupt:
        click.echo("\nAu revoir!")
    finally:
        clear_screen()


def update_contract():
    """Mise à jour d'un contrat"""
    print("\n=== Modifier un contrat ===\n")
    contract_id = click.prompt("ID du contrat", type=int)
    field = click.prompt(
        "Champ à modifier",
        type=click.Choice(
            ["description", "total_amount", "is_signed", "is_paid", "remaining_amount"]
        ),
    )
    value = click.prompt("Nouvelle valeur")

    if field in ["is_signed", "is_paid"]:
        value = value.lower() == "true"
    elif field in ["total_amount", "remaining_amount"]:
        value = float(value)

    cmd = f"contract update {contract_id} --{field.replace('_', '-')} {value}"
    run_command(cmd)


def list_events():
    """Liste des événements"""
    print("\n=== Liste des événements ===\n")
    status = click.prompt(
        "Statut",
        type=click.Choice(["all", "future", "ongoing", "past"]),
        default="all",
        show_default=True,
    )

    cmd = "event list"
    if status != "all":
        cmd += f" --status {status}"

    run_command(cmd)


def update_event():
    """Mise à jour d'un événement"""
    print("\n=== Modifier un événement ===\n")
    event_id = click.prompt("ID de l'événement", type=int)
    field = click.prompt(
        "Champ à modifier",
        type=click.Choice(
            [
                "name",
                "start_date",
                "end_date",
                "location",
                "attendees",
                "notes",
                "support_id",
            ]
        ),
    )
    value = click.prompt("Nouvelle valeur")

    cmd = f"event update {event_id} --{field.replace('_', '-')} {value}"
    run_command(cmd)


def handle_management_menu():
    """Menu de gestion"""
    while True:
        print_header()
        print("\n=== MENU GESTION ===\n")
        print("1. Gérer utilisateurs")
        print("2. Voir statistiques")
        print("3. Retour au menu")
        print("4. Quitter\n")

        choice = click.prompt("Votre choix", type=int, default=3, show_default=True)

        if choice == 1:
            user_menu()
        elif choice == 2:
            click.echo("Fonction statistiques pas encore disponible.")
        elif choice == 3:
            return
        elif choice == 4:
            print("Au revoir!")
            sys.exit(0)
        else:
            print("Vous n'avez pas les permissions pour faire ça.")
