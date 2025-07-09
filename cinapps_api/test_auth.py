#!/usr/bin/env python3
"""
Script de test pour l'authentification et l'inscription
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"

def test_register():
    """Test d'inscription d'un nouvel utilisateur"""
    print("🔐 Test d'inscription...")
    
    # Données du nouvel utilisateur
    user_data = {
        "username": "nouveau_user",
        "password": "motdepasse123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Inscription réussie!")
            return True
        else:
            print("❌ Échec de l'inscription")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'inscription: {e}")
        return False

def test_login(username, password):
    """Test de connexion"""
    print(f"🔑 Test de connexion pour {username}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/token",
            data={
                "username": username,
                "password": password
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Connexion réussie!")
            print(f"Token: {token_data['access_token'][:50]}...")
            return token_data['access_token']
        else:
            print(f"❌ Échec de la connexion: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de la connexion: {e}")
        return None

def test_protected_route(token):
    """Test d'accès à une route protégée"""
    print("🔒 Test d'accès à une route protégée...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Accès autorisé!")
            print(f"Utilisateur: {user_data}")
            return True
        else:
            print(f"❌ Accès refusé: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'accès: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests d'authentification...\n")
    
    # Test 1: Inscription
    register_success = test_register()
    print()
    
    # Test 2: Connexion avec le nouvel utilisateur
    if register_success:
        token = test_login("nouveau_user", "motdepasse123")
        print()
        
        # Test 3: Accès à une route protégée
        if token:
            test_protected_route(token)
            print()
    
    # Test 4: Connexion avec l'utilisateur existant
    print("🔑 Test de connexion avec l'utilisateur existant...")
    token_existing = test_login("testuser", "test123")
    print()
    
    if token_existing:
        test_protected_route(token_existing)
    
    print("🏁 Tests terminés!")

if __name__ == "__main__":
    main() 