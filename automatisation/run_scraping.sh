#!/bin/bash

# Script de lancement du scraping avec nettoyage préalable
# Usage: ./run_scraping.sh

echo "🚀 Démarrage du processus de scraping..."

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages colorés
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Étape 1: Nettoyage de la base de données
print_status "Étape 1: Nettoyage de la base de données..."

# Option 1: Utiliser le script Python
if [ -f "clean_db_manual.py" ]; then
    print_status "Exécution du script Python de nettoyage..."
    python3 clean_db_manual.py
    if [ $? -eq 0 ]; then
        print_status "✅ Nettoyage Python réussi"
    else
        print_error "❌ Erreur lors du nettoyage Python"
        exit 1
    fi
else
    print_warning "Script Python non trouvé, utilisation de MySQL Docker..."
    # Option 2: Utiliser MySQL Docker
    docker exec cinapps-mysql mysql -u kevin -pkevinpass cinapps < clean_database.sql
    if [ $? -eq 0 ]; then
        print_status "✅ Nettoyage MySQL Docker réussi"
    else
        print_error "❌ Erreur lors du nettoyage MySQL Docker"
        exit 1
    fi
fi

# Étape 2: Lancement du scraping
print_status "Étape 2: Lancement du scraping..."
print_status "Attendre 3 secondes avant de lancer le scraping..."
sleep 3

# Lancer le scraping
print_status "Lancement de Scrapy..."
scrapy crawl alloc_newfilms

if [ $? -eq 0 ]; then
    print_status "✅ Scraping terminé avec succès!"
else
    print_error "❌ Erreur lors du scraping"
    exit 1
fi

print_status "🎉 Processus terminé avec succès!" 