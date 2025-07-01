# app/main.py

from fastapi import FastAPI
from .routes import films, auth
from .database import check_db_connection, init_db

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

@app.on_event("startup")
def on_startup():
    # 1) Vérifier la connexion
    check_db_connection()
    # 2) (Re)créer les tables SQLModel si besoin
    init_db()

# Inclusion des routes
app.include_router(auth.router, tags=["Auth"])
app.include_router(films.router, tags=["Films"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bienvenue sur l'API Cinapps !", "version": "1.0"}