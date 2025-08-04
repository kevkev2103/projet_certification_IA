#!/bin/bash
# Script de visualisation des logs Docker pour Cinapps

set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 LOGS DOCKER CINAPPS${NC}"
echo -e "${BLUE}======================${NC}"

# Fonction pour afficher les options
show_menu() {
    echo -e "${YELLOW}Choisissez les logs à afficher :${NC}"
    echo "1. Tous les services"
    echo "2. API CRUD (cinapps-api)"
    echo "3. API Prédiction (prediction-api)"
    echo "4. Interface Streamlit (streamlit-app)"
    echo "5. Base de données MySQL"
    echo "6. Scraping (scraper-service)"
    echo "7. Pipeline de prédiction"
    echo "8. Prometheus"
    echo "9. Grafana"
    echo "10. Services en temps réel (suivi continu)"
    echo "11. Quitter"
}

# Fonction pour afficher les logs
show_logs() {
    local service=$1
    local follow=${2:-false}
    
    if [ "$follow" = true ]; then
        echo -e "${GREEN}📊 Logs en temps réel pour $service (Ctrl+C pour arrêter)${NC}"
        docker-compose logs -f $service
    else
        echo -e "${GREEN}📋 Derniers logs pour $service${NC}"
        docker-compose logs --tail=50 $service
    fi
}

# Menu principal
while true; do
    echo ""
    show_menu
    read -p "Votre choix [1-11]: " choice
    
    case $choice in
        1)
            show_logs ""
            ;;
        2)
            show_logs "cinapps-api"
            ;;
        3)
            show_logs "prediction-api"
            ;;
        4)
            show_logs "streamlit-app"
            ;;
        5)
            show_logs "mysql"
            ;;
        6)
            show_logs "scraper-service"
            ;;
        7)
            show_logs "prediction-pipeline"
            ;;
        8)
            show_logs "prometheus"
            ;;
        9)
            show_logs "grafana"
            ;;
        10)
            echo -e "${YELLOW}Choisissez le service pour le suivi en temps réel :${NC}"
            echo "1. Tous les services"
            echo "2. API CRUD"
            echo "3. API Prédiction"
            echo "4. Streamlit"
            echo "5. Retour au menu principal"
            read -p "Votre choix [1-5]: " real_time_choice
            
            case $real_time_choice in
                1) show_logs "" true ;;
                2) show_logs "cinapps-api" true ;;
                3) show_logs "prediction-api" true ;;
                4) show_logs "streamlit-app" true ;;
                5) continue ;;
                *) echo -e "${RED}❌ Option invalide${NC}" ;;
            esac
            ;;
        11)
            echo -e "${GREEN}👋 Au revoir !${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Option invalide${NC}"
            ;;
    esac
    
    # Pause avant de revenir au menu
    if [ "$choice" != "10" ]; then
        echo ""
        read -p "Appuyez sur Entrée pour revenir au menu..."
    fi
done