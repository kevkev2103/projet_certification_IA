# Tests CinApps

## 📋 Vue d'ensemble

Ce dossier contient tous les tests automatisés pour le projet CinApps, organisés pour valider les compétences **C18** (CI) et **C19** (CD) de la certification.

## 🧪 Structure des Tests

### **Types de Tests**

| Fichier | Description | Scope |
|---------|-------------|-------|
| `test_api_crud.py` | Tests de l'API CRUD | Endpoints, authentification, documentation |
| `test_prediction_pipeline.py` | Tests du pipeline ML | Configuration, données, logique métier |
| `test_streamlit.py` | Tests de l'interface | Configuration, accessibilité, fichiers |
| `test_docker_setup.py` | Tests infrastructure | Docker, structure projet, YAML |

### **Couverture des Tests**

- ✅ **Tests unitaires** : Fonctions individuelles
- ✅ **Tests d'intégration** : Communication entre services
- ✅ **Tests de configuration** : Variables d'environnement, fichiers
- ✅ **Tests d'infrastructure** : Docker, structure du projet

## 🚀 Exécution des Tests

### **Localement**

```bash
# Installation des dépendances
pip install -r tests/requirements.txt

# Exécution de tous les tests
cd tests
python -m pytest -v

# Tests spécifiques
python -m pytest test_api_crud.py -v
python -m pytest test_docker_setup.py -v

# Avec couverture
python -m pytest --cov=../ --cov-report=html
```

### **Avec Docker**

```bash
# Démarrer les services nécessaires
docker-compose up -d mysql cinapps-api

# Attendre que les services soient prêts
sleep 10

# Exécuter les tests
cd tests
python -m pytest test_api_crud.py -v
```

### **En CI/CD**

Les tests sont automatiquement exécutés par GitHub Actions :
- ✅ **Sur chaque push** vers `main` et `develop`
- ✅ **Sur chaque pull request** vers `main`
- ✅ **Avec environnement MySQL** configuré automatiquement

## 📊 Rapports et Métriques

### **Couverture de Code**

```bash
# Générer le rapport de couverture
python -m pytest --cov=../ --cov-report=html --cov-report=term

# Voir le rapport
# Le rapport HTML est disponible dans htmlcov/index.html
```

### **Formats de Sortie**

- **Console** : Résultats en temps réel
- **HTML** : Rapport détaillé de couverture
- **XML** : Pour intégration CI/CD
- **JSON** : Pour analyse programmatique

## 🔧 Configuration

### **Variables d'Environnement de Test**

```bash
# Pour les tests locaux
export MYSQL_HOST=localhost
export MYSQL_USER=kevin
export MYSQL_PASSWORD=kevinpass
export MYSQL_DATABASE=cinapps
export API_URL_CRUD=http://localhost:8000
export STREAMLIT_URL=http://localhost:8501
```

### **Dépendances de Test**

```python
# requirements.txt
pytest==7.4.3          # Framework de test
pytest-cov==4.1.0      # Couverture de code
requests==2.31.0       # Tests API
python-dotenv==1.0.0   # Variables d'environnement
PyYAML==6.0.1          # Tests configuration
coverage==7.3.2        # Métriques de couverture
```

## 🧪 Détail des Tests

### **test_api_crud.py**

```python
# Tests inclus :
- test_health_endpoint()           # Endpoint de santé
- test_root_endpoint()             # Endpoint racine
- test_auth_token_endpoint_exists() # Authentification
- test_docs_endpoint()             # Documentation Swagger
- test_valid_credentials()         # Login valide
- test_invalid_credentials()       # Login invalide
```

### **test_prediction_pipeline.py**

```python
# Tests inclus :
- test_database_config_structure()     # Configuration DB
- test_api_urls_configuration()        # URLs API
- test_authenticate_and_get_token_success() # Auth pipeline
- test_data_preparation_structure()    # Structure données
- test_environment_variables()         # Variables env
```

### **test_streamlit.py**

```python
# Tests inclus :
- test_streamlit_health_check()        # Health check Streamlit
- test_streamlit_app_accessible()      # Accessibilité app
- test_environment_variables_for_streamlit() # Variables env
- test_streamlit_files_exist()         # Fichiers requis
- test_acteurs_coef_file_exists()      # Fichier acteurs
```

### **test_docker_setup.py**

```python
# Tests inclus :
- test_docker_compose_file_exists()    # Fichier compose
- test_docker_compose_is_valid_yaml()  # YAML valide
- test_dockerfiles_exist()             # Tous les Dockerfiles
- test_requirements_files_exist()      # Fichiers requirements
- test_docker_compose_services()       # Services définis
- test_main_directories_exist()        # Structure projet
- test_git_repository_initialized()    # Dépôt Git
- test_env_example_exists()            # Fichier .env
```

## 🚨 Gestion des Erreurs

### **Tests qui Peuvent Échouer en CI**

Certains tests sont marqués avec `pytest.skip()` quand les services ne sont pas disponibles :

```python
try:
    response = requests.get(f"{STREAMLIT_URL}/_stcore/health")
    assert response.status_code == 200
except requests.exceptions.RequestException:
    pytest.skip("Streamlit non accessible (normal en CI)")
```

### **Debugging des Tests**

```bash
# Mode verbose avec stack trace complète
python -m pytest -v --tb=long

# Arrêter au premier échec
python -m pytest -x

# Exécuter seulement les tests qui ont échoué
python -m pytest --lf

# Mode debug avec pdb
python -m pytest --pdb
```

## 📈 Métriques de Qualité

### **Objectifs de Couverture**

- **Couverture globale** : > 70%
- **Tests critiques** : 100% (authentification, santé)
- **Infrastructure** : 100% (Docker, configuration)

### **Critères de Succès**

- ✅ Tous les tests passent en CI
- ✅ Aucune régression détectée
- ✅ Couverture maintenue ou améliorée
- ✅ Temps d'exécution < 5 minutes

## 🔄 Workflow de Développement

### **Avant de Commiter**

```bash
# 1. Exécuter les tests localement
cd tests
python -m pytest -v

# 2. Vérifier la couverture
python -m pytest --cov=../ --cov-report=term

# 3. Si tous les tests passent → commit
git add . && git commit -m "feat: nouvelle fonctionnalité"
```

### **Ajout de Nouveaux Tests**

1. **Créer le test** dans le fichier approprié
2. **Suivre la convention** de nommage `test_*`
3. **Inclure la documentation** des cas testés
4. **Vérifier** que le test échoue avant implémentation
5. **Implémenter** la fonctionnalité
6. **Vérifier** que le test passe

## 📚 Ressources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Plugin](https://pytest-cov.readthedocs.io/)
- [Requests Testing](https://docs.python-requests.org/en/latest/)
- [Docker Testing Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**🎯 Ces tests garantissent la qualité et la fiabilité du projet CinApps !**