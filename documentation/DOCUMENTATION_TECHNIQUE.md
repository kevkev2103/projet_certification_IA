# Documentation Technique - Cinapps

## 📋 **Vue d'ensemble**

**Cinapps** est une application de prédiction d'entrées cinéma utilisant l'intelligence artificielle. Cette documentation couvre l'architecture, l'installation, l'utilisation et les API du projet.

## 🏗️ **Architecture du système**

### **Diagramme de l'architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Allociné      │    │   Base MySQL    │    │   API CRUD      │
│   (Scraping)    │───▶│   (Stockage)    │◀───│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   API ML        │    │   Streamlit     │
                       │   (Prédictions) │    │   (Interface)   │
                       └─────────────────┘    └─────────────────┘
```

### **Composants principaux**

1. **Scraping Allociné** (`automatisation/`)
   - Collecte automatique des sorties de films
   - Stockage en base de données MySQL

2. **API CRUD** (`cinapps_api/`)
   - Gestion des films et utilisateurs
   - Authentification JWT
   - Endpoints REST sécurisés

3. **API de Prédiction** (`API_s/`)
   - Modèle ML CatBoost
   - Prédiction d'entrées cinéma
   - Stockage des prédictions

4. **Interface Streamlit** (`streamlit/`)
   - Dashboard utilisateur
   - Visualisation des prédictions
   - Classement des films

5. **Base de données** (MySQL)
   - Stockage des films et prédictions
   - Gestion des utilisateurs

## 🚀 **Installation et configuration**

### **Prérequis**
- Python 3.10+
- MySQL 8.0
- Docker (optionnel)

### **1. Cloner le projet**
```bash
git clone <repository-url>
cd projet
```

### **2. Configuration des variables d'environnement**
Créer un fichier `.env` à la racine :
```ini
# Base de données MySQL
MYSQL_USER=db_user
MYSQL_PASSWORD=user_mdp
MYSQL_HOST=127.0.0.1
MYSQL_DATABASE=cinapps
DATABASE_URL=mysql+pymysql://db_user:user_mdp@127.0.0.1:3306/cinapps

# URLs des APIs
URL_API_CRUD=http://127.0.0.1:8000
URL_API_PRED=http://127.0.0.1:8001
```

### **3. Installation des dépendances**
```bash
# API CRUD
cd cinapps_api
pip install -r requirements.txt

# API de prédiction
cd ../API_s
pip install -r requirements.txt

# Interface Streamlit
cd ../streamlit
pip install -r requirements.txt

# Scraping
cd ../automatisation
pip install -r requirements.txt
```

### **4. Initialisation de la base de données**
```bash
# Démarrer MySQL avec Docker
docker-compose up -d mysql

# Créer la base de données
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS cinapps;"
```

## 🔧 **Démarrage des services**

### **1. Base de données**
```bash
docker-compose up -d mysql
```

### **2. API CRUD**
```bash
cd cinapps_api
uvicorn app.main:app --reload --port 8000
```
- **Documentation Swagger** : http://127.0.0.1:8000/docs
- **Endpoints disponibles** : Films, Authentification, Prédictions

### **3. API de Prédiction**
```bash
cd API_s
uvicorn main:app --reload --port 8001
```
- **Documentation** : http://127.0.0.1:8001/docs

### **4. Interface Streamlit**
```bash
cd streamlit
streamlit run app.py --server.port 8501
```
- **Interface utilisateur** : http://127.0.0.1:8501

## 🔐 **Authentification et sécurité**

### **Système d'authentification**
- **Méthode** : JWT (JSON Web Tokens)
- **Algorithme** : HS256
- **Durée de vie** : 30 minutes

### **Utilisateur par défaut**
```sql
-- Créé automatiquement dans init_bdd_app.sql
INSERT INTO main_user (username, password) 
VALUES ('testuser', 'pbkdf2_sha256$600000$salt$6JQqRHzwqgJkR+PtRbnevHFztd5GXqGVNAxVwpBvIbY=');
```
- **Username** : `testuser`
- **Password** : `test123`

### **Obtention d'un token**
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=test123"
```

## 📡 **API Documentation**

### **API CRUD (Port 8000)**

#### **Authentification**
```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=testuser&password=test123
```

#### **Films**
```http
GET /films/                    # Liste tous les films
POST /films/                   # Créer un film
PUT /films/{id}               # Modifier un film
DELETE /films/{id}            # Supprimer un film
GET /films/{id}/acteurs/      # Acteurs d'un film
GET /films/{id}/realisateurs/ # Réalisateurs d'un film
```

#### **Prédictions**
```http
GET /predictions/              # Toutes les prédictions
GET /films/{id}/predictions/   # Prédictions d'un film
```

### **API de Prédiction (Port 8001)**

#### **Prédiction d'entrées**
```http
POST /prediction/
Authorization: Bearer <token>
Content-Type: application/json

{
  "id_film": 1,
  "budget": 50000000,
  "duree": 120,
  "genre": "Action",
  "pays": "USA",
  "salles_premiere_semaine": 350,
  "scoring_acteurs_realisateurs": 0.8,
  "coeff_studio": 1.2,
  "year": 2024
}
```

## 🎬 **Workflow de données**

### **1. Collecte de données**
```bash
cd automatisation
scrapy crawl films -o films_export.json
```

### **2. Traitement et prédiction**
```bash
python prediction_pipeline.py
```

### **3. Visualisation**
- Accéder à http://127.0.0.1:8501
- Se connecter avec `testuser` / `test123`
- Consulter les prédictions des films de la semaine

## 📊 **Modèle de données**

### **Table Films**
```sql
CREATE TABLE table_films (
    id_film INT AUTO_INCREMENT PRIMARY KEY,
    titre VARCHAR(255) NOT NULL,
    duree INT,
    salles INT,
    genre VARCHAR(255),
    date_sortie DATE,
    pays VARCHAR(255),
    studio VARCHAR(255),
    description TEXT,
    image VARCHAR(255),
    budget INT,
    entrees INT,
    film_url VARCHAR(255),
    is_pred BOOLEAN DEFAULT FALSE
);
```

### **Table Prédictions**
```sql
CREATE TABLE table_predictions (
    id_prediction INT AUTO_INCREMENT PRIMARY KEY,
    id_film INT NOT NULL,
    prediction_entrees INT NOT NULL,
    date_prediction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_film) REFERENCES table_films(id_film)
);
```

### **Table Utilisateurs**
```sql
CREATE TABLE main_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
```

## 🔍 **Tests et validation**

### **Tests des APIs**
```bash
# Test API CRUD
curl -X GET "http://localhost:8000/films/" \
  -H "Authorization: Bearer <token>"

# Test API Prédiction
curl -X POST "http://localhost:8001/prediction/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"id_film": 1, "budget": 50000000, ...}'
```

### **Validation des données**
- Vérification de la cohérence des prédictions
- Contrôle des valeurs aberrantes
- Validation des formats de dates

## 📈 **Monitoring et logs**

### **Logs applicatifs**
- **API CRUD** : Logs dans la console
- **API Prédiction** : Fichier `prediction.log`
- **Streamlit** : Logs dans la console

### **Métriques de performance**
- Temps de réponse des APIs
- Précision des prédictions
- Utilisation de la base de données

## 🛠️ **Dépannage**

### **Problèmes courants**

#### **Erreur de connexion à la base de données**
```bash
# Vérifier que MySQL est démarré
docker-compose ps

# Vérifier les variables d'environnement
echo $DATABASE_URL
```

#### **Erreur d'authentification**
```bash
# Vérifier que l'utilisateur existe
mysql -u root -p cinapps -e "SELECT * FROM main_user;"

# Recréer l'utilisateur si nécessaire
INSERT INTO main_user (username, password) 
VALUES ('testuser', 'pbkdf2_sha256$600000$salt$6JQqRHzwqgJkR+PtRbnevHFztd5GXqGVNAxVwpBvIbY=');
```

#### **Erreur de prédiction**
```bash
# Vérifier que le modèle est chargé
ls -la API_s/model.pkl

# Vérifier les logs de l'API
tail -f API_s/prediction.log
```

## 📚 **Références techniques**

### **Technologies utilisées**
- **FastAPI** : Framework web pour les APIs
- **SQLModel** : ORM pour la base de données
- **CatBoost** : Modèle de machine learning
- **Streamlit** : Interface utilisateur
- **Scrapy** : Framework de scraping
- **MySQL** : Base de données relationnelle
- **JWT** : Authentification sécurisée

### **Standards respectés**
- **OpenAPI 3.0** : Documentation des APIs
- **REST** : Architecture des APIs
- **OWASP Top 10** : Sécurité des applications
- **WCAG 2.1** : Accessibilité

## 🔄 **Maintenance et évolutions**

### **Tâches de maintenance**
- Sauvegarde quotidienne de la base de données
- Mise à jour des dépendances Python
- Monitoring des performances

### **Évolutions prévues**
- Ajout de nouveaux modèles ML
- Interface d'administration
- API pour applications mobiles
- Intégration de nouvelles sources de données

---

**Version** : 1.0  
**Dernière mise à jour** : 2024  
**Auteur** : Kevin  
**Contact** : [email] 