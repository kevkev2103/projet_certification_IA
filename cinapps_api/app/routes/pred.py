from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from ..database import engine
from ..models import PredictionRequest  
import logging
from .auth import get_current_user
from ..utils.model_utils import load_model
import pandas as pd
from prometheus_client import Counter, Histogram, Gauge, Summary
import time
import numpy as np
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# ===== MÉTRIQUES DU MODÈLE IA =====
# Métriques de performance du modèle
model_inference_time = Histogram('model_inference_time_seconds', 'Temps d\'inférence du modèle')
model_prediction_accuracy = Gauge('model_prediction_accuracy', 'Précision moyenne du modèle')
model_prediction_mae = Gauge('model_prediction_mae', 'Mean Absolute Error du modèle')

# Métriques de drift des features
feature_drift_budget = Gauge('feature_drift_budget', 'Drift de la feature budget (%)')
feature_drift_duree = Gauge('feature_drift_duree', 'Drift de la feature durée (%)')
feature_drift_genre = Counter('feature_drift_genre', 'Distribution des genres', ['genre'])

# Métriques de qualité des prédictions
prediction_outliers = Counter('prediction_outliers_total', 'Nombre de prédictions aberrantes')
prediction_range = Summary('prediction_range', 'Distribution des prédictions')
prediction_volatility = Gauge('prediction_volatility', 'Volatilité des prédictions (%)')

# Métriques de santé du modèle
model_health_score = Gauge('model_health_score', 'Score de santé du modèle (0-100)')
model_version = Gauge('model_version', 'Version du modèle déployé', ['version'])

# Historique pour calculs de drift
prediction_history = deque(maxlen=1000)  # Garder les 1000 dernières prédictions
feature_history = deque(maxlen=1000)     # Garder les 1000 dernières features

# Statistiques de référence (données d'entraînement)
REFERENCE_STATS = {
    'budget': {'mean': 50000000, 'std': 30000000},
    'duree': {'mean': 120, 'std': 30},
    'genre_dist': {'Action': 0.3, 'Comédie': 0.25, 'Drame': 0.2, 'Thriller': 0.15, 'Autre': 0.1}
}

try:
    model_pipeline, preprocessor = load_model()  # modèle ML préchargé
    logger.info("Modèle et preprocessor chargés avec succès")
    
    # Initialiser la version du modèle
    model_version.labels(version="1.0").set(1)
    
except Exception as e:
    logger.error(f"Erreur lors du chargement du modèle : {str(e)}")
    raise RuntimeError("Impossible de charger le modèle")

def calculate_drift(current_features):
    """Calculer le drift des features par rapport aux données d'entraînement"""
    drift_metrics = {}
    
    # Drift du budget
    if 'budget' in current_features:
        current_budget = current_features['budget']
        ref_budget_mean = REFERENCE_STATS['budget']['mean']
        drift_metrics['budget'] = abs(current_budget - ref_budget_mean) / ref_budget_mean * 100
    
    # Drift de la durée
    if 'duree' in current_features:
        current_duree = current_features['duree']
        ref_duree_mean = REFERENCE_STATS['duree']['mean']
        drift_metrics['duree'] = abs(current_duree - ref_duree_mean) / ref_duree_mean * 100
    
    return drift_metrics

def calculate_prediction_volatility():
    """Calculer la volatilité des prédictions récentes"""
    if len(prediction_history) < 2:
        return 0
    
    predictions = list(prediction_history)
    mean_pred = np.mean(predictions)
    std_pred = np.std(predictions)
    
    if mean_pred == 0:
        return 0
    
    return (std_pred / mean_pred) * 100

def calculate_health_score():
    """Calculer un score de santé du modèle"""
    score = 100
    
    # Réduire le score si trop d'outliers
    if len(prediction_history) > 10:
        recent_predictions = list(prediction_history)[-10:]
        outlier_count = sum(1 for p in recent_predictions if p > 1000000000)  # Plus d'1 milliard
        outlier_ratio = outlier_count / len(recent_predictions)
        score -= outlier_ratio * 30
    
    # Réduire le score si volatilité élevée
    volatility = calculate_prediction_volatility()
    if volatility > 50:  # 50% de volatilité
        score -= 20
    
    # Réduire le score si drift élevé
    if len(feature_history) > 0:
        recent_features = list(feature_history)[-10:]
        avg_drift = np.mean([
            calculate_drift(f).get('budget', 0) + calculate_drift(f).get('duree', 0)
            for f in recent_features
        ]) / 2
        if avg_drift > 30:  # 30% de drift moyen
            score -= 15
    
    return max(0, score)

def update_model_metrics(features, prediction):
    """Mettre à jour toutes les métriques du modèle"""
    # Temps d'inférence (déjà mesuré dans la fonction principale)
    
    # Drift des features
    drift = calculate_drift(features)
    if 'budget' in drift:
        feature_drift_budget.set(drift['budget'])
    if 'duree' in drift:
        feature_drift_duree.set(drift['duree'])
    
    # Distribution des genres
    genre = features.get('genre', 'unknown')
    feature_drift_genre.labels(genre=genre).inc()
    
    # Qualité des prédictions
    prediction_range.observe(prediction)
    
    # Détection d'outliers
    if prediction > 1000000000:  # Plus d'1 milliard d'entrées
        prediction_outliers.inc()
    
    # Ajouter à l'historique
    prediction_history.append(prediction)
    feature_history.append(features)
    
    # Volatilité des prédictions
    volatility = calculate_prediction_volatility()
    prediction_volatility.set(volatility)
    
    # Score de santé du modèle
    health_score = calculate_health_score()
    model_health_score.set(health_score)

@router.post("/prediction/")
async def predict(features: PredictionRequest, current_user: dict = Depends(get_current_user)): 
    model_start_time = time.time()  # Début du chronomètre pour le modèle
    
    try:
        # Créer un DataFrame avec les features
        df = pd.DataFrame([features.dict()])
        
        # Le modèle est un pipeline complet, il fait le preprocessing automatiquement
        prediction = model_pipeline.predict(df)
        prediction_value = int(prediction[0])
        
        # Mesurer le temps d'inférence du modèle
        model_inference_time.observe(time.time() - model_start_time)
        
        # Stocker la prédiction selon le type de film
        with engine.connect() as conn:
            if features.is_fictif:
                # Pour les films fictifs : stockage dans prediction_fictive
                insert_prediction = text("""
                    INSERT INTO prediction_fictive (id_film_fictif, prediction_entrees)
                    VALUES (:id_film, :prediction)
                """)
                conn.execute(insert_prediction, {
                    "id_film": features.id_film,
                    "prediction": prediction_value
                })
                logger.info(f"Prédiction fictive stockée pour film ID {features.id_film}")
            else:
                # Pour les films réels : stockage dans table_predictions
                insert_prediction = text("""
                    INSERT INTO table_predictions (id_film, prediction_entrees)
                    VALUES (:id_film, :prediction)
                """)
                conn.execute(insert_prediction, {
                    "id_film": features.id_film,
                    "prediction": prediction_value
                })
                
                # Mettre à jour le statut is_pred dans table_films
                update_film = text("""
                    UPDATE table_films 
                    SET is_pred = TRUE 
                    WHERE id_film = :id_film
                """)
                conn.execute(update_film, {"id_film": features.id_film})
                logger.info(f"Prédiction réelle stockée pour film ID {features.id_film}")
            
            conn.commit()
        
        # ===== MISE À JOUR DES MÉTRIQUES DU MODÈLE =====
        update_model_metrics(features.dict(), prediction_value)
        
        return {
            "prediction": prediction_value,
            "id_film": features.id_film,
            "is_fictif": features.is_fictif,
            "message": f"Prédiction {'fictive' if features.is_fictif else 'réelle'} stockée avec succès"
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))