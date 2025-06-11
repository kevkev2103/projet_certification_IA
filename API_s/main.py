from fastapi import FastAPI
from pydantic import BaseModel
from model_utils import load_model
import pandas as pd
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import date

app = FastAPI()
model = load_model()  #modèle ML préchargé


class Film(SQLModel, table=True):
    __tablename__ = "table_films"

    id_film: Optional[int] = Field(default=None, primary_key=True)
    titre: str
    duree: Optional[int] = None
    salles: Optional[int] = None
    genre: Optional[str] = None
    date_sortie: Optional[date] = None  #  Change `str` en `date`
    pays: Optional[str] = None
    studio: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    budget: Optional[int] = None
    entrees: Optional[int] = None
    anecdotes: Optional[str] = None
    film_url: Optional[str] = None
    is_pred: Optional[bool] = None


    @staticmethod
    def get_film():
        with Session(engine) as session:
            film = session.exec(select(Film)).all()
            return film

class FeaturesInput(BaseModel):
    budget: float
    duree: int
    genre: str
    pays: str
    salles_premiere_semaine: int
    scoring_acteurs_realisateurs: float
    coeff_studio: int
    year: int

    @staticmethod  
    def create_dataframe(feature_input:FeaturesInput):
        return pd.DataFrame([{
            'budget': feature_input.budget,
            'duree': feature_input.duree,
            'genre': feature_input.genre,
            'pays': feature_input.pays,
            'salles_premiere_semaine': feature_input.salles_premiere_semaine,   
            'scoring_acteurs_realisateurs': feature_input.scoring_acteurs_realisateurs,
            'coeff_studio': feature_input.coeff_studio,
            'year': feature_input.year
        }])

class PredictionOutput(BaseModel):
    prediction: float

@app.post('/prediction/', response_model=PredictionOutput)
def prediction_root(feature_input: FeaturesInput):
    films = Film.get_film()

    print(films)

    data = pd.DataFrame(films)
    # Création du DataFrame
    print(data)
    prediction = model.predict(data)
    return create_dataframe(prediction)

#uvicorn main:app --host 0.0.0.0 --port 8001 --reload