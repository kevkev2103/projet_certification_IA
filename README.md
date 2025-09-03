🎬 Ciné App - Prédiction d'entrées cinéma

Application d'intelligence artificielle pour aider les exploitants de cinéma à optimiser leur programmation en prédisant le nombre d'entrées des films.

✨ Fonctionnalités principales

🤖 Modèle ML : Prédiction d'entrées basée sur Random Forest Regressor

🌐 API REST : Interface FastAPI sécurisée avec authentification JWT

📊 Interface utilisateur : Application Streamlit intuitive et responsive

🕷️ Scraping automatique : Collecte de données films depuis Allociné

🗄️ Base de données : Stockage MySQL avec gestion des relations

📈 Monitoring : Métriques Prometheus et tableau de bord Grafana

🐳 Conteneurisation : Déploiement Docker avec orchestration

<img width="581" height="206" alt="image" src="https://github.com/user-attachments/assets/0cef7bf4-87fd-4625-af18-1cd4a08e8dcf" />


🚀 Prérequis techniques

Python 3.10+

Docker et Docker Compose

MySQL 8.0 (inclus dans Docker)

Git

⚡ Installation et démarrage

Cloner le projet

git clone https://github.com/kevkev2103/projet_certification_IA.git
cd projet_certification_IA

Lancer avec Docker
docker compose up --build

Accès aux services

Interface utilisateur : http://localhost:8501

API documentation : http://localhost:8002/docs

Monitoring Grafana : http://localhost:3000

🔧 Utilisation
Interface Streamlit

Ouvrir http://localhost:8501

Se connecter avec les identifiants de test

Consulter les films et leurs prédictions

API REST

# Obtenir un token d'authentification
curl -X POST "http://localhost:8002/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=test123"

# Consulter les films (avec token)
curl -X GET "http://localhost:8002/films/" \
  -H "Authorization: Bearer <votre_token>"

Scraping de données

# Lancer le scraping manuellement
docker compose run scraper-service

# Ou utiliser le script
./automatisation/run_scraping.sh

🏗️ Architecture technique

<img width="542" height="267" alt="image" src="https://github.com/user-attachments/assets/0de07642-8acf-4d39-847d-72ac718f0849" />



🧪 Tests

# Lancer les tests unitaires
pytest tests/

# Tests avec couverture
pytest --cov=. tests/

# Tests d'intégration
pytest tests/test_integration_simple.py

📊 Modèle Machine Learning

Algorithme : Random Forest Regressor (100 arbres)

Features : Budget, durée, genre, pays, acteurs, réalisateur

Métriques : MAE, R², RMSE

Performance : R² = 0.73 sur les données de test

🔒 Sécurité

Authentification : JWT avec expiration 30 minutes

Mots de passe : Hachage bcrypt + pbkdf2_sha256

API : Validation Pydantic automatique

Base de données : Relations avec suppression en cascade

🚀 Déploiement

Le projet est configuré pour fonctionner en production avec :

GCP (Google Cloud Platform)

Coolify pour l'orchestration

GitHub Actions pour la CI/CD

Monitoring en temps réel

👨‍💻 Contributeurs

Projet réalisé par : Kevin - Certification IA

