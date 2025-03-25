# Epic Events CRM

Application de gestion CRM pour l'entreprise Epic Events, spécialisée dans l'organisation d'événements d'entreprise.

## Description

Epic Events CRM est une application en ligne de commande (CLI) qui permet la gestion complète des clients, contrats et événements pour une entreprise d'organisation d'événements. Elle prend en charge différents rôles utilisateurs (administrateur, commercial, support, gestion) avec des permissions spécifiques.

## Fonctionnalités

- **Gestion des utilisateurs** : Création, modification, suppression et liste des utilisateurs avec différents rôles
- **Gestion des clients** : Suivi des informations clients et association avec un commercial
- **Gestion des contrats** : Suivi des contrats, avec statut (signé, payé) et montants
- **Gestion des événements** : Organisation des prestations avec dates, lieux et assignation à l'équipe support
- **Journalisation** : Intégration avec Sentry pour le suivi des actions utilisateurs, signatures de contrats et erreurs
- **Sécurité** : Hachage des mots de passe et gestion des permissions par rôle

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Bash (pour les scripts d'installation et de test)

## Installation

Utilisez le script d'installation fourni :

```bash
./setup.sh
```

Et sélectionnez l'option "1) Installer l'application".

Ce script va :
1. Créer un environnement virtuel Python
2. Installer les dépendances requises
3. Configurer Sentry (optionnel)
4. Initialiser la base de données
5. Créer un utilisateur administrateur par défaut

## Utilisation

Après installation, vous pouvez utiliser l'application via sa CLI :

```bash
# Avec l'environnement virtuel activé
python -m epic_events.cli [COMMANDE]
```

### Commandes principales

- `user` : Gestion des utilisateurs
- `client` : Gestion des clients
- `contract` : Gestion des contrats
- `event` : Gestion des événements
- `seed` : Génération de données de test

### Exemples d'utilisation

```bash
# Créer un utilisateur
python -m epic_events.cli user create --username "john_doe" --email "john@example.com" --password "secure_password" --first-name "John" --last-name "Doe" --role "commercial"

# Lister les clients d'un commercial
python -m epic_events.cli client list --commercial-id 1

# Créer un contrat
python -m epic_events.cli contract create --name "Séminaire annuel" --client-id 1 --total-amount 5000 --is-signed

# Lister les événements assignés à un support
python -m epic_events.cli event list --support-id 2
```

## Structure du projet

```
epic_events/
├── __init__.py        # Initialisation du package
├── cli.py             # Point d'entrée de la CLI
├── database.py        # Configuration de la base de données
├── event_logging.py   # Intégration avec Sentry
├── commands/          # Commandes CLI
│   ├── __init__.py
│   ├── client_commands.py
│   ├── contract_commands.py
│   ├── event_commands.py
│   ├── seed_commands.py
│   └── user_commands.py
└── models/            # Modèles de données
    ├── __init__.py
    ├── client.py
    ├── contract.py
    ├── event.py
    └── user.py
```

## Tests

Pour exécuter les tests automatisés :

```bash
./test_epic_events.sh
```

Ce script va :
1. Nettoyer l'environnement de test
2. Initialiser une base de données de test
3. Tester les fonctionnalités de base (utilisateurs, clients, contrats, événements)
4. Générer un rapport des tests

## Configuration de Sentry

Pour la journalisation avec Sentry :

1. Copiez le fichier `.env.example` vers `.env`
2. Modifiez la variable `SENTRY_DSN` avec votre DSN Sentry
3. Configurez `SENTRY_SEND_PII` selon vos besoins de confidentialité

Vous pouvez également utiliser l'option "4) Configurer Sentry" du script `setup.sh`.

## Maintenance

Pour nettoyer l'installation ou formater le code :

```bash
./setup.sh
```

Et sélectionnez l'option appropriée :
- "2) Nettoyer l'installation" : Supprime l'environnement virtuel, la base de données et les fichiers cache
- "3) Formater le code" : Utilise Black et Flake8 pour formater et vérifier le code source

## Auteur

[Votre nom]

## Licence

[Votre licence] 