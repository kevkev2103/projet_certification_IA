import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

# Configuration de l'environnement pour les tests
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "testsecret")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from cinapps_api.app.database import engine
from cinapps_api.app.main import app


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Initialise une base SQLite propre pour l'ensemble du module de tests."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


def test_root_and_health_endpoints():
    """Vérifie que les endpoints racine et health répondent correctement."""
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        assert client.get("/health").status_code == 200


def test_full_api_flow():
    """Parcourt l'ensemble des endpoints principaux de l'API."""
    with TestClient(app) as client:
        # Inscription d'un utilisateur
        response = client.post("/auth/register", json={"username": "alice", "password": "wonder"})
        assert response.status_code == 200

        # Authentification
        response = client.post(
            "/auth/token",
            data={"username": "alice", "password": "wonder"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Utilisateur courant et liste des utilisateurs
        assert client.get("/auth/users/me", headers=headers).json()["username"] == "alice"
        users = client.get("/auth/users", headers=headers)
        assert users.status_code == 200 and any(u["username"] == "alice" for u in users.json())

        # Création d'un film
        film_payload = {"titre": "Film test", "duree": 100}
        film = client.post("/films/", json=film_payload, headers=headers)
        assert film.status_code == 201
        film_id = film.json()["id_film"]

        # Lecture et mise à jour du film
        assert client.get("/films/", headers=headers).status_code == 200
        updated = client.put(f"/films/{film_id}", json={"titre": "Film mod"}, headers=headers)
        assert updated.status_code == 200 and updated.json()["titre"] == "Film mod"

        # Endpoints acteurs / réalisateurs (retourne des listes vides)
        assert client.get(f"/films/{film_id}/acteurs/", headers=headers).json() == []
        assert client.get(f"/films/{film_id}/realisateurs/", headers=headers).json() == []

        # Endpoint de prédiction
        features = {
            "id_film": film_id,
            "budget": 100.0,
            "duree": 90,
            "genre": "Action",
            "pays": "France",
            "salles_premiere_semaine": 50,
            "scoring_acteurs_realisateurs": 1.0,
            "coeff_studio": 1,
            "year": 2024,
            "is_fictif": False,
        }
        prediction = client.post("/prediction/", json=features, headers=headers)
        assert prediction.status_code == 200 and "prediction" in prediction.json()

        # Consultation des prédictions
        assert len(client.get("/predictions/", headers=headers).json()) == 1
        assert len(client.get(f"/films/{film_id}/predictions/", headers=headers).json()) == 1

        # Suppression du film puis de l'utilisateur
        assert client.delete(f"/films/{film_id}", headers=headers).status_code == 200
        assert client.delete("/auth/users/alice", headers=headers).status_code == 200
