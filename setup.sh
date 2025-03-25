#!/bin/bash

# Couleurs pour le terminal
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Fonction pour afficher les messages
print_step() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

print_warning() {
    echo -e "${YELLOW}! $1${NC}"
}

# Fonction pour configurer Sentry
configure_sentry() {
    print_step "Configuration de Sentry"

    if [ ! -f ".env" ]; then
        cp .env.example .env || print_error "Impossible de créer le fichier .env"
        print_success "Fichier .env créé"
        
        echo -e "\n${YELLOW}Configuration de Sentry${NC}"
        read -p "Entrez votre DSN Sentry (laissez vide pour désactiver) : " sentry_dsn
        
        if [ ! -z "$sentry_dsn" ]; then
            sed -i "s|https://your-sentry-dsn@your-sentry-instance.ingest.sentry.io/your-project-id|$sentry_dsn|" .env
            print_success "DSN Sentry configuré"
        else
            sed -i "s|^SENTRY_DSN=.*|SENTRY_DSN=|" .env
            print_warning "Sentry désactivé"
        fi
    else
        print_warning "Le fichier .env existe déjà"
    fi
}

# Fonction pour installer l'application
install() {
    print_step "Installation de Epic Events"

    # Créer et activer l'environnement virtuel
    print_step "Configuration de l'environnement virtuel"
    python3 -m venv venv || print_error "Impossible de créer l'environnement virtuel"
    source venv/bin/activate || print_error "Impossible d'activer l'environnement virtuel"
    print_success "Environnement virtuel activé"

    # Installer les dépendances
    print_step "Installation des dépendances"
    pip install -r requirements.txt || print_error "Impossible d'installer les dépendances"
    print_success "Dépendances installées"

    # Configurer Sentry
    configure_sentry

    # Initialiser la base de données
    print_step "Initialisation de la base de données"
    python3 -m epic_events.cli init || print_error "Échec de l'initialisation de la base de données"
    print_success "Base de données initialisée"

    print_step "Installation terminée avec succès"
    echo -e "\nVous pouvez maintenant utiliser Epic Events avec les identifiants par défaut :"
    echo -e "Username: admin"
    echo -e "Password: admin123"
}

# Fonction pour nettoyer l'installation
cleanup() {
    print_step "Nettoyage de l'installation"

    # Désactiver l'environnement virtuel si actif
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate
        print_success "Environnement virtuel désactivé"
    fi

    # Supprimer les fichiers et dossiers
    rm -rf venv epic_events.db __pycache__ epic_events/__pycache__ epic_events/*/__pycache__ .env
    print_success "Fichiers supprimés"

    print_step "Nettoyage terminé"
}

# Fonction pour formater le code
format_code() {
    print_step "Formatage du code"

    # Vérifier si l'environnement virtuel est activé
    if [ -z "$VIRTUAL_ENV" ]; then
        if [ -d "venv" ]; then
            source venv/bin/activate || print_error "Impossible d'activer l'environnement virtuel"
        else
            print_error "L'environnement virtuel n'existe pas. Veuillez d'abord installer l'application."
        fi
    fi

    # Formater avec black
    print_step "Formatage avec black"
    black epic_events/ --line-length 100 || print_warning "Problèmes lors du formatage avec black"
    print_success "Code formaté avec black"

    # Vérifier avec flake8
    print_step "Vérification avec flake8"
    mkdir -p reports
    flake8 epic_events/ \
        --max-line-length=100 \
        --exclude=__pycache__,*.pyc,venv \
        --statistics \
        --ignore=E203,W503 \
        --output-file=reports/flake8_report.txt || true

    # Afficher le rapport flake8
    if [ -f reports/flake8_report.txt ]; then
        ERRORS_COUNT=$(wc -l < reports/flake8_report.txt)
        if [ "$ERRORS_COUNT" -eq 0 ]; then
            print_success "Aucun problème de style détecté"
        else
            print_warning "Nombre de problèmes détectés : $ERRORS_COUNT"
            echo -e "\nProblèmes détectés :"
            cat reports/flake8_report.txt
        fi
    fi

    print_step "Formatage terminé"
}

# Fonction pour générer un rapport HTML avec flake8
generate_html_report() {
    print_step "Génération du rapport HTML avec flake8"

    # Vérifier si l'environnement virtuel est activé
    if [ -z "$VIRTUAL_ENV" ]; then
        if [ -d "venv" ]; then
            source venv/bin/activate || print_error "Impossible d'activer l'environnement virtuel"
        else
            print_error "L'environnement virtuel n'existe pas. Veuillez d'abord installer l'application."
        fi
    fi

    # Créer le répertoire pour les rapports s'il n'existe pas
    mkdir -p reports/html

    # Exécuter flake8 avec le format HTML
    print_step "Exécution de flake8-html"
    flake8 epic_events/ \
        --max-line-length=100 \
        --exclude="__pycache__,*.pyc,venv" \
        --statistics \
        --ignore=E203,W503 \
        --format=html \
        --htmldir=reports/html || print_warning "Erreurs lors de la génération du rapport"

    print_success "Rapport HTML généré dans le dossier: reports/html"
    
    # Afficher l'URL pour ouvrir le rapport
    REPORT_PATH="$(pwd)/reports/html/index.html"
    print_step "Vous pouvez ouvrir le rapport avec la commande:"
    echo -e "${GREEN}firefox $REPORT_PATH${NC}"
    
    # Demander à l'utilisateur s'il souhaite ouvrir le rapport maintenant
    read -p "Voulez-vous ouvrir le rapport maintenant? (o/N) : " open_report
    if [[ $open_report =~ ^[Oo]$ ]]; then
        if command -v firefox &> /dev/null; then
            firefox "$REPORT_PATH"
        elif command -v google-chrome &> /dev/null; then
            google-chrome "$REPORT_PATH"
        elif command -v chromium &> /dev/null; then
            chromium "$REPORT_PATH"
        else
            print_warning "Aucun navigateur trouvé. Ouvrez le rapport manuellement."
        fi
    fi
}

# Menu principal
echo -e "${BLUE}Epic Events - Script de configuration${NC}"
echo -e "\nQue souhaitez-vous faire ?"
echo -e "1) Installer l'application"
echo -e "2) Nettoyer l'installation"
echo -e "3) Formater le code (black + flake8)"
echo -e "4) Configurer Sentry"
echo -e "5) Générer un rapport HTML avec flake8"
echo -e "6) Quitter"

read -p "Votre choix (1-6) : " choice

case $choice in
    1)
        install
        ;;
    2)
        echo -e "\n${RED}Attention : Cette action va supprimer tous les fichiers générés !${NC}"
        read -p "Êtes-vous sûr de vouloir continuer ? (o/N) : " confirm
        if [[ $confirm =~ ^[Oo]$ ]]; then
            cleanup
        else
            echo -e "\nOpération annulée."
        fi
        ;;
    3)
        format_code
        ;;
    4)
        configure_sentry
        ;;
    5)
        generate_html_report
        ;;
    6)
        echo -e "\nAu revoir !"
        exit 0
        ;;
    *)
        echo -e "\n${RED}Choix invalide${NC}"
        exit 1
        ;;
esac 