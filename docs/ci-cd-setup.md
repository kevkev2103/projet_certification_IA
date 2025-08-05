# Documentation CI/CD - CinApps

## 📋 Vue d'ensemble

Cette documentation couvre la mise en place du CI/CD (Continuous Integration / Continuous Deployment) pour le projet CinApps, utilisant **GitHub Actions** comme plateforme d'automatisation.

## 🎯 Objectifs de Certification

### **C18 - Automatiser les tests du code source (CI)**
- ✅ Documentation des outils, étapes et déclencheurs
- ✅ Intégration des étapes de build et configuration
- ✅ Exécution automatique des tests
- ✅ Configurations versionnées sur Git

### **C19 - Créer un processus de livraison continue (CD)**
- ✅ Documentation des étapes et déclencheurs CD
- ✅ Packaging avec Docker
- ✅ Livraison via pull requests
- ✅ Configurations versionnées

## 🔧 Architecture CI/CD

### **Structure des Workflows**

```
.github/workflows/
├── ci.yml          # Continuous Integration (tests, qualité)
├── cd.yml          # Continuous Deployment (build, déploiement)
└── security.yml    # Analyse de sécurité
```

### **Structure des Tests**

```
tests/
├── __init__.py
├── requirements.txt
├── test_api_crud.py          # Tests de l'API CRUD
├── test_prediction_pipeline.py  # Tests du pipeline ML
├── test_streamlit.py         # Tests de l'interface
└── test_docker_setup.py     # Tests de configuration Docker
```

## 🚀 Continuous Integration (CI)

### **Déclencheurs**
- **Push** sur les branches `main` et `develop`
- **Pull Requests** vers `main`

### **Jobs Exécutés**

#### **1. Job `test`**
- **Environnement** : Ubuntu Latest avec Python 3.10.12
- **Services** : MySQL 8.0 pour les tests d'intégration
- **Étapes** :
  1. Checkout du code
  2. Configuration Python et cache des dépendances
  3. Installation des dépendances de test
  4. Configuration des variables d'environnement
  5. Attente de la disponibilité de MySQL
  6. Exécution des tests par catégorie :
     - Tests de structure du projet
     - Tests du pipeline de prédiction
     - Tests de l'API CRUD (avec API démarrée)
     - Tests de configuration Streamlit
  7. Génération du rapport de couverture de code
  8. Upload des artefacts de couverture

#### **2. Job `lint`**
- **Outils utilisés** :
  - **Black** : Formatage du code Python
  - **isort** : Tri des imports
  - **flake8** : Analyse statique du code
- **Mode** : Continue-on-error (n'interrompt pas le build)

### **Variables d'Environnement CI**
```yaml
MYSQL_HOST: localhost
MYSQL_USER: kevin
MYSQL_PASSWORD: kevinpass
MYSQL_DATABASE: cinapps
API_URL_CRUD: http://localhost:8000
API_URL_PREDICTION: http://localhost:8000
STREAMLIT_URL: http://localhost:8501
```

## 📦 Continuous Deployment (CD)

### **Déclencheurs**
- **Push** sur la branche `main`
- **Tags** commençant par `v*`
- **Succès du workflow CI** sur `main`

### **Jobs Exécutés**

#### **1. Job `build-and-push`**
- **Stratégie Matrix** : Build parallèle de tous les services
- **Services construits** :
  - `cinapps-api` (API CRUD)
  - `prediction-api` (API de prédiction)
  - `streamlit-app` (Interface utilisateur)
  - `scraper-service` (Service de scraping)
  - `prediction-pipeline` (Pipeline ML)
- **Registry** : GitHub Container Registry (ghcr.io)
- **Tags automatiques** :
  - `latest` pour la branche main
  - Nom de branche pour les autres branches
  - Version sémantique pour les tags

#### **2. Job `deploy-staging`**
- **Condition** : Uniquement sur `main` après build réussi
- **Environnement** : staging
- **Actions** :
  1. Mise à jour du `docker-compose.yml` avec les images du registry
  2. Upload des artefacts de déploiement
  3. Simulation de déploiement (remplaçable par déploiement réel)

#### **3. Job `integration-tests`**
- **Tests post-déploiement** :
  - Vérification que les images se lancent
  - Test des endpoints de santé
  - Validation de la connectivité base de données

## 🔒 Analyse de Sécurité

### **Déclencheurs**
- **Push** sur `main` et `develop`
- **Pull Requests** vers `main`
- **Programmé** : Chaque dimanche à 2h (scan hebdomadaire)

### **Jobs de Sécurité**

#### **1. `dependency-check`**
- **Outil** : Safety (Python)
- **Scope** : Toutes les dépendances Python
- **Output** : Rapports JSON des vulnérabilités

#### **2. `docker-security`**
- **Outil** : Trivy (Aqua Security)
- **Scope** : Images Docker
- **Output** : Rapports SARIF intégrés à GitHub Security

#### **3. `secrets-scan`**
- **Outil** : GitLeaks
- **Scope** : Détection de secrets dans le code

#### **4. `docker-bench`**
- **Vérifications** :
  - Bonnes pratiques Dockerfile
  - Présence de HEALTHCHECK
  - Nettoyage des caches
  - Utilisation d'utilisateur non-root

#### **5. `owasp-zap`**
- **Outil** : OWASP ZAP
- **Scope** : Scan de sécurité web de l'API
- **Condition** : Uniquement sur push vers `main`

## 🛠️ Configuration et Utilisation

### **Prérequis**
1. **Dépôt GitHub** avec permissions Actions activées
2. **Secrets GitHub** configurés si nécessaire
3. **GitHub Container Registry** activé

### **Installation**
```bash
# Les workflows sont automatiquement détectés par GitHub
# Aucune installation manuelle requise
```

### **Exécution Manuelle**
```bash
# Via l'interface GitHub Actions :
# 1. Aller dans l'onglet "Actions"
# 2. Sélectionner le workflow souhaité
# 3. Cliquer sur "Run workflow"
```

### **Monitoring**
- **Interface GitHub** : Onglet "Actions" pour voir les exécutions
- **Notifications** : Emails automatiques en cas d'échec
- **Badges** : Ajoutables au README pour montrer le statut

## 📊 Métriques et Rapports

### **Couverture de Code**
- **Outil** : pytest-cov
- **Format** : HTML et XML
- **Artefacts** : Disponibles dans les runs GitHub Actions

### **Rapports de Sécurité**
- **Localisation** : GitHub Security tab
- **Formats** : SARIF, JSON
- **Fréquence** : Chaque push + scan hebdomadaire

### **Build Artifacts**
- **Logs de build** conservés 90 jours
- **Images Docker** versionnées dans le registry
- **Rapports de test** disponibles en téléchargement

## 🔄 Workflow de Développement

### **Développement Standard**
1. **Créer une branche** depuis `develop`
2. **Développer** et commiter les changements
3. **Push** → Déclenchement automatique du CI
4. **Créer une PR** vers `main`
5. **CI validé** → Merge possible
6. **Merge vers main** → Déclenchement CD automatique

### **Hotfix**
1. **Branche directe** depuis `main`
2. **Fix rapide** et push
3. **CI/CD automatique** pour déploiement urgent

## 🚨 Résolution des Problèmes

### **Échecs CI Courants**
```bash
# Tests échoués
- Vérifier les logs détaillés dans GitHub Actions
- Reproduire localement : pytest tests/

# Problèmes de dépendances
- Vérifier les requirements.txt
- Tester localement : pip install -r tests/requirements.txt

# Problèmes de base de données
- Vérifier la configuration MySQL dans le CI
- S'assurer que les migrations sont compatibles
```

### **Échecs CD Courants**
```bash
# Build Docker échoué
- Vérifier les Dockerfiles
- Tester localement : docker build -t test .

# Registry non accessible
- Vérifier les permissions GitHub
- Vérifier les secrets configurés
```

## 📈 Évolutions Futures

### **Améliorations Possibles**
- **Tests de performance** automatisés
- **Déploiement multi-environnements** (dev, staging, prod)
- **Rollback automatique** en cas d'échec
- **Notifications Slack/Teams** pour l'équipe
- **Analyse de qualité** avec SonarQube

### **Optimisations**
- **Cache Docker layers** pour des builds plus rapides
- **Tests parallèles** pour réduire le temps d'exécution
- **Déploiement conditionnel** basé sur les changements

## 📚 Ressources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [pytest Documentation](https://docs.pytest.org/)

---

**🎯 Cette configuration répond parfaitement aux exigences C18 et C19 de la certification !**