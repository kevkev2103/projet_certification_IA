#!/bin/bash

# Script de lancement du scraping avec nettoyage préalable pour Docker
# Usage: ./run_scraping_docker.sh

echo "🚀 Démarrage du processus de scraping avec Docker..."

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

# Vérifier que Docker est en cours d'exécution
print_status "Vérification de Docker..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker n'est pas en cours d'exécution"
    exit 1
fi

# Vérifier que le conteneur MySQL existe
print_status "Vérification du conteneur MySQL..."
if ! docker ps | grep -q "cinapps-mysql"; then
    print_error "Le conteneur cinapps-mysql n'est pas en cours d'exécution"
    print_status "Démarrage des services Docker..."
    docker-compose up -d mysql
    sleep 10
fi

# Étape 1: Nettoyage de la base de données
print_status "Étape 1: Nettoyage de la base de données Docker..."

# Option 1: Utiliser le script Python dans le conteneur
print_status "Exécution du script Python de nettoyage dans Docker..."
docker run --rm \
    --network cinapps-network \
    -v $(pwd):/app \
    -w /app \
    -e MYSQL_HOST=mysql \
    -e MYSQL_USER=kevin \
    -e MYSQL_PASSWORD=kevinpass \
    -e MYSQL_DATABASE=cinapps \
    python:3.10-slim \
    bash -c "pip install mysql-connector-python python-dotenv && python3 clean_db_manual.py"

if [ $? -eq 0 ]; then
    print_status "✅ Nettoyage Python Docker réussi"
else
    print_warning "Script Python échoué, utilisation de MySQL direct..."
    # Option 2: Utiliser MySQL directement dans le conteneur
    docker exec cinapps-mysql mysql -u kevin -pkevinpass cinapps < clean_database.sql
    if [ $? -eq 0 ]; then
        print_status "✅ Nettoyage MySQL direct réussi"
    else
        print_error "❌ Erreur lors du nettoyage MySQL"
        exit 1
    fi
fi

# Étape 2: Lancement du scraping
print_status "Étape 2: Lancement du scraping Docker..."
print_status "Attendre 3 secondes avant de lancer le scraping..."
sleep 3

# Lancer le scraping avec Docker
print_status "Lancement de Scrapy avec Docker..."
docker-compose --profile scraping up scraper-service --build

if [ $? -eq 0 ]; then
    print_status "✅ Scraping Docker terminé avec succès!"
else
    print_error "❌ Erreur lors du scraping Docker"
    exit 1
fi

print_status "🎉 Processus Docker terminé avec succès!" 