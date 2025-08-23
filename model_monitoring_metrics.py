#!/usr/bin/env python3
"""
Exemple de métriques pour monitorer le modèle IA
À intégrer dans votre API_s/main.py
"""

from prometheus_client import Counter, Histogram, Gauge, Summary
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
import time

# ===== MÉTRIQUES POUR LE MODÈLE IA =====

# Métriques de performance
model_prediction_accuracy = Gauge('model_prediction_accuracy', 'Précision moyenne du modèle')
model_prediction_mae = Gauge('model_prediction_mae', 'Mean Absolute Error du modèle')
model_prediction_rmse = Gauge('model_prediction_rmse', 'Root Mean Square Error du modèle')

# Métriques de drift
feature_drift_budget = Gauge('feature_drift_budget', 'Drift de la feature budget')
feature_drift_duree = Gauge('feature_drift_duree', 'Drift de la feature durée')
feature_drift_genre = Counter('feature_drift_genre', 'Distribution des genres', ['genre'])

# Métriques de performance système
model_inference_time = Histogram('model_inference_time_seconds', 'Temps d\'inférence du modèle')
model_memory_usage = Gauge('model_memory_usage_mb', 'Utilisation mémoire du modèle (MB)')
model_cpu_usage = Gauge('model_cpu_usage_percent', 'Utilisation CPU du modèle (%)')

# Métriques de qualité des prédictions
prediction_outliers = Counter('prediction_outliers_total', 'Nombre de prédictions aberrantes')
prediction_range = Summary('prediction_range', 'Distribution des prédictions')

# Métriques de santé du modèle
model_health_score = Gauge('model_health_score', 'Score de santé du modèle (0-100)')
model_version = Gauge('model_version', 'Version du modèle déployé', ['version'])

class ModelMonitor:
    def __init__(self, model_pipeline, reference_data=None):
        self.model = model_pipeline
        self.reference_data = reference_data
        self.prediction_history = []
        self.feature_history = []
        
    def calculate_drift(self, current_features):
        """Calculer le drift des features"""
        if self.reference_data is None:
            return {}
        
        drift_metrics = {}
        
        # Exemple pour le budget
        ref_budget_mean = self.reference_data['budget'].mean()
        current_budget_mean = np.mean([f['budget'] for f in current_features])
        drift_metrics['budget'] = abs(current_budget_mean - ref_budget_mean) / ref_budget_mean
        
        # Exemple pour la durée
        ref_duree_mean = self.reference_data['duree'].mean()
        current_duree_mean = np.mean([f['duree'] for f in current_features])
        drift_metrics['duree'] = abs(current_duree_mean - ref_duree_mean) / ref_duree_mean
        
        return drift_metrics
    
    def update_metrics(self, features, prediction, actual_value=None):
        """Mettre à jour toutes les métriques"""
        start_time = time.time()
        
        # Temps d'inférence
        inference_time = time.time() - start_time
        model_inference_time.observe(inference_time)
        
        # Drift des features
        drift = self.calculate_drift([features])
        if 'budget' in drift:
            feature_drift_budget.set(drift['budget'])
        if 'duree' in drift:
            feature_drift_duree.set(drift['duree'])
        
        # Distribution des genres
        genre = features.get('genre', 'unknown')
        feature_drift_genre.labels(genre=genre).inc()
        
        # Qualité des prédictions
        prediction_range.observe(prediction)
        
        # Détection d'outliers (exemple simple)
        if prediction > 1000000000:  # Plus d'1 milliard d'entrées
            prediction_outliers.inc()
        
        # Historique pour calculs de performance
        self.prediction_history.append(prediction)
        self.feature_history.append(features)
        
        # Calculer la précision si on a la vraie valeur
        if actual_value is not None:
            mae = mean_absolute_error([actual_value], [prediction])
            rmse = np.sqrt(mean_squared_error([actual_value], [prediction]))
            
            model_prediction_mae.set(mae)
            model_prediction_rmse.set(rmse)
        
        # Score de santé du modèle (exemple)
        health_score = self.calculate_health_score()
        model_health_score.set(health_score)
    
    def calculate_health_score(self):
        """Calculer un score de santé du modèle"""
        score = 100
        
        # Réduire le score si trop d'outliers
        if len(self.prediction_history) > 10:
            recent_predictions = self.prediction_history[-10:]
            outlier_ratio = sum(1 for p in recent_predictions if p > 1000000000) / len(recent_predictions)
            score -= outlier_ratio * 30
        
        # Réduire le score si drift élevé
        if hasattr(self, 'feature_drift_budget'):
            drift = self.feature_drift_budget._value.get()
            if drift > 0.5:  # 50% de drift
                score -= 20
        
        return max(0, score)

# Exemple d'utilisation dans votre API
def monitor_prediction(features, prediction, actual_value=None):
    """Fonction à appeler dans votre endpoint de prédiction"""
    # Initialiser le moniteur (à faire une seule fois)
    if not hasattr(monitor_prediction, 'monitor'):
        # Charger vos données de référence
        reference_data = None  # Charger vos données d'entraînement
        monitor_prediction.monitor = ModelMonitor(None, reference_data)
    
    # Mettre à jour les métriques
    monitor_prediction.monitor.update_metrics(features, prediction, actual_value)
