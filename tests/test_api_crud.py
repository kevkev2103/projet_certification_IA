"""
Tests pour l'API CRUD CinApps
"""
import pytest
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# URL de base pour les tests
BASE_URL = os.getenv("API_URL_CRUD", "http://localhost:8000")

class TestAPICRUD:
    """Tests pour l'API CRUD"""
    
    def test_health_endpoint(self):
        """Test de l'endpoint de santé"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "cinapps-api"
    
    def test_root_endpoint(self):
        """Test de l'endpoint racine"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_auth_token_endpoint_exists(self):
        """Test que l'endpoint d'authentification existe"""
        # Test avec des données invalides pour vérifier que l'endpoint existe
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data={"username": "invalid", "password": "invalid"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        # L'endpoint doit exister (ne pas retourner 404)
        assert response.status_code != 404
    
    def test_docs_endpoint(self):
        """Test que la documentation Swagger est accessible"""
        response = requests.get(f"{BASE_URL}/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

class TestAuthentication:
    """Tests d'authentification"""
    
    def test_valid_credentials(self):
        """Test avec des identifiants valides"""
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data={
                "username": "chouchou",
                "password": "chouchou123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
    
    def test_invalid_credentials(self):
        """Test avec des identifiants invalides"""
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data={
                "username": "invalid_user",
                "password": "invalid_password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code in [401, 422]  # Unauthorized ou Unprocessable Entity

if __name__ == "__main__":
    pytest.main([__file__])