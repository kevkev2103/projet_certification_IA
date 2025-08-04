#!/bin/bash
# Script de démarrage complet pour Cinapps Docker

set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 DÉMARRAGE CINAPPS DOCKER${NC}"
echo -e "${BLUE}================================${NC}"

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé${NC}"
    exit 1
fi

# Vérifier si Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose n'est pas installé${NC}"
    exit 1
fi

# Vérifier si le fichier .env existe
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Fichier .env non trouvé${NC}"
    if [ -f .env.example ]; then
        echo -e "${YELLOW}📋 Copie de .env.example vers .env${NC}"
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Veuillez ajuster les valeurs dans .env si nécessaire${NC}"
    else
        echo -e "${RED}❌ Fichier .env.example non trouvé${NC}"
        exit 1
    fi
fi

echo -e "${YELLOW}🔄 Construction et démarrage des services...${NC}"

# Construire et démarrer les services principaux
docker-compose up --build -d mysql cinapps-api streamlit-app prometheus grafana

echo -e "${YELLOW}⏳ Attente que les services soient prêts...${NC}"
sleep 10

# Vérifier l'état des services
echo -e "${BLUE}📊 État des services :${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}✅ DÉMARRAGE TERMINÉ !${NC}"
echo -e "${GREEN}===================${NC}"
echo ""
echo -e "${BLUE}🌐 URLs disponibles :${NC}"
echo -e "   • API CRUD (Swagger)  : ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "   • Interface Streamlit: ${YELLOW}http://localhost:8501${NC}"
echo -e "   • Prometheus         : ${YELLOW}http://localhost:9090${NC}"
echo -e "   • Grafana           : ${YELLOW}http://localhost:3000${NC}"
echo ""
echo -e "${BLUE}🔧 Commandes utiles :${NC}"
echo -e "   • Logs en temps réel : ${YELLOW}docker-compose logs -f${NC}"
echo -e "   • Arrêter les services: ${YELLOW}docker-compose down${NC}"
echo -e "   • Lancer le scraping  : ${YELLOW}docker-compose --profile scraping up scraper-service${NC}"
echo -e "   • Lancer le pipeline  : ${YELLOW}docker-compose --profile pipeline up prediction-pipeline${NC}"