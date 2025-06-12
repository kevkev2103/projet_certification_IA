from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from model_utils import load_model
import pandas as pd
import logging
from auth import verify_api_key

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Chargement du modèle avec gestion d'erreur
try:
    model, preprocessor = load_model()  # modèle ML préchargé
    logger.info("Modèle et preprocessor chargés avec succès")
except Exception as e:
    logger.error(f"Erreur lors du chargement du modèle : {str(e)}")
    raise RuntimeError("Impossible de charger le modèle")

class PredictionRequest(BaseModel):
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

@app.post("/prediction/")
async def predict(features: PredictionRequest):
    try:
        # Créer un DataFrame avec les features
        df = pd.DataFrame([features.dict()])
        
        # Le modèle est un pipeline complet, il fait le preprocessing automatiquement
        prediction = model.predict(df)
        
        return {
            "prediction": int(prediction[0])
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# uvicorn main:app --host 0.0.0.0 --port 8001 --reload