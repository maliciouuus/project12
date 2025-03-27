"""
Commandes CLI pour la gestion des contrats.

Ce module définit l'interface en ligne de commande pour manipuler les contrats
dans l'application Epic Events. Il utilise le package Click pour la définition
des commandes et des options.
"""

import click
from ..models import Contract, Client, User
from ..database import get_session
from ..event_logging import log_contract_signature, log_error


@click.group()
def contract():
    """
    Commandes de gestion des contrats.

    Ce groupe contient toutes les commandes relatives aux contrats:
    - creation (create)
    - suppression (delete)
    - mise à jour (update)
    - liste et filtrage (list)

    Ces commandes sont accessibles via: python -m epic_events.cli contract [COMMANDE]
    """
    pass


@contract.command()
@click.option("--name", required=True, help="Nom du contrat")
@click.option("--description", help="Description du contrat")
@click.option("--client-id", type=int, required=True, help="ID du client")
@click.option("--total-amount", type=float, required=True, help="Montant total")
@click.option("--is-signed", is_flag=True, help="Le contrat est signé")
@click.option("--is-paid", is_flag=True, help="Le contrat est payé")
@log_contract_signature
def create(name, description, client_id, total_amount, is_signed, is_paid):
    """
    Créer un nouveau contrat.

    Cette commande permet de créer un nouveau contrat en fournissant les informations
    nécessaires. Le contrat est automatiquement lié au client spécifié et au commercial
    associé à ce client. La signature du contrat est journalisée via Sentry si l'option
    --is-signed est activée.

    Exemple:
        python -m epic_events.cli contract create --name "Séminaire 2023" --client-id 1
        --total-amount 5000 --is-signed
    """
    # Récupérer une session de base de données
    session = get_session()

    try:
        # Vérifier que le montant est positif
        # C'est une validation métier importante
        if total_amount <= 0:
            click.echo("Erreur: Le montant total doit être positif.")
            return 1

        # Vérifier que le client existe
        # Si le client n'existe pas, on lève une exception
        client = session.query(Client).filter_by(id=client_id).first()
        if not client:
            raise click.ClickException(f"Client avec ID {client_id} non trouvé")

        # Créer le contrat
        # On associe automatiquement le commercial du client
        contract = Contract(
            name=name,
            description=description,
            client_id=client_id,
            commercial_id=client.commercial_id,  # Associe au commercial du client
            total_amount=total_amount,
            remaining_amount=total_amount,  # Par défaut, montant restant = montant total
            is_signed=is_signed,
            is_paid=is_paid,
        )

        # Ajouter et valider la transaction
        session.add(contract)
        session.commit()

        # Confirmer le succès à l'utilisateur
        click.echo(f"Contrat {contract.name} créé avec succès.")
        return 0
    except Exception as e:
        # Annuler la transaction en cas d'erreur
        session.rollback()

        # Journaliser l'erreur pour diagnostic
        log_error(
            e, {"name": name, "client_id": client_id, "total_amount": total_amount}
        )

        # Remonter l'erreur à l'interface utilisateur
        raise click.ClickException(str(e))
    finally:
        # Toujours fermer la session pour libérer les ressources
        session.close()


@contract.command()
@click.option("--contract-id", type=int, required=True, help="ID du contrat")
def delete(contract_id):
    """
    Supprimer un contrat.

    Cette commande supprime le contrat spécifié par son ID.
    Attention: La suppression d'un contrat entraîne également la suppression
    des événements associés en raison de la cascade de suppression.

    Exemple:
        python -m epic_events.cli contract delete --contract-id 1
    """
    session = get_session()
    contract = session.query(Contract).filter_by(id=contract_id).first()
    if not contract:
        click.echo("Erreur: Contrat non trouvé.")
        session.close()
        return

    try:
        # Supprimer le contrat et ses événements associés (via cascade)
        session.delete(contract)
        session.commit()
        click.echo(f"Contrat {contract.name} supprimé avec succès.")
    except Exception as e:
        session.rollback()
        log_error(e, {"contract_id": contract_id})
        raise click.ClickException(str(e))
    finally:
        session.close()


@contract.command()
@click.option("--contract-id", type=int, required=True, help="ID du contrat")
@click.option("--name", help="Nouveau nom du contrat")
@click.option("--description", help="Nouvelle description")
@click.option("--total-amount", type=float, help="Nouveau montant total")
@click.option("--remaining-amount", type=float, help="Nouveau montant restant")
@click.option("--is-signed", type=bool, help="Statut de signature")
@click.option("--is-paid", type=bool, help="Statut de paiement")
@log_contract_signature
def update(
    contract_id, name, description, total_amount, remaining_amount, is_signed, is_paid
):
    """
    Mettre à jour les informations d'un contrat.

    Cette commande permet de modifier les propriétés d'un contrat existant.
    Seules les propriétés spécifiées dans les options seront modifiées.
    La signature du contrat est journalisée via Sentry si l'option
    --is-signed est modifiée à True.

    Exemple:
        python -m epic_events.cli contract update --contract-id 1 --name "Nouveau nom"
        --is-signed true
    """
    session = get_session()
    contract = session.query(Contract).filter_by(id=contract_id).first()
    if not contract:
        click.echo("Erreur: Contrat non trouvé.")
        session.close()
        return

    # Mise à jour conditionnelle des champs
    # On ne modifie que les champs pour lesquels une valeur a été fournie
    if name:
        contract.name = name
    if description:
        contract.description = description
    if total_amount is not None:
        contract.total_amount = total_amount
    if remaining_amount is not None:
        contract.remaining_amount = remaining_amount
    if is_signed is not None:
        contract.is_signed = is_signed
    if is_paid is not None:
        contract.is_paid = is_paid

    try:
        # Valider les modifications
        session.commit()
        click.echo(f"Contrat {contract.name} mis à jour avec succès.")
    except Exception as e:
        session.rollback()
        log_error(e, {"contract_id": contract_id})
        raise click.ClickException(str(e))
    finally:
        session.close()


@contract.command()
@click.option("--client-id", type=int, help="Filtrer par client")
@click.option("--commercial-id", type=int, help="Filtrer par commercial")
@click.option(
    "--signed-only", is_flag=True, help="Afficher uniquement les contrats signés"
)
@click.option(
    "--unsigned-only", is_flag=True, help="Afficher uniquement les contrats non signés"
)
@click.option(
    "--paid-only", is_flag=True, help="Afficher uniquement les contrats payés"
)
@click.option(
    "--unpaid-only", is_flag=True, help="Afficher uniquement les contrats non payés"
)
def list(client_id, commercial_id, signed_only, unsigned_only, paid_only, unpaid_only):
    """
    Lister tous les contrats avec filtres optionnels.

    Cette commande affiche les contrats en fonction des filtres spécifiés.
    Les filtres peuvent être combinés pour affiner la recherche.
    Par exemple, on peut lister tous les contrats signés mais non payés
    d'un client spécifique.

    Exemples:
        python -m epic_events.cli contract list
        python -m epic_events.cli contract list --client-id 1 --signed-only
        python -m epic_events.cli contract list --commercial-id 2 --unsigned-only
    """
    session = get_session()
    query = session.query(Contract)

    # Application des filtres à la requête
    if client_id:
        query = query.filter_by(client_id=client_id)
    if commercial_id:
        query = query.filter_by(commercial_id=commercial_id)
    if signed_only:
        query = query.filter_by(is_signed=True)
    if unsigned_only:
        query = query.filter_by(is_signed=False)
    if paid_only:
        query = query.filter_by(is_paid=True)
    if unpaid_only:
        query = query.filter_by(is_paid=False)

    # Exécution de la requête
    contracts = query.all()
    if not contracts:
        click.echo("Aucun contrat trouvé.")
        session.close()
        return

    # Affichage des résultats
    for contract in contracts:
        # Récupérer les informations liées pour un affichage complet
        client = session.query(Client).get(contract.client_id)
        commercial = session.query(User).get(contract.commercial_id)

        # Afficher les informations du contrat
        click.echo(f"ID: {contract.id}")
        click.echo(f"Nom: {contract.name}")
        click.echo(f"Client: {client.full_name}")
        click.echo(f"Commercial: {commercial.full_name}")
        click.echo(f"Montant total: {contract.total_amount}€")
        click.echo(f"Montant restant: {contract.remaining_amount}€")
        click.echo(f"Signé: {'Oui' if contract.is_signed else 'Non'}")
        click.echo(f"Payé: {'Oui' if contract.is_paid else 'Non'}")
        click.echo("---")

    session.close()
