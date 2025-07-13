from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from model_utils import load_model
import pandas as pd
import logging
from auth import verify_api_key
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os


# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

app = FastAPI()

# Chargement du modèle avec gestion d'erreur
try:
    model_pipeline, preprocessor = load_model()  # modèle ML préchargé
    logger.info("Modèle et preprocessor chargés avec succès")
except Exception as e:
    logger.error(f"Erreur lors du chargement du modèle : {str(e)}")
    raise RuntimeError("Impossible de charger le modèle")

class PredictionRequest(BaseModel):
    id_film: int
    budget: float
    duree: int
    genre: str
    pays: str
    salles_premiere_semaine: int
    scoring_acteurs_realisateurs: float
    coeff_studio: int
    year: int

@app.get("/")
async def root():
    return {"message": "Welcome to the Movie Box Office Prediction API"}

@app.post("/prediction/", dependencies=[Depends(verify_api_key)])
async def predict(features: PredictionRequest):
    try:
        # Créer un DataFrame avec les features
        df = pd.DataFrame([features.dict()])
        
        # Le modèle est un pipeline complet, il fait le preprocessing automatiquement
        prediction = model_pipeline.predict(df)
        prediction_value = int(prediction[0])
        
        # Stocker la prédiction dans la base de données
        with engine.connect() as conn:
            # Insérer la prédiction
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
            
            conn.commit()
        
        logger.info(f"Prédiction stockée pour le film ID {features.id_film}")
        
        return {
            "prediction": prediction_value,
            "id_film": features.id_film,
            "message": "Prédiction stockée avec succès"
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



# uvicorn main:app --host 0.0.0.0 --port 8001 --reload