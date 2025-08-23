import mysql.connector
import pandas as pd
import requests
from datetime import datetime
import logging
from typing import Dict, List
import os
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la base de données
DB_CONFIG = {
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'host': os.getenv('MYSQL_HOST'),
    'database': os.getenv('MYSQL_DATABASE')
}

# Configuration de l'API (APIs fusionnées)
API_URL_CRUD = os.getenv("API_URL_CRUD", "http://localhost:8002")
API_URL_PREDICTION = API_URL_CRUD + "/prediction/"
API_TOKEN = os.getenv("API_TOKEN")  # Token depuis les variables d'environnement

def authenticate_and_get_token():
    """S'authentifie automatiquement et récupère le token"""
    try:
        auth_url = f"{API_URL_CRUD}/auth/token"
        auth_data = {
            "username": "chouchou",
            "password": "chouchou123"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        response = requests.post(auth_url, data=auth_data, headers=headers)
        response.raise_for_status()
        
        token = response.json()['access_token']
        logger.info("✅ Authentification réussie")
        return token
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erreur d'authentification: {e}")
        raise

def get_db_connection():
    """Établit une connexion à la base de données"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        logger.error(f"Erreur de connexion à la base de données: {e}")
        raise

def get_unpredicted_films(conn) -> List[Dict]:
    """Récupère les films sans prédiction"""
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT f.*, 
           GROUP_CONCAT(CASE WHEN p.role = 'acteur' THEN pe.nom END) as acteurs,
           GROUP_CONCAT(CASE WHEN p.role = 'realisateur' THEN pe.nom END) as realisateurs
    FROM table_films f
    LEFT JOIN table_predictions pred ON f.id_film = pred.id_film
    LEFT JOIN table_participations p ON f.id_film = p.id_film
    LEFT JOIN table_personnes pe ON p.id_personne = pe.id_personne
    WHERE pred.id_prediction IS NULL
    GROUP BY f.id_film
    """
    cursor.execute(query)
    films = cursor.fetchall()
    cursor.close()
    return films

def calculate_scoring(acteurs: str, realisateurs: str) -> float:
    """Calcule le score des acteurs et réalisateurs"""
    # Pour l'instant, un calcul simple basé sur le nombre de personnes
    acteurs_list = acteurs.split(',') if acteurs else []
    realisateurs_list = realisateurs.split(',') if realisateurs else []
    return len(acteurs_list) * 0.5 + len(realisateurs_list) * 1.0

def prepare_prediction_data(film: Dict) -> Dict:
    """Prépare les données pour l'API de prédiction"""
    
    # Gestion de la date_sortie qui peut être un objet date ou une string
    if film['date_sortie']:
        if isinstance(film['date_sortie'], str):
            year = datetime.strptime(film['date_sortie'], '%Y-%m-%d').year
        else:  # Si c'est déjà un objet date
            year = film['date_sortie'].year
    else:
        year = datetime.now().year
    
    return {
        "id_film": film['id_film'],
        "budget": float(film['budget']) if film['budget'] else 0.0,
        "duree": film['duree'] if film['duree'] else 0,
        "genre": film['genre'] if film['genre'] else "Inconnu",
        "pays": film['pays'] if film['pays'] else "Inconnu",
        "salles_premiere_semaine": film['salles'] if film['salles'] else 0,
        "scoring_acteurs_realisateurs": calculate_scoring(film.get('acteurs'), film.get('realisateurs')),
        "coeff_studio": 1,  # Valeur par défaut, à améliorer
        "year": year
    }

def get_prediction(data: Dict) -> float:
    """Obtient une prédiction de l'API avec authentification automatique"""
    try:
        # Récupérer le token automatiquement
        token = authenticate_and_get_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.post(API_URL_PREDICTION, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        logger.info(f"Réponse de l'API: {result}")
        return result['prediction']
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de l'appel à l'API: {e}")
        raise

def main():
    """Fonction principale du pipeline"""
    logger.info("Démarrage du pipeline de prédiction")
    
    try:
        conn = get_db_connection()
        films = get_unpredicted_films(conn)
        logger.info(f"Nombre de films à traiter: {len(films)}")
        
        for film in films:
            logger.info(f"Traitement du film: {film['titre']}")
            
            # Préparation des données
            prediction_data = prepare_prediction_data(film)
            logger.info(f"Données préparées: {prediction_data}")
            
            # Obtention de la prédiction (stockage automatique par l'API)
            prediction = get_prediction(prediction_data)
            logger.info(f"Prédiction obtenue et stockée: {prediction}")
        
        logger.info("Pipeline terminé avec succès")
        
    except Exception as e:
        logger.error(f"Erreur dans le pipeline: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main() 