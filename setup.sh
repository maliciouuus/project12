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

# Vérifie si l'environnement virtuel est activé, sinon l'active
ensure_venv_activated() {
    if [ -z "$VIRTUAL_ENV" ]; then
        if [ -d "venv" ]; then
            source venv/bin/activate || print_error "Impossible d'activer l'environnement virtuel"
            print_success "Environnement virtuel activé"
        else
            print_error "L'environnement virtuel n'existe pas. Veuillez d'abord installer l'application (option 1)."
        fi
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

    # Demander confirmation pour supprimer .env
    if [ -f ".env" ]; then
        read -p "Voulez-vous également supprimer le fichier .env contenant la configuration Sentry? (o/N) : " remove_env
        if [[ $remove_env =~ ^[Oo]$ ]]; then
            rm -f .env
            print_success "Fichier .env supprimé"
        else
            print_success "Fichier .env conservé"
        fi
    fi

    # Supprimer les fichiers et dossiers (sauf .env si conservé)
    rm -rf venv epic_events.db __pycache__ epic_events/__pycache__ epic_events/*/__pycache__ *.pyc epic_events/*.pyc epic_events/*/*.pyc
    print_success "Fichiers et caches supprimés"

    print_step "Nettoyage terminé"
}

# Fonction pour générer un rapport HTML avec flake8
generate_html_report() {
    print_step "Génération du rapport HTML avec flake8"

    # Vérifier si l'environnement virtuel est activé
    ensure_venv_activated

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

# Fonction pour lancer le menu interactif
run_menu() {
    print_step "Lancement du menu interactif Epic Events"
    
    # Vérifier si l'environnement virtuel est activé
    ensure_venv_activated
    
    print_step "Démarrage du menu..."
    python -m epic_events.cli menu
    
    print_success "Session du menu terminée"
}

# Menu principal
show_menu() {
    echo -e "${BLUE}Epic Events - Script de configuration${NC}"
    echo -e "\nQue souhaitez-vous faire ?"
    echo -e "1) Installer l'application"
    echo -e "2) Lancer le menu interactif"
    echo -e "3) Générer un rapport HTML avec flake8"
    echo -e "4) Nettoyer l'installation"
    echo -e "5) Quitter"

    read -p "Votre choix (1-5) : " choice

    case $choice in
        1)
            install
            ;;
        2)
            run_menu
            ;;
        3)
            generate_html_report
            ;;
        4)
            echo -e "\n${RED}Attention : Cette action va supprimer tous les fichiers générés et les caches !${NC}"
            read -p "Êtes-vous sûr de vouloir continuer ? (o/N) : " confirm
            if [[ $confirm =~ ^[Oo]$ ]]; then
                cleanup
            else
                echo -e "\nOpération annulée."
            fi
            ;;
        5)
            echo -e "\nAu revoir !"
            exit 0
            ;;
        *)
            echo -e "\n${RED}Choix invalide${NC}"
            return 1
            ;;
    esac
    
    # Demander à l'utilisateur s'il souhaite revenir au menu principal
    read -p "Voulez-vous revenir au menu principal? (O/n) : " return_menu
    if [[ $return_menu =~ ^[Nn]$ ]]; then
        echo -e "\nAu revoir !"
        exit 0
    else
        clear  # Nettoyer l'écran avant d'afficher à nouveau le menu
        show_menu  # Afficher à nouveau le menu
    fi
}

# Démarrer le script avec le menu principal
show_menu 