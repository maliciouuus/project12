# Epic Events CRM

Un système de gestion de la relation client (CRM) en ligne de commande pour Epic Events.

## Description

Cette application permet de gérer les clients, les contrats et les événements pour Epic Events. Elle est conçue pour être utilisée par trois départements distincts :
- Commercial
- Support
- Gestion

## Fonctionnalités principales

- Gestion des clients
- Gestion des contrats
- Gestion des événements
- Système d'authentification et de droits d'accès
- Journalisation des erreurs avec Sentry

## Installation

1. Cloner le repository :
```bash
git clone [url-du-repo]
cd epic-events
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# ou
.\venv\Scripts\activate  # Sur Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Copier le fichier .env.example en .env et configurer les variables d'environnement :
```bash
cp .env.example .env
```

## Configuration

Le fichier `.env` doit contenir les variables suivantes :
- `DATABASE_URL`: URL de connexion à la base de données
- `SECRET_KEY`: Clé secrète pour la sécurité
- `SENTRY_DSN`: DSN pour la connexion à Sentry

## Utilisation

[Documentation à venir sur les commandes disponibles]

## Structure du projet

```
epic_events/
├── models/         # Modèles de données
├── controllers/    # Logique métier
├── views/         # Interface utilisateur CLI
├── utils/         # Utilitaires et helpers
└── tests/         # Tests unitaires et d'intégration
```

## Tests

Pour exécuter les tests :
```bash
pytest
```

## Contribution

[Instructions pour contribuer au projet]

## Licence

[Information sur la licence]
