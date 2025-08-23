#!/usr/bin/env python3
"""
Script pour générer des données de test pour les métriques du modèle IA
"""

import requests
import time
import random
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8002"
LOGIN_URL = f"{API_BASE_URL}/auth/token"
PREDICTION_URL = f"{API_BASE_URL}/prediction/"

# Données de test pour simuler différents scénarios
TEST_SCENARIOS = [
    # Scénario normal
    {
        "name": "Film normal",
        "data": {
            "id_film": 1,
            "budget": 50000000,
            "duree": 120,
            "genre": "Action",
            "pays": "USA",
            "salles_premiere_semaine": 3000,
            "scoring_acteurs_realisateurs": 7.5,
            "coeff_studio": 8,
            "year": 2024,
            "is_fictif": False
        }
    },
    # Scénario budget élevé (drift)
    {
        "name": "Film gros budget",
        "data": {
            "id_film": 2,
            "budget": 200000000,
            "duree": 150,
            "genre": "Action",
            "pays": "USA",
            "salles_premiere_semaine": 4000,
            "scoring_acteurs_realisateurs": 8.0,
            "coeff_studio": 9,
            "year": 2024,
            "is_fictif": False
        }
    },
    # Scénario durée longue (drift)
    {
        "name": "Film très long",
        "data": {
            "id_film": 3,
            "budget": 30000000,
            "duree": 180,
            "genre": "Drame",
            "pays": "France",
            "salles_premiere_semaine": 800,
            "scoring_acteurs_realisateurs": 6.5,
            "coeff_studio": 5,
            "year": 2024,
            "is_fictif": False
        }
    },
    # Scénario genre rare
    {
        "name": "Film genre rare",
        "data": {
            "id_film": 4,
            "budget": 40000000,
            "duree": 100,
            "genre": "Documentaire",
            "pays": "UK",
            "salles_premiere_semaine": 200,
            "scoring_acteurs_realisateurs": 5.0,
            "coeff_studio": 3,
            "year": 2024,
            "is_fictif": False
        }
    },
    # Scénario normal
    {
        "name": "Film normal 2",
        "data": {
            "id_film": 5,
            "budget": 60000000,
            "duree": 110,
            "genre": "Comédie",
            "pays": "France",
            "salles_premiere_semaine": 1200,
            "scoring_acteurs_realisateurs": 7.0,
            "coeff_studio": 6,
            "year": 2024,
            "is_fictif": False
        }
    }
]

def login():
    """Se connecter à l'API"""
    login_data = {
        "username": "chouchou",
        "password": "chouchou123"
    }
    
    try:
        response = requests.post(LOGIN_URL, data=login_data)
        response.raise_for_status()
        
        # Extraire le token d'accès
        token_data = response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            print("❌ Erreur: Token d'accès non trouvé dans la réponse")
            return None
            
        print("✅ Connexion réussie")
        return access_token
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def make_prediction(token, scenario):
    """Faire une prédiction avec le scénario donné"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(PREDICTION_URL, json=scenario["data"], headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ {scenario['name']}: Prédiction = {result.get('prediction', 'N/A')}")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur prédiction {scenario['name']}: {e}")
        return None

def generate_traffic(duration_minutes=5, interval_seconds=10):
    """Générer du trafic pendant la durée spécifiée"""
    print(f"🚀 Génération de trafic pendant {duration_minutes} minutes...")
    print(f"   Intervalle: {interval_seconds} secondes entre les requêtes")
    print(f"   Scénarios: {len(TEST_SCENARIOS)}")
    print("-" * 50)
    
    # Se connecter
    token = login()
    if not token:
        return
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    request_count = 0
    
    while time.time() < end_time:
        # Choisir un scénario aléatoire
        scenario = random.choice(TEST_SCENARIOS)
        
        # Faire la prédiction
        result = make_prediction(token, scenario)
        if result:
            request_count += 1
        
        # Attendre avant la prochaine requête
        time.sleep(interval_seconds)
    
    elapsed_time = time.time() - start_time
    print("-" * 50)
    print(f"✅ Génération terminée!")
    print(f"   Temps écoulé: {elapsed_time:.1f} secondes")
    print(f"   Requêtes effectuées: {request_count}")
    print(f"   Taux: {request_count / (elapsed_time / 60):.1f} req/min")

def quick_test():
    """Test rapide avec quelques requêtes"""
    print("🧪 Test rapide avec 3 requêtes...")
    
    token = login()
    if not token:
        return
    
    for i, scenario in enumerate(TEST_SCENARIOS[:3]):
        print(f"\n--- Requête {i+1} ---")
        result = make_prediction(token, scenario)
        time.sleep(2)  # Pause entre les requêtes

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_test()
    else:
        # Génération de trafic par défaut
        generate_traffic(duration_minutes=3, interval_seconds=5)
