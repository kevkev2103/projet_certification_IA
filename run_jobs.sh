#!/bin/bash



echo "🚀 Nettoyage et scraping avec conteneur MySQL existant..."

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Étape 1: Nettoyage direct avec le conteneur MySQL
print_status "Étape 1: Nettoyage de la base de données..."

# Utiliser le conteneur MySQL existant
docker exec mysql-nksg4g0o4ww44cos0ww84gkw-092802151189 mysql -u kevin -pkevinpass cinapps -e "
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE table_predictions;
TRUNCATE TABLE table_participations;
TRUNCATE TABLE table_films;
TRUNCATE TABLE table_personnes;
SET FOREIGN_KEY_CHECKS = 1;
SELECT '✅ Base de données nettoyée avec succès' as status;
"

if [ $? -eq 0 ]; then
    print_status "✅ Nettoyage réussi"
else
    print_error "❌ Erreur lors du nettoyage"
    exit 1
fi

# Étape 2: Lancement du scraping
print_status "Étape 2: Lancement du scraping..."
sleep 3

# Lancer le scraping
docker compose --profile scraping up scraper-service
docker compose --profile pipeline up prediction-pipeline

if [ $? -eq 0 ]; then
    print_status "✅ Scraping terminé avec succès!"
else
    print_error "❌ Erreur lors du scraping"
    exit 1
fi

print_status "🎉 Processus terminé avec succès!" 