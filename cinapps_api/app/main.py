# app/main.py

import logging
from fastapi import FastAPI
from .routes import films, auth, pred
from .database import check_db_connection, init_db
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



