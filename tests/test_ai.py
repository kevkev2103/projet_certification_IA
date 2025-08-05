import pandas as pd
from cinapps_api.app.utils.model_utils import load_model, prediction


def test_model_prediction_shape():
    """Le modèle doit retourner une prédiction pour un ensemble de caractéristiques."""
    model, _ = load_model()
    sample = pd.DataFrame([
        {
            "budget": 100.0,
            "duree": 90,
            "salles_premiere_semaine": 50,
            "scoring_acteurs_realisateurs": 1.0,
            "coeff_studio": 1,
            "year": 2024,
            "genre": "Action",
            "pays": "France",
        }
    ])
    preds = prediction(model, sample)
    assert preds.shape == (1,)
