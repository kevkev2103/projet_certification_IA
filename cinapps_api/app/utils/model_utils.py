import pickle
import os

def load_model():
    """
    Charge le modèle pipeline depuis le fichier pickle
    """
    # Chemin vers le modèle dans le même dossier
    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    
    with open(model_path, 'rb') as f:
        model_pipeline = pickle.load(f)
    
    # Retourne le pipeline complet et son preprocessor
    preprocessor = model_pipeline.named_steps['preprocessor']
    return model_pipeline, preprocessor

def prediction(model, data):
    predictions = model.predict(data)
    return predictions