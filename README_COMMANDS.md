# Epic Events - Exemples de commandes pour test

Ce document fournit des exemples concrets de commandes pour tester l'application Epic Events CRM. Les commandes sont organisées par catégorie et peuvent être exécutées directement dans un terminal.

## Préparation de l'environnement

Activez d'abord l'environnement virtuel :

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier que l'environnement est activé
which python3
```

## Commandes utilisateurs

### Créer différents types d'utilisateurs

```bash
# Créer un utilisateur commercial
python3 -m epic_events.cli user create \
    --username "commercial_test1" \
    --email "commercial_test1@epic-events.fr" \
    --password "password123" \
    --first-name "Jean" \
    --last-name "Dupont" \
    --role "commercial"

# Créer un utilisateur support
python3 -m epic_events.cli user create \
    --username "support_test1" \
    --email "support_test1@epic-events.fr" \
    --password "password123" \
    --first-name "Marie" \
    --last-name "Martin" \
    --role "support"

# Créer un utilisateur gestion
python3 -m epic_events.cli user create \
    --username "gestion_test1" \
    --email "gestion_test1@epic-events.fr" \
    --password "password123" \
    --first-name "Pierre" \
    --last-name "Dubois" \
    --role "gestion"
```

### Lister et filtrer les utilisateurs

```bash
# Lister tous les utilisateurs
python3 -m epic_events.cli user list

# Lister seulement les utilisateurs commerciaux
python3 -m epic_events.cli user list --role "commercial"

# Lister seulement les utilisateurs support
python3 -m epic_events.cli user list --role "support"
```

### Mettre à jour et supprimer des utilisateurs

```bash
# Mettre à jour un utilisateur (remplacez 2 par l'ID réel)
python3 -m epic_events.cli user update \
    --user-id 2 \
    --first-name "Nouveau" \
    --last-name "Nom" \
    --email "nouvelle_adresse@epic-events.fr"

# Changer le mot de passe d'un utilisateur
python3 -m epic_events.cli user update \
    --user-id 2 \
    --password "nouveau_mot_de_passe"

# Supprimer un utilisateur (remplacez 3 par l'ID réel)
python3 -m epic_events.cli user delete --user-id 3
```

## Commandes clients

### Créer un client

```bash
# Créer un client (remplacez 2 par l'ID d'un commercial existant)
python3 -m epic_events.cli client create \
    --first-name "Client" \
    --last-name "Important" \
    --email "client.important@company.com" \
    --phone "+33612345678" \
    --company "Entreprise XYZ" \
    --commercial-id 2
```

### Lister et filtrer les clients

```bash
# Lister tous les clients
python3 -m epic_events.cli client list

# Lister les clients d'un commercial spécifique (remplacez 2 par l'ID réel)
python3 -m epic_events.cli client list --commercial-id 2
```

### Mettre à jour et supprimer des clients

```bash
# Mettre à jour un client (remplacez 1 par l'ID réel)
python3 -m epic_events.cli client update \
    --client-id 1 \
    --company "Nouvelle Entreprise SA" \
    --phone "+33698765432"

# Supprimer un client (remplacez 1 par l'ID réel)
python3 -m epic_events.cli client delete --client-id 1
```

## Commandes contrats

### Créer un contrat

```bash
# Créer un contrat non signé (remplacez 1 par l'ID d'un client existant)
python3 -m epic_events.cli contract create \
    --name "Séminaire annuel 2023" \
    --description "Organisation du séminaire annuel" \
    --client-id 1 \
    --total-amount 15000

# Créer un contrat signé
python3 -m epic_events.cli contract create \
    --name "Formation équipe marketing" \
    --description "Deux jours de formation pour l'équipe marketing" \
    --client-id 1 \
    --total-amount 8500 \
    --is-signed

# Créer un contrat signé et payé
python3 -m epic_events.cli contract create \
    --name "Cocktail de fin d'année" \
    --description "Organisation du cocktail annuel" \
    --client-id 1 \
    --total-amount 3200 \
    --is-signed \
    --is-paid
```

### Lister et filtrer les contrats

```bash
# Lister tous les contrats
python3 -m epic_events.cli contract list

# Lister les contrats d'un client spécifique (remplacez 1 par l'ID réel)
python3 -m epic_events.cli contract list --client-id 1

# Lister les contrats gérés par un commercial (remplacez 2 par l'ID réel)
python3 -m epic_events.cli contract list --commercial-id 2

# Lister seulement les contrats signés
python3 -m epic_events.cli contract list --signed-only

# Lister seulement les contrats non signés
python3 -m epic_events.cli contract list --unsigned-only

# Lister seulement les contrats payés
python3 -m epic_events.cli contract list --paid-only
```

### Mettre à jour un contrat

```bash
# Mettre à jour un contrat (remplacez 1 par l'ID réel)
python3 -m epic_events.cli contract update \
    --contract-id 1 \
    --name "Nouveau nom de contrat" \
    --total-amount 12000

# Marquer un contrat comme signé
python3 -m epic_events.cli contract update \
    --contract-id 1 \
    --is-signed true

# Marquer un contrat comme payé
python3 -m epic_events.cli contract update \
    --contract-id 1 \
    --is-paid true
```

## Commandes événements

### Créer un événement

```bash
# Créer un événement (remplacez 1 par l'ID d'un contrat signé existant)
python3 -m epic_events.cli event create \
    --name "Conférence Tech 2023" \
    --contract-id 1 \
    --start-date "2023-10-15 09:00" \
    --end-date "2023-10-15 18:00" \
    --location "Palais des Congrès, Paris" \
    --attendees 150 \
    --notes "Inclut pauses café et déjeuner"
```

### Assigner un support à un événement

```bash
# Assigner un support à un événement 
# (remplacez 1 par l'ID d'un événement et 3 par l'ID d'un utilisateur support)
python3 -m epic_events.cli event assign_support \
    --event-id 1 \
    --support-id 3
```

### Lister et filtrer les événements

```bash
# Lister tous les événements
python3 -m epic_events.cli event list

# Lister les événements à venir
python3 -m epic_events.cli event list --upcoming

# Lister les événements sans support assigné
python3 -m epic_events.cli event list --unassigned

# Lister les événements gérés par un support spécifique (remplacez 3 par l'ID réel)
python3 -m epic_events.cli event list --support-id 3
```

### Mettre à jour un événement

```bash
# Mettre à jour un événement (remplacez 1 par l'ID réel)
python3 -m epic_events.cli event update \
    --event-id 1 \
    --name "Nouveau nom d'événement" \
    --location "Nouvelle localisation" \
    --attendees 200
```

## Génération de données de test

### Générer des données complètes pour les tests

```bash
# Créer un ensemble complet de données de test (utilisateurs, clients, contrats, événements)
python3 -m epic_events.cli seed create_all

# Supprimer toutes les données de test (sauf l'utilisateur admin)
python3 -m epic_events.cli seed reset_all
```

## Script de test automatisé

Pour exécuter les tests automatisés :

```bash
# Exécuter les tests avec Sentry activé (logs supprimés)
./test_epic_events.sh

# Exécuter les tests avec Sentry désactivé
./test_epic_events.sh --disable-sentry

# Exécuter les tests avec Sentry activé et afficher les logs
./test_epic_events.sh --show-sentry
```

---

## Workflow complet d'exemple

Voici un workflow complet pour tester toutes les fonctionnalités :

```bash
# 1. Créer un commercial
COMMERCIAL_ID=$(python3 -m epic_events.cli user create \
    --username "commercial_test" \
    --email "commercial_test@epic-events.fr" \
    --password "password123" \
    --first-name "Jean" \
    --last-name "Commercial" \
    --role "commercial" | grep -oP 'ID: \K\d+')
echo "Commercial créé avec ID: $COMMERCIAL_ID"

# 2. Créer un support
SUPPORT_ID=$(python3 -m epic_events.cli user create \
    --username "support_test" \
    --email "support_test@epic-events.fr" \
    --password "password123" \
    --first-name "Sophie" \
    --last-name "Support" \
    --role "support" | grep -oP 'ID: \K\d+')
echo "Support créé avec ID: $SUPPORT_ID"

# 3. Créer un client
CLIENT_ID=$(python3 -m epic_events.cli client create \
    --first-name "Client" \
    --last-name "Test" \
    --email "client.test@company.com" \
    --phone "+33612345678" \
    --company "Company Test" \
    --commercial-id $COMMERCIAL_ID | grep -oP 'ID: \K\d+')
echo "Client créé avec ID: $CLIENT_ID"

# 4. Créer un contrat
CONTRACT_ID=$(python3 -m epic_events.cli contract create \
    --name "Contrat Test" \
    --description "Contrat de test complet" \
    --client-id $CLIENT_ID \
    --total-amount 10000 \
    --is-signed | grep -oP 'ID: \K\d+')
echo "Contrat créé avec ID: $CONTRACT_ID"

# 5. Créer un événement
START_DATE=$(date -d "+1 week" "+%Y-%m-%d 10:00")
END_DATE=$(date -d "+1 week" "+%Y-%m-%d 17:00")
EVENT_ID=$(python3 -m epic_events.cli event create \
    --name "Événement Test" \
    --contract-id $CONTRACT_ID \
    --start-date "$START_DATE" \
    --end-date "$END_DATE" \
    --location "Lieu de Test" \
    --attendees 100 \
    --notes "Notes de test" | grep -oP 'ID: \K\d+')
echo "Événement créé avec ID: $EVENT_ID"

# 6. Assigner le support à l'événement
python3 -m epic_events.cli event assign_support \
    --event-id $EVENT_ID \
    --support-id $SUPPORT_ID
echo "Support assigné à l'événement"

# 7. Vérifier que tout a été créé
echo "Vérification des données créées:"
echo "Liste des utilisateurs:"
python3 -m epic_events.cli user list
echo "Liste des clients:"
python3 -m epic_events.cli client list
echo "Liste des contrats:"
python3 -m epic_events.cli contract list
echo "Liste des événements:"
python3 -m epic_events.cli event list
```

Assurez-vous d'adapter les ID dans les commandes en fonction des identifiants réellement générés dans votre base de données. 