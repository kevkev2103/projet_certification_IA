# 🐳 Guide Docker - Cinapps Project

## 🚀 **Démarrage rapide**

### **Option 1 : Script automatique (Recommandé)**
```bash
# Démarrer tout l'écosystème
./docker-start.sh
```

### **Option 2 : Commandes manuelles**
```bash
# Construire et démarrer tous les services
docker-compose up --build -d

# Vérifier l'état des services
docker-compose ps
```

## 🌐 **URLs disponibles après démarrage**

| Service | URL | Description |
|---------|-----|-------------|
| **API CRUD** | http://localhost:8000 | API principale avec JWT |
| **API CRUD (Swagger)** | http://localhost:8000/docs | Documentation interactive |
| **API Prédiction** | http://localhost:8001 | API de machine learning |
| **API Prédiction (Docs)** | http://localhost:8001/docs | Documentation ML |
| **Interface Streamlit** | http://localhost:8501 | Dashboard utilisateur |
| **Prometheus** | http://localhost:9090 | Monitoring metrics |
| **Grafana** | http://localhost:3000 | Dashboards (admin/admin123) |

## 🏗️ **Architecture Docker**

```
🐳 Cinapps Docker Stack
├── 🗄️  mysql (3306)           → Base de données
├── 🔧  cinapps-api (8000)      → API CRUD avec JWT
├── 🤖  prediction-api (8001)   → API ML + Prédictions
├── 🎭  streamlit-app (8501)    → Interface utilisateur
├── 🕷️  scraper-service         → Scraping Allociné (optionnel)
├── ⚙️  prediction-pipeline     → Pipeline de prédiction (optionnel)
├── 📊  prometheus (9090)       → Métriques
└── 📈  grafana (3000)          → Dashboards
```

## ⚙️ **Gestion des services**

### **Logs et monitoring**
```bash
# Script interactif pour les logs
./docker-logs.sh

# Logs de tous les services en temps réel
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f cinapps-api
docker-compose logs -f streamlit-app
```

### **Services optionnels**

#### **Scraping (récupération des films)**
```bash
# Lancer le scraping des films Allociné
docker-compose --profile scraping up scraper-service

# Suivre les logs du scraping
docker-compose logs -f scraper-service
```

#### **Pipeline de prédiction**
```bash
# Lancer le pipeline de prédiction
docker-compose --profile pipeline up prediction-pipeline

# Suivre les logs du pipeline
docker-compose logs -f prediction-pipeline
```

## 🧹 **Nettoyage et maintenance**

### **Script de nettoyage**
```bash
# Script interactif avec options
./docker-clean.sh
```

### **Commandes manuelles**
```bash
# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes (ATTENTION: supprime les données)
docker-compose down -v

# Nettoyage complet du système Docker
docker system prune -a -f
```

## 🔧 **Configuration**

### **Variables d'environnement**
Les configurations sont intégrées dans `docker-compose.yml` basées sur vos fichiers .env existants :

- **MySQL** : kevin/kevinpass sur base `cinapps`
- **JWT Secret** : `la_clé_secrète_pour_JWT`
- **Grafana** : admin/admin123

### **Données persistantes**
Les volumes Docker conservent vos données :
- `cinapps-mysql-data` → Base de données MySQL
- `cinapps-prometheus-data` → Métriques Prometheus
- `cinapps-grafana-data` → Configuration Grafana

## 🚨 **Dépannage**

### **Problèmes courants**

#### **Port déjà utilisé**
```bash
# Vérifier les ports occupés
sudo netstat -tulpn | grep :8000

# Arrêter les services locaux si nécessaire
sudo systemctl stop mysql
```

#### **Services qui ne démarrent pas**
```bash
# Vérifier l'état des services
docker-compose ps

# Voir les logs d'erreur
docker-compose logs [nom-du-service]

# Reconstruire un service spécifique
docker-compose build [nom-du-service]
docker-compose up -d [nom-du-service]
```

#### **Base de données non accessible**
```bash
# Vérifier MySQL
docker-compose exec mysql mysql -u kevin -pkevinpass -e "SHOW DATABASES;"

# Réinitialiser la base de données
docker-compose down -v
docker-compose up -d mysql
```

## 🔄 **Migration depuis l'ancienne méthode**

Si vous utilisiez l'ancienne méthode (services locaux) :

1. **Arrêtez les services locaux :**
```bash
# Arrêter MySQL local
sudo systemctl stop mysql

# Arrêter les APIs FastAPI/Uvicorn (Ctrl+C dans leurs terminaux)
```

2. **Lancez Docker :**
```bash
./docker-start.sh
```

3. **Vérifiez que tout fonctionne :**
- Streamlit : http://localhost:8501
- APIs : http://localhost:8000/docs

## 📊 **Monitoring et métriques**

### **Prometheus (http://localhost:9090)**
- Métriques des APIs FastAPI
- Performance des services
- Health checks

### **Grafana (http://localhost:3000)**
- Login : admin/admin123
- Dashboards préconfigurés
- Alerting disponible

## 🎯 **Workflow recommandé**

1. **Développement quotidien :**
```bash
./docker-start.sh
# Développer votre code
# Les changements sont automatiquement détectés
```

2. **Tests et données :**
```bash
# Scraper des nouveaux films
docker-compose --profile scraping up scraper-service

# Générer des prédictions
docker-compose --profile pipeline up prediction-pipeline
```

3. **Fin de journée :**
```bash
# Arrêter proprement
docker-compose down
```

## ✨ **Avantages de Docker**

- ✅ **Configuration unifiée** → Un seul `docker-compose up`
- ✅ **Isolation** → Pas de conflits avec votre système
- ✅ **Reproductibilité** → Même environnement partout
- ✅ **Monitoring intégré** → Prometheus + Grafana inclus
- ✅ **Health checks** → Détection automatique des problèmes
- ✅ **Scalabilité** → Facile d'ajouter des services