from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from dotenv import load_dotenv
import os
import requests
import logging
from typing import Dict

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# Système de récupération du token depuis le header Authorization
oauth2_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")  # le "sub" a été mis dans l'API CRUD
        if username is None:
            raise credentials_exception()
        return username
    except JWTError:
        raise credentials_exception()

def credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

# Alias pour la compatibilité avec main.py
verify_api_key = get_current_user

def authenticate_and_get_token():
    """S'authentifie automatiquement et récupère le token"""
    try:
        auth_url = "http://localhost:8000/auth/token"
        auth_data = {
            "username": "testuser",
            "password": "test123"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        response = requests.post(auth_url, data=auth_data, headers=headers)
        response.raise_for_status()
        
        token = response.json()['access_token']
        logging.info("✅ Authentification réussie")
        return token
        
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Erreur d'authentification: {e}")
        raise

def get_prediction(data: Dict) -> float:
    """Obtient une prédiction de l'API avec authentification automatique"""
    try:
        # Récupérer le token automatiquement
        token = authenticate_and_get_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.post(API_URL, json=data, headers=headers)
        response.raise_for_status()
        return response.json()['prediction']
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Erreur lors de l'appel à l'API: {e}")
        raise
