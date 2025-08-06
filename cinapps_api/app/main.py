# app/main.py

import logging
import os
from fastapi import FastAPI
from .routes import films, auth, pred
from .database import check_db_connection, init_db
from .services import UserService
from .security import get_password_hash
from prometheus_fastapi_instrumentator import Instrumentator


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cinapps API",
    description="API sécurisée avec JWT et Auth directement dans Swagger",
    version="1.0",
    openapi_tags=[
        {"name": "Auth",   "description": "Authentification avec JWT"},
        {"name": "Films",  "description": "Gestion des films"},
        {"name": "Predictions", "description": "Gestion des prédictions d'entrées"},
    ],
)
Instrumentator().instrument(app).expose(app)



@app.on_event("startup")
def on_startup():
    # 1) Vérifier la connexion
    check_db_connection()
    # 2) (Re)créer les tables SQLModel si besoin
    init_db()

# Inclusion des routes
app.include_router(auth.router, tags=["Auth"])
app.include_router(films.router, tags=["Films"])
app.include_router(pred.router, tags=["Predictions"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bienvenue sur l'API Cinapps !", "version": "1.0"}

@app.get("/health", tags=["Root"])
async def health_check():
    """Endpoint de health check pour Docker"""
    return {"status": "healthy", "service": "cinapps-api"}

@app.post("/test/setup-user", tags=["Test"])
async def setup_test_user():
    """Endpoint pour créer l'utilisateur de test en CI"""
    if os.getenv('GITHUB_ACTIONS'):
        try:
            from .database import get_db
            db = next(get_db())
            
            # Créer l'utilisateur testuser avec mot de passe test123
            test_password = "test123"
            hashed_password = get_password_hash(test_password)
            
            # Vérifier si l'utilisateur existe déjà
            existing_user = UserService.get_user_by_username(db, "testuser")
            if existing_user:
                return {"message": "Utilisateur testuser existe déjà", "status": "success"}
            
            # Créer le nouvel utilisateur
            from .models import User
            new_user = User(username="testuser", password=hashed_password)
            db.add(new_user)
            db.commit()
            
            return {"message": "Utilisateur testuser créé avec succès", "status": "success"}
            
        except Exception as e:
            return {"message": f"Erreur création utilisateur: {str(e)}", "status": "error"}
    else:
        return {"message": "Endpoint réservé aux tests CI", "status": "skipped"}



