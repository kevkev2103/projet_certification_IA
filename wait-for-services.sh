#!/bin/bash
# Script d'attente pour les services Docker

set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔄 Attente des services...${NC}"

# Fonction d'attente pour un service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1

    echo -e "${YELLOW}⏳ Attente de $service_name ($host:$port)...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "http://$host:$port/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name est prêt !${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}   Tentative $attempt/$max_attempts...${NC}"
        sleep 5
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $service_name n'est pas accessible après $max_attempts tentatives${NC}"
    return 1
}

# Attendre MySQL (via l'API CRUD)
wait_for_service "cinapps-api" "8000" "API CRUD"

# Attendre l'API de prédiction
wait_for_service "prediction-api" "8001" "API Prédiction"

echo -e "${GREEN}🚀 Tous les services sont prêts !${NC}"

# Exécuter la commande passée en argument
exec "$@"