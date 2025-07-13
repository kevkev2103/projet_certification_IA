# Cinapps - Projet de Prédiction d'Entrées Cinéma

## 📋 Présentation du projet

### 🎯 **Contexte et objectifs**

**Cinapps** est une application de prédiction d'entrées en salle de cinéma utilisant l'intelligence artificielle. Le projet vise à analyser les données de films (budget, casting, genre, etc.) pour prédire leur performance au box-office.

### 👥 **Acteurs du projet**
- **Développeur principal** : Kevin
- **Utilisateurs finaux** : Professionnels du cinéma, distributeurs, producteurs
- **Stakeholders** : Studios de production, salles de cinéma

### 🎬 **Objectifs fonctionnels**
1. **Collecte automatisée** de données de films depuis IMDB
2. **Prédiction d'entrées** basée sur un modèle ML
3. **Interface utilisateur** pour visualiser les prédictions
4. **API sécurisée** pour l'intégration avec d'autres systèmes
5. **Dashboard** de monitoring des performances

### 🔧 **Objectifs techniques**
- Architecture microservices avec FastAPI
- Base de données MySQL pour le stockage
- Modèle ML CatBoost pour les prédictions
- Interface Streamlit pour la visualisation
- Authentification JWT sécurisée
- Pipeline de données automatisé

### 💰 **Budget et contraintes**
- **Budget** : Développement en open source
- **Contraintes techniques** : Compatibilité Linux/WSL2
- **Contraintes de temps** : Projet de certification

### 📅 **Organisation du travail et planification**

#### **Phase 1 : Infrastructure (Terminée)**
- ✅ Configuration Docker et base de données
- ✅ API CRUD avec authentification
- ✅ API de prédiction ML

#### **Phase 2 : Collecte de données (En cours)**
- ✅ Scraping IMDB avec Scrapy
- 🔄 Pipeline d'agrégation des données
- ⏳ Tests et validation

#### **Phase 3 : Interface et monitoring (En cours)**
- ✅ Interface Streamlit
- 🔄 Dashboard de monitoring
- ⏳ Tests d'intégration

#### **Phase 4 : Documentation et déploiement (À faire)**
- ⏳ Documentation complète
- ⏳ Tests automatisés
- ⏳ CI/CD pipeline

### 🌍 **Environnements**
- **Développement** : WSL2 Ubuntu 24.04
- **Base de données** : MySQL 8.0 (Docker)
- **APIs** : FastAPI sur ports 8000 et 8001
- **Interface** : Streamlit sur port 8501

### 🔒 **Contraintes d'accessibilité**
- Interface web responsive
- Support des standards WCAG
- Documentation accessible

## 🏗️ **Architecture technique**

### **Technologies utilisées**
- **Backend** : FastAPI, Python 3.10+
- **Base de données** : MySQL 8.0
- **ML** : CatBoost, Pandas, NumPy
- **Frontend** : Streamlit
- **Scraping** : Scrapy
- **Authentification** : JWT
- **Containerisation** : Docker

### **Services externes**
- **IMDB** : Source de données de films
- **GitHub** : Versioning du code

### **Exigences de programmation**
- Python 3.10+
- Gestion des erreurs robuste
- Logging détaillé
- Tests unitaires et d'intégration
- Documentation OpenAPI

### **Accessibilité**
- Disponibilité 24/7 (en développement)
- Accès via interface web
- API REST standardisée
- Documentation technique complète 