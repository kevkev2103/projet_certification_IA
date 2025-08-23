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

# Configuration de la base de données (même config que load_csv_to_db.py)
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'cinapps',
    'user': 'kevin',
    'password': 'kevinpass',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

# Configuration de l'API ML (port 8002 SEULEMENT)
API_URL = "http://localhost:8002/prediction/"

def authenticate_and_get_token():
    """S'authentifie automatiquement et récupère le token JWT"""
    try:
        auth_url = "http://localhost:8002/auth/token"
        auth_data = {
            "username": "testuser",
            "password": "test123"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        response = requests.post(auth_url, data=auth_data, headers=headers)
        response.raise_for_status()
        
        token = response.json()['access_token']
        logger.info("✅ Authentification JWT réussie")
        return token
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erreur d'authentification: {e}")
        raise

def get_db_connection():
    """Établit une connexion à la base de données"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        logger.info("✅ Connexion à la base de données établie")
        return connection
    except mysql.connector.Error as e:
        logger.error(f"❌ Erreur de connexion à la base : {e}")
        raise

def get_unpredicted_fictive_films(conn) -> List[Dict]:
    """Récupère les films fictifs sans prédiction (évite les doublons)"""
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT DISTINCT ff.* 
    FROM film_fictif ff
    LEFT JOIN prediction_fictive pf ON ff.id_film_fictif = pf.id_film_fictif
    WHERE pf.id_prediction_fictive IS NULL
    GROUP BY ff.id_film_fictif
    """
    cursor.execute(query)
    films = cursor.fetchall()
    cursor.close()
    logger.info(f"📊 {len(films)} films fictifs à prédire trouvés")
    return films

def prepare_fictive_prediction_data(film: Dict) -> Dict:
    """Prépare les données des films fictifs pour l'API de prédiction"""
    
    return {
        "id_film": film['id_film_fictif'],  # ID du film fictif
        "budget": float(film['budget']) if film['budget'] else 0.0,
        "duree": film['duree'] if film['duree'] else 0,
        "genre": film['genre'] if film['genre'] else "Inconnu",
        "pays": film['pays'] if film['pays'] else "Inconnu",
        "salles_premiere_semaine": film['salles_premiere_semaine'] if film['salles_premiere_semaine'] else 0,
        "scoring_acteurs_realisateurs": float(film['scoring_acteurs_realisateurs']) if film['scoring_acteurs_realisateurs'] else 0.0,
        "coeff_studio": film['coeff_studio'] if film['coeff_studio'] else 1,
        "year": film['year'] if film['year'] else datetime.now().year,
        "is_fictif": True  # Nouveau paramètre pour identifier les films fictifs
    }

def get_fictive_prediction(data: Dict) -> float:
    """Obtient une prédiction de l'API ML pour un film fictif (SANS stockage auto)"""
    try:
        # Récupérer le token JWT automatiquement
        token = authenticate_and_get_token()
        
        # SUPPRIMER is_fictif pour éviter le stockage automatique dans l'API
        prediction_data = {k: v for k, v in data.items() if k != 'is_fictif'}
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.post(API_URL, json=prediction_data, headers=headers)
        response.raise_for_status()
        result = response.json()
        logger.info(f"🎯 Prédiction reçue: {result['prediction']} entrées (stockage manuel)")
        return result['prediction']
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erreur API: {e}")
        raise

def store_fictive_prediction(conn, id_film_fictif: int, prediction: float):
    """Stocke la prédiction dans la table prediction_fictive"""
    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO prediction_fictive (id_film_fictif, prediction_entrees)
        VALUES (%s, %s)
        """
        cursor.execute(query, (id_film_fictif, int(prediction)))
        conn.commit()
        logger.info(f"✅ Prédiction stockée pour film fictif ID {id_film_fictif}")
    except mysql.connector.Error as e:
        logger.error(f"❌ Erreur stockage prédiction: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()

def main():
    """Fonction principale du pipeline films fictifs"""
    logger.info("🚀 DÉMARRAGE PIPELINE PRÉDICTIONS FILMS FICTIFS")
    logger.info("=" * 60)
    
    try:
        conn = get_db_connection()
        films = get_unpredicted_fictive_films(conn)
        
        if not films:
            logger.info("📝 Aucun film fictif à prédire")
            return
        
        logger.info(f"🎬 {len(films)} films fictifs à traiter")
        
        for i, film in enumerate(films, 1):
            logger.info(f"\n🎭 [{i}/{len(films)}] Traitement : {film['titre']}")
            
            # Préparation des données
            prediction_data = prepare_fictive_prediction_data(film)
            logger.info(f"📋 Données préparées pour {film['titre']}")
            
            # Obtention de la prédiction via API ML
            prediction = get_fictive_prediction(prediction_data)
            
            # Stockage en base locale (prediction_fictive)
            store_fictive_prediction(conn, film['id_film_fictif'], prediction)
            
            logger.info(f"🎉 Film '{film['titre']}' traité avec succès")
        
        logger.info("=" * 60)
        logger.info(f"🏆 PIPELINE TERMINÉ - {len(films)} prédictions générées")
        logger.info("💡 Prochaine étape : Vérifier les résultats dans DBeaver")
        
    except Exception as e:
        logger.error(f"💥 Erreur dans le pipeline: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("🔌 Connexion fermée")

if __name__ == "__main__":
    main() 