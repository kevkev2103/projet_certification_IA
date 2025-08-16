# Documentation E5 - Monitoring & Débogage (C20/C21)

## 📋 Table des matières
1. [Introduction](#introduction)
2. [Architecture du monitoring](#architecture-du-monitoring)
3. [Installation et configuration](#installation-et-configuration)
4. [Métriques surveillées](#métriques-surveillées)
5. [Alertes configurées](#alertes-configurées)
6. [Procédure de débogage](#procédure-de-débogage)
7. [Résolution d'incidents](#résolution-dincidents)
8. [Commandes utiles](#commandes-utiles)

---

## 🎯 Introduction

Cette documentation explique comment surveiller et déboguer l'application Cinapps. Le monitoring nous permet de voir en temps réel si l'application fonctionne bien, et le débogage nous aide à résoudre les problèmes quand ils surviennent.

### 🛠️ Outils utilisés
- **Prometheus** : Collecte les métriques (comme un compteur qui mesure tout)
- **Grafana** : Affiche les graphiques et tableaux de bord
- **FastAPI Instrumentator** : Ajoute automatiquement des métriques à notre API
- **Logging Python** : Enregistre les événements et erreurs

---

## 🏗️ Architecture du monitoring

### Schéma simplifié
```
[API Cinapps] → [Prometheus] → [Grafana]
     ↓              ↓            ↓
  Métriques    Collecte      Visualisation
  + Logs      données       + Alertes
```

### Fichiers de configuration
- `monitoring/prometheus.yml` : Configuration de Prometheus
- `monitoring/alert_rules.yml` : Règles d'alertes
- `monitoring/grafana-dashboard.json` : Tableau de bord Grafana
- `docker-compose.yml` : Lancement des services

---

## 🚀 Installation et configuration

### 1. Prérequis
- Docker et Docker Compose installés
- Ports 9090 et 3000 disponibles

### 2. Lancer le monitoring
```bash
# Depuis la racine du projet
cd monitoring
docker-compose up -d
```

### 3. Accéder aux interfaces
- **Prometheus** : http://localhost:9090
- **Grafana** : http://localhost:3000
  - Utilisateur : `admin`
  - Mot de passe : `admin123`

### 4. Configurer Grafana
1. Aller sur http://localhost:3000
2. Se connecter avec admin/admin123
3. Aller dans "Connections" → "Data sources"
4. Ajouter Prometheus avec l'URL : `http://prometheus:9090`
5. Tester la connexion

---

## 📊 Métriques surveillées

### Métriques automatiques (FastAPI)
Ces métriques sont générées automatiquement par FastAPI :

```python
# Dans cinapps_api/app/main.py
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
```

**Métriques disponibles :**
- `http_requests_total` : Nombre total de requêtes
- `http_request_duration_seconds` : Temps de réponse des requêtes
- `http_requests_total{status="4xx"}` : Erreurs 4xx (client)
- `http_requests_total{status="5xx"}` : Erreurs 5xx (serveur)

### Métriques personnalisées (Prédictions)
Ces métriques sont créées spécifiquement pour notre modèle IA :

```python
# Dans cinapps_api/app/routes/pred.py
from prometheus_client import Counter, Histogram, Gauge

# Compteur total de prédictions
predictions_counter = Counter('predictions_total', 'Total number of predictions made')

# Temps de traitement des prédictions
prediction_duration = Histogram('prediction_duration_seconds', 'Time spent making predictions')

# Prédictions par minute
predictions_per_minute = Gauge('predictions_per_minute', 'Predictions per minute')
```

**Utilisation dans le code :**
```python
@router.post("/prediction/")
async def predict(features: PredictionRequest, current_user: dict = Depends(get_current_user)): 
    start_time = time.time()
    
    try:
        # ... logique de prédiction ...
        
        # Incrémenter les métriques
        predictions_counter.inc()
        predictions_per_minute.inc()
        
        return {"prediction": prediction_value}
    
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Mesurer la durée
        duration = time.time() - start_time
        prediction_duration.observe(duration)
```

---

## 🚨 Alertes configurées

### Règles d'alertes (monitoring/alert_rules.yml)

#### 1. Alerte latence élevée
```yaml
- alert: HighLatency
  expr: histogram_quantile(0.95, rate(http_request_duration_highr_seconds_bucket[5m])) > 0.5
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "Latence élevée détectée"
    description: "La latence p95 est supérieure à 500ms depuis 2 minutes"
```
**Signification :** Si les requêtes prennent plus de 500ms pendant 2 minutes → Alerte

#### 2. Alerte taux d'erreurs élevé
```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"4..|5.."}[5m]) / rate(http_requests_total[5m]) > 0.02
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "Taux d'erreurs élevé"
    description: "Le taux d'erreurs est supérieur à 2% depuis 2 minutes"
```
**Signification :** Si plus de 2% des requêtes échouent pendant 2 minutes → Alerte

#### 3. Alerte API indisponible
```yaml
- alert: APIDown
  expr: up{job="cinapps-api"} == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "API Cinapps indisponible"
    description: "L'API Cinapps ne répond plus depuis 1 minute"
```
**Signification :** Si l'API ne répond plus pendant 1 minute → Alerte critique

#### 4. Alerte prédictions lentes
```yaml
- alert: SlowPredictions
  expr: histogram_quantile(0.95, rate(prediction_duration_seconds_bucket[5m])) > 1.0
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "Prédictions lentes"
    description: "Les prédictions prennent plus de 1 seconde (p95)"
```
**Signification :** Si les prédictions prennent plus de 1 seconde pendant 2 minutes → Alerte

---

## 🔍 Procédure de débogage

### 1. Système de logging

#### Configuration du logging
```python
# Dans chaque fichier Python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

#### Niveaux de log
- `logger.info()` : Informations générales
- `logger.warning()` : Avertissements
- `logger.error()` : Erreurs
- `logger.debug()` : Informations détaillées (débogage)

#### Exemple d'utilisation
```python
try:
    # Charger le modèle ML
    model_pipeline, preprocessor = load_model()
    logger.info("Modèle et preprocessor chargés avec succès")
except Exception as e:
    logger.error(f"Erreur lors du chargement du modèle : {str(e)}")
    raise RuntimeError("Impossible de charger le modèle")
```

### 2. Gestion d'erreurs

#### Structure try-catch
```python
@router.post("/prediction/")
async def predict(features: PredictionRequest, current_user: dict = Depends(get_current_user)): 
    start_time = time.time()
    
    try:
        # Code principal
        prediction = model_pipeline.predict(df)
        logger.info(f"Prédiction réussie pour film ID {features.id_film}")
        
    except Exception as e:
        # Gestion d'erreur
        logger.error(f"Erreur lors de la prédiction : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Code toujours exécuté (métriques)
        duration = time.time() - start_time
        prediction_duration.observe(duration)
```

### 3. Endpoints de diagnostic

#### Health check
```python
@app.get("/health", tags=["Root"])
async def health_check():
    """Endpoint de health check pour Docker"""
    return {"status": "healthy", "service": "cinapps-api"}
```

#### Endpoint de test
```python
@app.post("/test/setup-user", tags=["Test"])
async def setup_test_user():
    """Endpoint pour créer l'utilisateur de test en CI"""
    if os.getenv('GITHUB_ACTIONS'):
        try:
            # Créer un utilisateur de test
            # ... code de création ...
            return {"message": "Utilisateur testuser créé avec succès", "status": "success"}
        except Exception as e:
            return {"message": f"Erreur création utilisateur: {str(e)}", "status": "error"}
```

---

## 🛠️ Résolution d'incidents

### Étapes de résolution

#### 1. Détecter l'incident
- Vérifier les alertes dans Grafana
- Consulter les logs de l'application
- Vérifier les métriques Prometheus

#### 2. Identifier la cause
```bash
# Voir les logs de l'API
docker logs cinapps-api

# Voir les logs de Prometheus
docker logs prometheus

# Voir les logs de Grafana
docker logs grafana
```

#### 3. Reproduire le problème
- Utiliser l'endpoint `/test/setup-user` pour créer un environnement de test
- Reproduire les conditions d'erreur
- Vérifier les paramètres de la requête

#### 4. Corriger le problème
- Modifier le code
- Ajouter des logs pour le débogage
- Tester la correction

#### 5. Déployer la correction
```bash
# Via Git (recommandé)
git add .
git commit -m "Fix: correction du problème X"
git push origin main

# Ou redémarrer les services
docker-compose restart cinapps-api
```

#### 6. Valider la correction
- Vérifier que les métriques reviennent à la normale
- Confirmer que les alertes se désactivent
- Tester la fonctionnalité corrigée

---

## 💻 Commandes utiles

### Monitoring
```bash
# Lancer le monitoring
cd monitoring
docker-compose up -d

# Voir les logs du monitoring
docker-compose logs -f

# Arrêter le monitoring
docker-compose down

# Redémarrer un service
docker-compose restart prometheus
```

### Application
```bash
# Lancer toute l'application
docker-compose up -d

# Voir les logs de l'API
docker logs cinapps-api

# Voir les logs en temps réel
docker logs -f cinapps-api

# Redémarrer l'API
docker-compose restart cinapps-api
```

### Base de données
```bash
# Voir les logs MySQL
docker logs cinapps-mysql

# Se connecter à MySQL
docker exec -it cinapps-mysql mysql -u kevin -pkevinpass cinapps

# Vérifier les tables
SHOW TABLES;
```

### Tests
```bash
# Lancer les tests
pytest -v

# Tests avec coverage
pytest --cov=tests --cov-report=term-missing

# Tests spécifiques
pytest tests/test_api.py -v
```

### Débogage
```bash
# Voir les métriques Prometheus
curl http://localhost:9090/metrics

# Voir les métriques de l'API
curl http://localhost:8000/metrics

# Test de santé de l'API
curl http://localhost:8000/health

# Test d'authentification
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=test123"
```

---

## 📚 Ressources supplémentaires

### Documentation officielle
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Prometheus FastAPI Instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator)

### Fichiers de configuration
- `monitoring/prometheus.yml` : Configuration Prometheus
- `monitoring/alert_rules.yml` : Règles d'alertes
- `monitoring/grafana-dashboard.json` : Dashboard Grafana
- `docker-compose.yml` : Services Docker

### Logs importants
- Logs API : `docker logs cinapps-api`
- Logs Prometheus : `docker logs prometheus`
- Logs Grafana : `docker logs grafana`
- Logs MySQL : `docker logs cinapps-mysql`

---

## ✅ Checklist de vérification

### Monitoring
- [ ] Prometheus accessible sur http://localhost:9090
- [ ] Grafana accessible sur http://localhost:3000
- [ ] Métriques de l'API visibles dans Prometheus
- [ ] Dashboard Grafana configuré
- [ ] Alertes configurées et actives

### Débogage
- [ ] Logs configurés dans tous les fichiers Python
- [ ] Gestion d'erreurs avec try-catch
- [ ] Endpoint `/health` fonctionnel
- [ ] Endpoint `/test/setup-user` disponible
- [ ] Métriques personnalisées implémentées

### Tests
- [ ] Tests unitaires passent
- [ ] Tests d'intégration fonctionnels
- [ ] Pipeline CI/CD configuré
- [ ] Déploiement automatique actif

---

*Documentation créée pour le projet Cinapps - Monitoring & Débogage (E5)*
