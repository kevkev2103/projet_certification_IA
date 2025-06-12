import pickle

def load_model():
    """
    Charge le modèle pipeline depuis le fichier pickle
    """
    with open('model.pkl', 'rb') as f:
        model_pipeline = pickle.load(f)
    
    # Retourne le pipeline complet et son preprocessor
    preprocessor = model_pipeline.named_steps['preprocessor']
    return model_pipeline, preprocessor

def prediction(model, data):
    predictions = model.predict(data)
    return predictions