# Configuration des tests
import pytest

# Configuration simple pour tous les tests
@pytest.fixture
def api_base_url():
    """URL de base pour les tests"""
    return "http://localhost:8000"

@pytest.fixture  
def valid_user():
    """Données d'un utilisateur valide pour les tests"""
    return {
        "username": "testuser",
        "password": "test123"
    }

@pytest.fixture
def new_user():
    """Données d'un nouvel utilisateur pour les tests"""
    return {
        "username": "newuser",
        "password": "newpass123"
    }