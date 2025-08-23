# Configuration des tests
import pytest
import os
from database_test import setup_test_database

# Setup automatique de la base de test
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Setup automatique de la base de données pour les tests"""
    if os.getenv('GITHUB_ACTIONS'):
        print("🔧 Setup SQLite pour CI...")
        setup_test_database()
    else:
        print("🔧 Utilisation MySQL local...")

# Configuration simple pour tous les tests
@pytest.fixture
def api_base_url():
    """URL de base pour les tests"""
    return "http://localhost:8002"

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