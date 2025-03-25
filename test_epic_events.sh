#!/bin/bash

# Couleurs pour le terminal
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Variables pour le suivi des tests
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Paramètres par défaut
ENABLE_SENTRY=false

# Fonction d'aide
show_help() {
    echo -e "${BLUE}Script de test pour Epic Events CRM${NC}"
    echo -e "\nUtilisation: $0 [options]"
    echo -e "\nOptions:"
    echo -e "  --enable-sentry    Active Sentry pour journaliser les événements pendant les tests"
    echo -e "  --help, -h         Affiche cette aide"
    echo -e "\nExemples:"
    echo -e "  $0                 Exécute les tests avec Sentry désactivé"
    echo -e "  $0 --enable-sentry Exécute les tests avec Sentry activé"
    exit 0
}

# Traitement des arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --enable-sentry)
      ENABLE_SENTRY=true
      shift
      ;;
    --help|-h)
      show_help
      ;;
    *)
      shift
      ;;
  esac
done

# Configuration de Sentry selon le paramètre
if [ "$ENABLE_SENTRY" = true ]; then
    echo -e "${BLUE}Sentry est activé pour les tests${NC}"
    # Ne pas modifier SENTRY_DSN pour utiliser celui défini dans .env
    export PYTHONWARNINGS="ignore"
else
    echo -e "${BLUE}Sentry est désactivé pour les tests${NC}"
    # Désactiver l'affichage des logs Sentry pour les tests
    export SENTRY_DSN=""
    export PYTHONWARNINGS="ignore"
fi

# Fonctions utilitaires
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
}

# Fonction pour générer un identifiant unique
generate_unique_id() {
    echo "test_$(date +%s%N | md5sum | head -c 8)"
}

# Fonction pour nettoyer l'environnement
cleanup() {
    print_header "Nettoyage de l'environnement"
    rm -f epic_events.db
    print_success "Base de données supprimée"
}

# Fonction pour initialiser l'environnement
setup() {
    print_header "Initialisation de l'environnement"
    
    # Activer l'environnement virtuel
    source venv/bin/activate || {
        print_error "Impossible d'activer l'environnement virtuel"
        exit 1
    }
    print_success "Environnement virtuel activé"

    # Initialiser la base de données
    python3 -m epic_events.cli init > /dev/null 2>&1 || {
        print_error "Échec de l'initialisation de la base de données"
        exit 1
    }
    print_success "Base de données initialisée"
}

# Test de la gestion des utilisateurs
test_users() {
    print_header "Test de la gestion des utilisateurs"
    
    # Créer un commercial
    USERNAME="commercial_$(generate_unique_id)"
    python3 -m epic_events.cli user create \
        --username "$USERNAME" \
        --email "${USERNAME}@test.com" \
        --password "password123" \
        --first-name "Test" \
        --last-name "Commercial" \
        --role "commercial" > /dev/null 2>&1 && \
        print_success "Création d'un commercial" || \
        print_error "Échec de la création du commercial"

    # Vérifier la liste des utilisateurs
    python3 -m epic_events.cli user list | grep -q "$USERNAME" > /dev/null 2>&1 && \
        print_success "Commercial trouvé dans la liste" || \
        print_error "Commercial non trouvé dans la liste"
}

# Test de la gestion des clients
test_clients() {
    print_header "Test de la gestion des clients"
    
    # Créer un client
    EMAIL="client_$(generate_unique_id)@test.com"
    python3 -m epic_events.cli client create \
        --first-name "Test" \
        --last-name "Client" \
        --email "$EMAIL" \
        --phone "+33123456789" \
        --company "Test Company" \
        --commercial-id 2 > /dev/null 2>&1 && \
        print_success "Création d'un client" || \
        print_error "Échec de la création du client"

    # Vérifier la liste des clients
    python3 -m epic_events.cli client list | grep -q "$EMAIL" > /dev/null 2>&1 && \
        print_success "Client trouvé dans la liste" || \
        print_error "Client non trouvé dans la liste"
}

# Test de la gestion des contrats
test_contracts() {
    print_header "Test de la gestion des contrats"
    
    # Créer un contrat
    CONTRACT_NAME="Contrat_$(generate_unique_id)"
    python3 -m epic_events.cli contract create \
        --name "$CONTRACT_NAME" \
        --client-id 1 \
        --total-amount 5000 \
        --is-signed > /dev/null 2>&1 && \
        print_success "Création d'un contrat" || \
        print_error "Échec de la création du contrat"

    # Vérifier la liste des contrats
    python3 -m epic_events.cli contract list | grep -q "$CONTRACT_NAME" > /dev/null 2>&1 && \
        print_success "Contrat trouvé dans la liste" || \
        print_error "Contrat non trouvé dans la liste"
}

# Test de la gestion des événements
test_events() {
    print_header "Test de la gestion des événements"
    
    # Créer un événement
    EVENT_NAME="Event_$(generate_unique_id)"
    START_DATE=$(date -d "+1 day" "+%Y-%m-%d 09:00")
    END_DATE=$(date -d "+1 day" "+%Y-%m-%d 17:00")
    
    python3 -m epic_events.cli event create \
        --name "$EVENT_NAME" \
        --contract-id 1 \
        --start-date "$START_DATE" \
        --end-date "$END_DATE" \
        --location "Test Location" \
        --attendees 50 > /dev/null 2>&1 && \
        print_success "Création d'un événement" || \
        print_error "Échec de la création de l'événement"

    # Vérifier la liste des événements
    python3 -m epic_events.cli event list | grep -q "$EVENT_NAME" > /dev/null 2>&1 && \
        print_success "Événement trouvé dans la liste" || \
        print_error "Événement non trouvé dans la liste"
}

# Fonction pour afficher le rapport final
show_report() {
    print_header "Rapport des tests"
    echo -e "Tests totaux : $TOTAL_TESTS"
    echo -e "Tests réussis : ${GREEN}$PASSED_TESTS${NC}"
    echo -e "Tests échoués : ${RED}$FAILED_TESTS${NC}"
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "\n${GREEN}Tous les tests ont réussi !${NC}"
        exit 0
    else
        echo -e "\n${RED}Certains tests ont échoué.${NC}"
        exit 1
    fi
}

# Exécution principale
cleanup
setup
test_users
test_clients
test_contracts
test_events
show_report