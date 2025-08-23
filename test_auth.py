#!/usr/bin/env python3
"""
Script pour tester l'authentification avec l'utilisateur chouchou
"""

import requests
import json

def test_auth():
    """Test d'authentification avec chouchou"""
    print("🔍 Test d'authentification avec l'utilisateur 'chouchou'")
    print("=" * 50)
    
    # Test 1: Authentification
    login_data = {
        "username": "chouchou",
        "password": "chouchou123"
    }
    
    try:
        response = requests.post("http://localhost:8002/auth/token", data=login_data)
        print(f"✅ Status code: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Token obtenu: {token_data.get('access_token', 'N/A')[:20]}...")
            return token_data.get('access_token')
        else:
            print(f"❌ Erreur: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_health():
    """Test de santé de l'API"""
    print("\n🏥 Test de santé de l'API")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8002/health")
        print(f"✅ Health status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Réponse: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health error: {e}")
        return False

def test_prediction_with_token(token):
    """Test de prédiction avec le token"""
    if not token:
        print("❌ Pas de token pour tester la prédiction")
        return False
    
    print("\n🎯 Test de prédiction")
    print("-" * 30)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    test_data = {
        "id_film": 999,
        "budget": 50000000,
        "duree": 120,
        "genre": "Action",
        "pays": "USA",
        "salles_premiere_semaine": 3000,
        "scoring_acteurs_realisateurs": 7.5,
        "coeff_studio": 8,
        "year": 2024,
        "is_fictif": True
    }
    
    try:
        response = requests.post("http://localhost:8002/prediction/", 
                               json=test_data, headers=headers)
        print(f"✅ Prédiction status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prédiction réussie: {result.get('prediction')}")
            return True
        else:
            print(f"❌ Erreur prédiction: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception prédiction: {e}")
        return False

def main():
    print("🚀 Test complet de l'API Cinapps")
    print("=" * 50)
    
    # Test 1: Santé de l'API
    api_ok = test_health()
    
    if not api_ok:
        print("\n❌ L'API n'est pas accessible")
        return
    
    # Test 2: Authentification
    token = test_auth()
    
    if not token:
        print("\n❌ Problème d'authentification")
        return
    
    # Test 3: Prédiction
    prediction_ok = test_prediction_with_token(token)
    
    if prediction_ok:
        print("\n✅ Tous les tests sont passés!")
        print("   Le script generate_model_metrics.py devrait fonctionner")
    else:
        print("\n❌ Problème avec l'endpoint de prédiction")

if __name__ == "__main__":
    main()
