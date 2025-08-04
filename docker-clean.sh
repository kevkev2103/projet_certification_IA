#!/bin/bash
# Script de nettoyage Docker pour Cinapps

set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 NETTOYAGE DOCKER CINAPPS${NC}"
echo -e "${BLUE}============================${NC}"

# Fonction pour demander confirmation
confirm() {
    read -p "Êtes-vous sûr ? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    else
        return 1
    fi
}

# Arrêter tous les services
echo -e "${YELLOW}🛑 Arrêt des services...${NC}"
docker-compose down

echo -e "${YELLOW}🗑️  Options de nettoyage :${NC}"
echo "1. Nettoyage standard (containers arrêtés)"
echo "2. Nettoyage complet (images + volumes)"
echo "3. Nettoyage total (tout supprimer)"
echo "4. Annuler"

read -p "Choisissez une option [1-4]: " choice

case $choice in
    1)
        echo -e "${YELLOW}🧹 Nettoyage standard...${NC}"
        docker system prune -f
        echo -e "${GREEN}✅ Nettoyage standard terminé${NC}"
        ;;
    2)
        echo -e "${YELLOW}⚠️  Nettoyage complet (images + volumes)${NC}"
        echo -e "${RED}ATTENTION: Cela supprimera toutes les données de la base de données !${NC}"
        if confirm; then
            docker-compose down -v
            docker system prune -a -f
            docker volume prune -f
            echo -e "${GREEN}✅ Nettoyage complet terminé${NC}"
        else
            echo -e "${YELLOW}❌ Annulé${NC}"
        fi
        ;;
    3)
        echo -e "${RED}⚠️  NETTOYAGE TOTAL${NC}"
        echo -e "${RED}ATTENTION: Cela supprimera TOUT (conteneurs, images, volumes, réseaux) !${NC}"
        if confirm; then
            docker-compose down -v --remove-orphans
            docker system prune -a -f --volumes
            docker network prune -f
            docker volume prune -f
            # Supprimer spécifiquement les éléments Cinapps
            docker volume rm cinapps-mysql-data cinapps-prometheus-data cinapps-grafana-data 2>/dev/null || true
            docker network rm cinapps-network 2>/dev/null || true
            echo -e "${GREEN}✅ Nettoyage total terminé${NC}"
        else
            echo -e "${YELLOW}❌ Annulé${NC}"
        fi
        ;;
    4)
        echo -e "${YELLOW}❌ Annulé${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Option invalide${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}📊 Espace disque libéré :${NC}"
docker system df