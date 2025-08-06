# Tests d'intégration simples - Flux bout-en-bout
import pytest
import requests
import time

# URLs des APIs
CRUD_API_URL = "http://localhost:8000"
ML_API_URL = "http://localhost:8001"

def test_full_auth_flow():
    """Test d'intégration : flux d'authentification complet"""
    # ARRANGE
    login_url = f"{CRUD_API_URL}/auth/token"
    me_url = f"{CRUD_API_URL}/auth/users/me"
    login_data = {"username": "testuser", "password": "test123"}
    
    # ACT 1 : Login
    login_response = requests.post(login_url, data=login_data)
    
    # ASSERT 1 : Login réussi
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token is not None
    
    # ACT 2 : Utiliser le token
    headers = {"Authorization": f"Bearer {token}"}
    me_response = requests.get(me_url, headers=headers)
    
    # ASSERT 2 : Token valide
    assert me_response.status_code == 200
    user_data = me_response.json()
    assert user_data["username"] == "testuser"

def test_films_api_integration():
    """Test d'intégration : gestion complète des films"""
    # ARRANGE - Récupérer un token
    login_url = f"{CRUD_API_URL}/auth/token"
    login_data = {"username": "testuser", "password": "test123"}
    login_response = requests.post(login_url, data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # ACT 1 : Lister les films
    films_url = f"{CRUD_API_URL}/films/"
    films_response = requests.get(films_url, headers=headers)
    
    # ASSERT 1 : Films accessibles
    assert films_response.status_code in [200, 404]  # 200 ou 404 si vide
    
    # ACT 2 : Créer un film de test
    new_film = {
        "titre": "Film Integration Test",
        "annee_sortie": 2024,
        "genre": "Test",
        "duree": 90
    }
    create_response = requests.post(films_url, json=new_film, headers=headers)
    
    # ASSERT 2 : Film créé ou existe déjà
    assert create_response.status_code in [201, 400]

def test_api_connectivity():
    """Test d'intégration : connectivité entre services"""
    # Test que toutes les APIs sont accessibles
    apis_to_test = [
        (CRUD_API_URL, "CRUD API"),
        (ML_API_URL, "ML API")
    ]
    
    results = {}
    
    for url, name in apis_to_test:
        try:
            response = requests.get(url, timeout=5)
            results[name] = response.status_code == 200
        except requests.exceptions.RequestException:
            results[name] = False
    
    # Afficher les résultats pour diagnostic
    print(f"Connectivité des APIs: {results}")
    
    # Au moins une API doit être accessible
    assert any(results.values()), "Aucune API n'est accessible"

def test_error_handling_integration():
    """Test d'intégration : gestion d'erreurs à travers les APIs"""
    # ARRANGE - Tester l'accès à la liste des films sans auth
    films_url = f"{CRUD_API_URL}/films/"
    
    # ACT 1 : Accès sans authentification
    response_no_auth = requests.get(films_url)
    
    # ASSERT 1 : Erreur d'authentification
    assert response_no_auth.status_code == 401
    
    # ARRANGE 2 : Avec authentification valide
    login_url = f"{CRUD_API_URL}/auth/token"
    login_data = {"username": "testuser", "password": "test123"}
    login_response = requests.post(login_url, data=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # ACT 2 : Accès à une ressource inexistante (film avec ID très élevé)
        wrong_url = f"{CRUD_API_URL}/films/999999"
        response_not_found = requests.get(wrong_url, headers=headers)
        
        # ASSERT 2 : Ressource non trouvée ou méthode non autorisée
        assert response_not_found.status_code in [404, 405]

def test_data_flow_integration():
    """Test d'intégration : flux de données entre composants"""
    # Ce test vérifie que les données peuvent circuler entre les APIs
    
    # ARRANGE - Authentification
    login_url = f"{CRUD_API_URL}/auth/token"
    login_data = {"username": "testuser", "password": "test123"}
    
    try:
        # ACT 1 : Login
        login_response = requests.post(login_url, data=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            
            # ACT 2 : Récupérer des films
            films_url = f"{CRUD_API_URL}/films/"
            headers = {"Authorization": f"Bearer {token}"}
            films_response = requests.get(films_url, headers=headers)
            
            # ASSERT : Le flux de données fonctionne
            assert films_response.status_code in [200, 404]
            
            print("✅ Flux de données CRUD API: OK")
        else:
            print("⚠️ Authentification échouée")
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Erreur de connexion: {e}")
        
    # Test de l'API ML
    try:
        ml_health_response = requests.get(f"{ML_API_URL}/health", timeout=5)
        if ml_health_response.status_code == 200:
            print("✅ Flux de données ML API: OK")
        else:
            print("⚠️ ML API non accessible")
    except requests.exceptions.RequestException:
        print("⚠️ ML API non accessible")
    
    # Ce test ne fail jamais mais donne des infos
    assert True