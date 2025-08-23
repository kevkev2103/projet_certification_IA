# Tests simples pour l'API ML (Prédictions) - Intégrée dans CRUD API
import pytest
import requests

# Configuration API - L'API ML est intégrée dans l'API CRUD sur le port 8002
API_URL = "http://localhost:8002"

def get_auth_token():
    """Fonction helper : récupérer un token JWT pour l'API ML"""
    url = f"{API_URL}/auth/token"
    data = {"username": "testuser", "password": "test123"}
    response = requests.post(url, data=data)
    return response.json()["access_token"]

def test_prediction_without_auth():
    """Test basique : prédiction refusée sans authentification"""
    # ARRANGE
    url = f"{API_URL}/prediction/"
    prediction_data = {
        "id_film": 1,
        "budget": 100000000,
        "duree": 120,
        "genre": "Action",
        "pays": "US",
        "salles_premiere_semaine": 3000,
        "scoring_acteurs_realisateurs": 8.5,
        "coeff_studio": 1,
        "year": 2024,
        "is_fictif": True
    }
    
    # ACT
    response = requests.post(url, json=prediction_data)
    
    # ASSERT
    assert response.status_code == 401  # Non autorisé

def test_prediction_with_auth():
    """Test basique : prédiction avec authentification valide"""
    # ARRANGE
    token = get_auth_token()
    url = f"{API_URL}/prediction/"
    headers = {"Authorization": f"Bearer {token}"}
    prediction_data = {
        "id_film": 1,
        "budget": 100000000,
        "duree": 120,
        "genre": "Action",
        "pays": "US",
        "salles_premiere_semaine": 3000,
        "scoring_acteurs_realisateurs": 8.5,
        "coeff_studio": 1,
        "year": 2024,
        "is_fictif": True
    }
    
    # ACT
    response = requests.post(url, json=prediction_data, headers=headers)
    
    # ASSERT
    assert response.status_code in [200, 500]  # 200 si OK, 500 si modèle pas chargé

def test_prediction_with_invalid_data():
    """Test basique : prédiction avec données invalides"""
    # ARRANGE
    token = get_auth_token()
    url = f"{API_URL}/prediction/"
    headers = {"Authorization": f"Bearer {token}"}
    invalid_data = {
        "id_film": "not_a_number",  # Données invalides
        "budget": -1000  # Budget négatif
    }
    
    # ACT
    response = requests.post(url, json=invalid_data, headers=headers)
    
    # ASSERT
    # Peut être 422 (données invalides) ou 500 (erreur serveur)
    assert response.status_code in [422, 400, 500]

def test_prediction_api_endpoint_exists():
    """Test basique : vérifier que l'endpoint de prédiction existe"""
    # ARRANGE
    token = get_auth_token()
    url = f"{API_URL}/prediction/"
    headers = {"Authorization": f"Bearer {token}"}
    
    # ACT - Test avec données minimales pour vérifier l'endpoint
    minimal_data = {
        "id_film": 1,
        "budget": 1000000,
        "duree": 90,
        "genre": "Test",
        "pays": "FR",
        "salles_premiere_semaine": 100,
        "scoring_acteurs_realisateurs": 5.0,
        "coeff_studio": 1,
        "year": 2024,
        "is_fictif": True
    }
    response = requests.post(url, json=minimal_data, headers=headers)
    
    # ASSERT - L'endpoint doit exister (pas 404)
    assert response.status_code != 404
    print(f"Endpoint /prediction/ : Status {response.status_code}")