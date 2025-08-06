# Tests simples pour l'authentification
import pytest
import requests

def test_login_existing_user():
    """Test basique : connexion avec utilisateur existant"""
    # ARRANGE (Préparer)
    url = "http://localhost:8000/auth/token"
    data = {
        "username": "testuser",
        "password": "test123"
    }
    
    # ACT (Agir) 
    response = requests.post(url, data=data)
    
    # ASSERT (Vérifier)
    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"

def test_login_wrong_password():
    """Test basique : mauvais mot de passe"""
    # ARRANGE
    url = "http://localhost:8000/auth/token"
    data = {
        "username": "testuser", 
        "password": "wrongpassword"
    }
    
    # ACT
    response = requests.post(url, data=data)
    
    # ASSERT
    assert response.status_code == 401

def test_get_user_info_without_token():
    """Test basique : accès refusé sans token"""
    # ARRANGE
    url = "http://localhost:8000/auth/users/me"
    
    # ACT
    response = requests.get(url)
    
    # ASSERT
    assert response.status_code == 401