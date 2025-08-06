# Tests simples pour les films
import pytest
import requests

def get_auth_token():
    """Fonction helper : récupérer un token d'auth"""
    url = "http://localhost:8000/auth/token"
    data = {"username": "testuser", "password": "test123"}
    response = requests.post(url, data=data)
    return response.json()["access_token"]

def test_get_films_with_auth():
    """Test basique : récupérer la liste des films"""
    # ARRANGE
    token = get_auth_token()
    url = "http://localhost:8000/films/"
    headers = {"Authorization": f"Bearer {token}"}
    
    # ACT
    response = requests.get(url, headers=headers)
    
    # ASSERT
    assert response.status_code in [200, 404]  # 200 si films, 404 si vide
    
def test_get_films_without_auth():
    """Test basique : accès refusé sans authentification"""
    # ARRANGE
    url = "http://localhost:8000/films/"
    
    # ACT
    response = requests.get(url)
    
    # ASSERT
    assert response.status_code == 401

def test_create_film():
    """Test basique : créer un film"""
    # ARRANGE
    token = get_auth_token()
    url = "http://localhost:8000/films/"
    headers = {"Authorization": f"Bearer {token}"}
    
    film_data = {
        "titre": "Film Test",
        "annee_sortie": 2024,
        "genre": "Action",
        "duree": 120
    }
    
    # ACT
    response = requests.post(url, json=film_data, headers=headers)
    
    # ASSERT
    assert response.status_code in [201, 400]  # 201 créé, 400 si existe déjà

def test_create_film_without_auth():
    """Test basique : création refusée sans auth"""
    # ARRANGE
    url = "http://localhost:8000/films/"
    film_data = {
        "titre": "Film Test Sans Auth",
        "annee_sortie": 2024,
        "genre": "Action",
        "duree": 120
    }
    
    # ACT
    response = requests.post(url, json=film_data)
    
    # ASSERT
    assert response.status_code == 401