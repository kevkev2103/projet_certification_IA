#!/bin/bash
# Script simple pour démarrer CinApps

echo "🚀 Démarrage de CinApps..."

# Démarrer tous les services
docker-compose up -d

# Attendre quelques secondes
sleep 5

# Afficher le statut
echo ""
echo "📊 Statut des services :"
docker-compose ps

echo ""
echo "🎯 Accès aux services :"
echo "  • Streamlit: http://localhost:8501"
echo "  • API: http://localhost:8000"
echo "  • Grafana: http://localhost:3000"
echo ""
echo "✅ CinApps démarré !"