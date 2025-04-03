# Epic Events CRM

Application de gestion CRM pour l'entreprise Epic Events, spécialisée dans l'organisation d'événements d'entreprise.

## Description

Epic Events CRM est une application complète qui permet la gestion des clients, contrats et événements pour une entreprise d'organisation d'événements. Elle propose une interface en ligne de commande (CLI) ainsi qu'une interface interactive sous forme de menu. L'application prend en charge différents rôles utilisateurs (administrateur, commercial, support, gestion) avec des permissions spécifiques.

## Fonctionnalités

- **Interface interactive** : Menu convivial pour naviguer facilement entre les fonctionnalités
- **Gestion des utilisateurs** : Création, modification, suppression et liste des utilisateurs avec différents rôles
- **Gestion des clients** : Suivi des informations clients et association avec un commercial
- **Gestion des contrats** : Suivi des contrats, avec statut (signé, payé) et montants
- **Gestion des événements** : Organisation des prestations avec dates, lieux et assignation à l'équipe support
- **Authentification** : Système de connexion sécurisé avec gestion des sessions
- **Autorisations** : Contrôle d'accès basé sur les rôles et les permissions spécifiques
- **Journalisation** : Intégration avec Sentry pour le suivi des actions utilisateurs, signatures de contrats et erreurs
- **Sécurité** : Hachage des mots de passe et gestion fine des permissions

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Bash (pour le script d'installation)

## Installation

Utilisez le script d'installation fourni :

```bash
./setup.sh
```

Et sélectionnez l'option "1) Installer l'application".

Ce script va :
1. Créer un environnement virtuel Python
2. Installer les dépendances requises
3. Initialiser la base de données
4. Créer un utilisateur administrateur par défaut

Pour configurer Sentry, vous devez configurer le fichier `.env` :
1. Si le fichier n'existe pas, copiez `.env.example` en `.env`
2. Modifiez la variable `SENTRY_DSN` avec votre DSN Sentry

## Utilisation

### Menu Interactif (Recommandé)

Pour lancer l'interface interactive :

```bash
./setup.sh
```

Et sélectionnez l'option "2) Lancer le menu interactif".

Ou directement avec la commande :

```bash
python -m epic_events.cli menu
```

### Interface en Ligne de Commande

Vous pouvez également utiliser l'application via sa CLI traditionnelle :

```bash
python -m epic_events.cli [COMMANDE]
```

#### Commandes principales

- `user` : Gestion des utilisateurs
- `client` : Gestion des clients
- `contract` : Gestion des contrats
- `event` : Gestion des événements
- `seed` : Génération de données de test
- `menu` : Lancer l'interface interactive
- `init` : Initialiser la base de données
- `test` : Exécuter les tests

#### Exemples d'utilisation CLI

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
├── auth.py            # Système d'authentification
├── database.py        # Configuration de la base de données
├── event_logging.py   # Intégration avec Sentry
├── menu.py            # Interface utilisateur interactive
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

Le projet comprend une suite complète de tests unitaires et d'intégration couvrant :
- Modèles de données
- Authentification
- Menu interactif
- Flux de travail complets

Pour exécuter les tests :

```bash
./setup.sh
```

Et sélectionnez l'option "3) Exécuter les tests (pytest)".

Ce processus vous offre plusieurs options :
- Exécuter tous les tests
- Exécuter les tests avec affichage détaillé
- Exécuter les tests avec rapport de couverture
- Exécuter un fichier de test spécifique

Par défaut, Sentry est activé pendant les tests mais ses messages ne sont pas affichés dans le terminal. Vous pouvez configurer le comportement de Sentry dans le fichier `.env` :

```bash
# Modifier les variables dans .env
# SENTRY_ENABLED=false  # Pour désactiver complètement Sentry
# SENTRY_DEBUG=true     # Pour afficher les messages Sentry dans le terminal
```

## Configuration de Sentry

Pour la journalisation avec Sentry :

1. Copiez le fichier `.env.example` vers `.env` s'il n'existe pas déjà
   ```bash
   cp .env.example .env
   ```
2. Modifiez la variable `SENTRY_DSN` dans le fichier `.env` avec votre DSN Sentry
3. Configurez les options supplémentaires selon vos besoins :
   ```
   SENTRY_ENABLED=true       # Activer/désactiver Sentry
   SENTRY_DEBUG=false        # Afficher les messages de debug Sentry
   SENTRY_SEND_PII=false     # Envoyer les informations personnelles identifiables
   ENVIRONMENT=development   # Environnement (development, test, production)
   ```

Pour vérifier que Sentry fonctionne correctement, lancez une commande qui effectue une action journalisée, ou connectez-vous via le menu interactif.

## Maintenance

Le script `setup.sh` offre plusieurs options pour gérer l'application :

```bash
./setup.sh
```

Options disponibles :
- "1) Installer l'application" : Installation complète avec initialisation
- "2) Lancer le menu interactif" : Démarrer l'interface utilisateur
- "3) Exécuter les tests (pytest)" : Lancer la suite de tests
- "4) Générer un rapport HTML avec flake8" : Analyser la qualité du code
- "5) Nettoyer l'installation" : Supprimer l'environnement et les fichiers générés
- "6) Quitter" : Sortir du script

### Rapport de qualité de code

L'application intègre des outils de qualité de code :

1. **Black** : Formateur de code automatique
2. **Flake8** : Linter pour les conventions PEP 8
3. **Rapport HTML** : Visualisation des problèmes de style de code

Pour générer un rapport HTML :
```bash
./setup.sh
```
Puis sélectionnez l'option "4) Générer un rapport HTML avec flake8".

## Authentification et Sécurité

### Utilisateur par défaut
Après l'installation, vous pouvez vous connecter avec l'utilisateur administrateur par défaut :
- Nom d'utilisateur : `admin`
- Mot de passe : `admin123`

Il est recommandé de changer ce mot de passe dès la première utilisation en production.

### Rôles utilisateurs
Le système gère quatre rôles distincts :
- **Admin** : Accès complet à toutes les fonctionnalités
- **Commercial** : Gestion des clients et contrats associés
- **Support** : Gestion des événements assignés
- **Gestion** : Supervision globale sans droits d'administration

## Auteur

[Votre nom]

## Licence

[Votre licence] 