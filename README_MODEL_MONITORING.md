# 🤖 Monitoring du Modèle IA - Guide d'utilisation

## 📊 Nouveau Dashboard Grafana pour le Modèle IA

### 🎯 Métriques disponibles

#### **1. Performance du modèle :**
- `model_inference_time_seconds` → Temps d'inférence du modèle
- `model_prediction_accuracy` → Précision moyenne
- `model_prediction_mae` → Mean Absolute Error

#### **2. Drift des features :**
- `feature_drift_budget` → Drift de la feature budget (%)
- `feature_drift_duree` → Drift de la feature durée (%)
- `feature_drift_genre` → Distribution des genres

#### **3. Qualité des prédictions :**
- `prediction_outliers_total` → Nombre de prédictions aberrantes
- `prediction_range` → Distribution des prédictions
- `prediction_volatility` → Volatilité des prédictions (%)

#### **4. Santé du modèle :**
- `model_health_score` → Score de santé (0-100)
- `model_version` → Version du modèle déployé

## 🚀 Installation et Configuration

### 1. Redémarrer l'API avec les nouvelles métriques
```bash
docker-compose restart cinapps-api
```

### 2. Vérifier que les métriques sont disponibles
```bash
curl http://localhost:8002/metrics | grep model
```

### 3. Importer le dashboard dans Grafana

1. **Ouvrir Grafana** : http://localhost:3000
2. **Aller dans** : Dashboards → Import
3. **Cliquer sur** : "Upload JSON file"
4. **Sélectionner** : `monitoring/grafana-model-dashboard.json`
5. **Cliquer sur** : "Import"

## 📈 Génération de données de test

### Utiliser le script automatique
```bash
python generate_model_metrics.py
```

**Ce script va :**
- ✅ Générer 50 prédictions avec différents scénarios de drift
- ✅ Tester différents types de données (budget élevé, durée longue, genres inhabituels)
- ✅ Créer des métriques variées pour le dashboard

### Scénarios de test inclus :
- **Normal** : Données standard (peu de drift)
- **High Budget** : Budgets élevés (drift du budget)
- **Long Duration** : Durées longues (drift de la durée)
- **Unusual Genre** : Genres inhabituels (drift des genres)

## 📊 Panels du Dashboard

### 1. **Score de santé du modèle** (Stat)
- Affiche le score global de santé (0-100)
- Couleurs : Rouge (0-50), Orange (50-70), Jaune (70-90), Vert (90-100)

### 2. **Temps d'inférence du modèle (p95)** (Graph)
- Temps d'inférence au 95ème percentile
- Mesure la performance du modèle

### 3. **Drift des features - Budget** (Graph)
- Écart du budget par rapport aux données d'entraînement
- Seuils : Vert (0-20%), Jaune (20-50%), Orange (50-100%), Rouge (>100%)

### 4. **Drift des features - Durée** (Graph)
- Écart de la durée par rapport aux données d'entraînement
- Mêmes seuils que le budget

### 5. **Distribution des genres** (Pie Chart)
- Répartition des genres dans les prédictions récentes
- Détecte les changements de distribution

### 6. **Volatilité des prédictions** (Graph)
- Stabilité des prédictions dans le temps
- Seuils : Vert (0-30%), Jaune (30-50%), Orange (50-100%), Rouge (>100%)

### 7. **Prédictions aberrantes** (Stat)
- Nombre total de prédictions considérées comme outliers
- Seuils : Vert (0), Jaune (1-5), Orange (6-10), Rouge (>10)

### 8. **Distribution des prédictions** (Histogram)
- Histogramme des valeurs de prédiction
- Aide à détecter les anomalies

### 9. **Temps d'inférence moyen** (Graph)
- Temps d'inférence moyen sur 5 minutes
- Tendance de performance

### 10. **Version du modèle** (Stat)
- Version actuelle du modèle déployé

## 🔍 Interprétation des métriques

### **Score de santé élevé (>90)**
- ✅ Modèle performant
- ✅ Peu d'outliers
- ✅ Faible volatilité
- ✅ Drift minimal

### **Score de santé moyen (70-90)**
- ⚠️ Surveillance recommandée
- ⚠️ Quelques anomalies détectées

### **Score de santé faible (<70)**
- ❌ Action requise
- ❌ Drift important détecté
- ❌ Trop d'outliers
- ❌ Volatilité élevée

## 🛠️ Maintenance

### Mettre à jour les statistiques de référence
Dans `API_s/main.py`, modifier `REFERENCE_STATS` :
```python
REFERENCE_STATS = {
    'budget': {'mean': 50000000, 'std': 30000000},
    'duree': {'mean': 120, 'std': 30},
    'genre_dist': {'Action': 0.3, 'Comédie': 0.25, 'Drame': 0.2, 'Thriller': 0.15, 'Autre': 0.1}
}
```

### Ajuster les seuils d'alerte
Modifier les seuils dans les fonctions :
- `calculate_health_score()` : Seuils pour le score de santé
- `update_model_metrics()` : Seuils pour les outliers

## 📞 Support

En cas de problème :
1. Vérifier que l'API fonctionne : `curl http://localhost:8002/health`
2. Vérifier les métriques : `curl http://localhost:8002/metrics`
3. Vérifier Prometheus : http://localhost:9090
4. Vérifier Grafana : http://localhost:3000

---

**🎯 Votre modèle IA est maintenant entièrement monitoré !** 🚀
