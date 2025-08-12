from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from ..database import engine
from ..models import PredictionRequest  
import logging
from .auth import get_current_user
from ..utils.model_utils import load_model
import pandas as pd
from prometheus_client import Counter, Histogram, Gauge
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Métriques Prometheus pour les prédictions
predictions_counter = Counter('predictions_total', 'Total number of predictions made')
prediction_duration = Histogram('prediction_duration_seconds', 'Time spent making predictions')
predictions_per_minute = Gauge('predictions_per_minute', 'Predictions per minute')

try:
    model_pipeline, preprocessor = load_model()  # modèle ML préchargé
    logger.info("Modèle et preprocessor chargés avec succès")
except Exception as e:
    logger.error(f"Erreur lors du chargement du modèle : {str(e)}")
    raise RuntimeError("Impossible de charger le modèle")

@router.post("/prediction/")
async def predict(features: PredictionRequest, current_user: dict = Depends(get_current_user)): 
    start_time = time.time()
    
    try:
        # Créer un DataFrame avec les features
        df = pd.DataFrame([features.dict()])
        
        # Le modèle est un pipeline complet, il fait le preprocessing automatiquement
        prediction = model_pipeline.predict(df)
        prediction_value = int(prediction[0])
        
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
        
        # Incrémenter les métriques Prometheus
        predictions_counter.inc()
        predictions_per_minute.inc()
        
        return {
            "prediction": prediction_value,
            "id_film": features.id_film,
            "is_fictif": features.is_fictif,
            "message": f"Prédiction {'fictive' if features.is_fictif else 'réelle'} stockée avec succès"
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Mesurer la durée de la prédiction
        duration = time.time() - start_time
        prediction_duration.observe(duration)