# Rapport E1 - Gestion des données


---

## �� Table des matières
1. [C1 - Automatiser l'extraction de données](#c1---automatiser-lextraction-de-données)
2. [C2 - Développer des requêtes SQL](#c2---développer-des-requêtes-sql)
3. [C3 - Développer des règles d'agrégation](#c3---développer-des-règles-dagrégation)
4. [C4 - Créer une base de données (RGPD)](#c4---créer-une-base-de-données-rgpd)
5. [C5 - Développer une API REST](#c5---développer-une-api-rest)

---

## C1 - Automatiser l'extraction de données

### 🏗️ Architecture du scraping

#### Vue d'ensemble
Notre système de scraping utilise **Scrapy**, un framework Python puissant pour extraire des données de sites web.


#### Composants principaux
- **Spiders** : Robots qui parcourent les sites web
- **Pipeline** : Traitement et nettoyage des données
- **Settings** : Configuration (délais, user-agent, etc.)
- **Items** : Structure des données extraites

### 🎯 Spécifications fonctionnelles

#### Objectifs du projet
1. **Collecter des données de films** depuis Allociné
2. **Extraire les informations clés** : titre, durée, genre, acteurs, etc.
3. **Nettoyer et normaliser** les données
4. **Sauvegarder en base MySQL** pour l'analyse

#### Contraintes techniques
- **Respect du robots.txt** : On ne spamme pas les sites
- **Délais entre requêtes** : 1 seconde minimum entre chaque page
- **Gestion des erreurs** : Si une page échoue, on continue
- **Limitation de bande passante** : Pas plus de 10 requêtes par seconde

#### Environnements
- **Développement** : Local avec Docker
- **Production** : VM GCP avec conteneurs Docker
- **Base de données** : MySQL 8.0

### ⚠️ Gestion des erreurs et exceptions

#### Types d'erreurs courantes
```python
# 1. Erreurs de connexion
try:
    response = requests.get(url)
except ConnectionError:
    logging.error(f"Impossible de se connecter à {url}")
    time.sleep(30)  # Attendre et réessayer

# 2. Erreurs de parsing HTML
try:
    titre = response.css('h1.titre::text').get()
    if not titre:
        titre = response.css('.movie-title::text').get()  # Fallback
except Exception as e:
    logging.error(f"Erreur parsing titre: {e}")
    titre = "Titre non trouvé"

# 3. Erreurs de base de données
try:
    self.cursor.execute(query, params)
except mysql.connector.Error as e:
    logging.error(f"Erreur MySQL: {e}")
    self.reconnect_database()
```

#### Procédures de récupération
```bash
# Redémarrage automatique
docker-compose --profile scraping up scraper-service --build

# Nettoyage de la base
./automatisation/clean_db_manual.py

# Logs de débogage
docker logs -f scraper-service
```

### 🔄 Versioning des scripts

#### Structure Git


#### Gestion des versions
```bash
# Numérotation : MAJOR.MINOR.PATCH
# Exemple : 2.1.3 (2=majeur, 1=fonctionnalité, 3=bug)

# Créer une branche
git checkout -b feature/nouveau-spider

# Créer un tag
git tag -a v2.0.0 -m "Version 2.0.0 - Nouveau spider Allociné"
```

---

## C2 - Développer des requêtes SQL

### 📊 Modèle conceptuel Merise

#### Entités principales


#### Relations
- **FILM** ←→ **PARTICIPATION** (1:N)
- **PERSONNE** ←→ **PARTICIPATION** (1:N)
- **FILM** ←→ **PREDICTION** (1:N)

### �� Requêtes SQL optimisées

#### 1. Requête de base - Films avec acteurs
```sql
-- Requête optimisée avec index sur titre et genre
SELECT 
    f.id_film,
    f.titre,
    f.genre,
    f.duree,
    GROUP_CONCAT(p.nom SEPARATOR ', ') as acteurs
FROM table_films f
LEFT JOIN table_participations part ON f.id_film = part.id_film
LEFT JOIN table_personnes p ON part.id_personne = p.id_personne
WHERE part.role = 'acteur'
GROUP BY f.id_film
ORDER BY f.date_sortie DESC;
```

#### 2. Requête de statistiques
```sql
-- Statistiques par genre avec index sur genre
SELECT 
    genre,
    COUNT(*) as nombre_films,
    AVG(duree) as duree_moyenne,
    SUM(entrees) as total_entrees
FROM table_films 
WHERE genre IS NOT NULL
GROUP BY genre
HAVING nombre_films > 5
ORDER BY total_entrees DESC;
```

#### 3. Requête de prédictions
```sql
-- Films sans prédiction (pour le pipeline ML)
SELECT 
    f.*,
    GROUP_CONCAT(CASE WHEN p.role = 'acteur' THEN pe.nom END) as acteurs,
    GROUP_CONCAT(CASE WHEN p.role = 'realisateur' THEN pe.nom END) as realisateurs
FROM table_films f
LEFT JOIN table_predictions pred ON f.id_film = pred.id_film
LEFT JOIN table_participations p ON f.id_film = p.id_film
LEFT JOIN table_personnes pe ON p.id_personne = pe.id_personne
WHERE pred.id_prediction IS NULL
GROUP BY f.id_film;
```

### ⚡ Optimisations appliquées

#### Index créés
```sql
-- Index pour améliorer les performances
CREATE INDEX idx_films_titre ON table_films(titre);
CREATE INDEX idx_films_genre ON table_films(genre);
CREATE INDEX idx_films_date ON table_films(date_sortie);
CREATE INDEX idx_participations_role ON table_participations(role);
CREATE INDEX idx_predictions_film ON table_predictions(id_film);
```

#### Justification des optimisations
- **Index sur titre** : Recherche rapide par nom de film
- **Index sur genre** : Filtrage et groupement par genre
- **Index sur date** : Tri chronologique des films
- **Index sur role** : Filtrage acteurs/réalisateurs
- **Index sur id_film** : Jointures optimisées

---

## C3 - Développer des règles d'agrégation

### 🧹 Script d'agrégation principal

#### Fichier : `fictif/load_csv_to_db.py`
```python
class CSVToDBLoader:
    """Classe pour charger des données CSV dans la base de données MySQL"""
    
    def load_csv_data(self, csv_file_path):
        """
        Charge les données depuis un fichier CSV vers la table film_fictif
        
        Règles d'agrégation appliquées :
        1. Nettoyage des valeurs manquantes
        2. Conversion des types de données
        3. Normalisation des chaînes de caractères
        4. Gestion des doublons
        """
```

#### Règles de nettoyage appliquées

##### 1. Gestion des valeurs manquantes
```python
# Règle : Remplacer les valeurs manquantes par des valeurs par défaut
if pd.isna(row['budget']):
    budget = 0
else:
    budget = int(row['budget'])

if pd.isna(row['genre']):
    genre = "Inconnu"
else:
    genre = str(row['genre']).strip()
```

##### 2. Normalisation des chaînes
```python
# Règle : Nettoyer et normaliser les chaînes
def clean_text(text):
    if pd.isna(text):
        return None
    return str(text).strip().lower().capitalize()

# Application
titre = clean_text(row['titre'])
pays = clean_text(row['pays'])
```

##### 3. Conversion des types
```python
# Règle : Convertir les types selon les contraintes de la base
def convert_entrees(entrees):
    if pd.isna(entrees):
        return None
    try:
        return int(float(entrees))
    except:
        return None

# Application
entrees = convert_entrees(row['entrees_premiere_semaine'])
```

### �� Pipeline de nettoyage Scrapy

#### Fichier : `automatisation/imdb/pipelines.py`
```python
class NewFilmsPipeline:
    def process_item(self, item, spider):
        """
        Pipeline de nettoyage des données extraites
        
        Règles appliquées :
        1. Suppression des champs inutiles
        2. Extraction des genres depuis HTML
        3. Nettoyage des dates
        4. Normalisation des durées
        """
```

#### Règles de nettoyage spécifiques

##### 1. Extraction des genres
```python
# Règle : Extraire le premier genre depuis le HTML
if "duree" in item and isinstance(item["duree"], str):
    selector = Selector(text=item["duree"])
    genres = selector.css("span.dark-grey-link::text").getall()
    item["genre"] = genres[0] if genres else None
```

##### 2. Nettoyage des dates
```python
# Règle : Convertir les dates françaises en format ISO
def convert_date(self, date_str):
    try:
        return datetime.strptime(date_str, '%d %B %Y').strftime('%Y-%m-%d')
    except ValueError:
        # Gestion des mois français
        french_to_english = {
            'janvier': 'January', 'février': 'February', 'mars': 'March'
        }
        for fr, en in french_to_english.items():
            if fr in date_str:
                date_str = date_str.replace(fr, en)
                break
        return datetime.strptime(date_str, '%d %B %Y').strftime('%Y-%m-%d')
```

##### 3. Normalisation des durées
```python
# Règle : Convertir "2h 30min" en minutes
def clean_duration(self, duration_html):
    if duration_html:
        match = re.search(r'(\d+)h\s*(\d+)min', duration_html)
        if match:
            hours, minutes = match.groups()
            return int(hours) * 60 + int(minutes)
    return None
```

### 📊 Logique d'agrégation

#### Algorithme de traitement
1. **Extraction** : Récupération des données brutes
2. **Validation** : Vérification de la cohérence
3. **Nettoyage** : Suppression des anomalies
4. **Transformation** : Conversion des formats
5. **Agrégation** : Regroupement des données
6. **Sauvegarde** : Stockage en base

#### Gestion des dépendances
```python
# Dépendances requises
requirements = [
    'pandas>=1.5.0',
    'mysql-connector-python>=8.0.0',
    'python-dotenv>=0.19.0'
]
```

---

## C4 - Créer une base de données (RGPD)

### ��️ Modèle conceptuel Merise

#### Diagramme conceptuel


#### Modèle physique
```sql
-- Table principale des films
CREATE TABLE table_films (
    id_film INT AUTO_INCREMENT PRIMARY KEY,
    titre VARCHAR(255) NOT NULL,
    duree INT,
    salles INT,
    genre VARCHAR(255),
    date_sortie DATE,
    pays VARCHAR(255),
    studio VARCHAR(255),
    description TEXT,
    image VARCHAR(255),
    budget INT,
    entrees INT,
    is_pred BOOLEAN DEFAULT FALSE
);

-- Table des personnes (acteurs/réalisateurs)
CREATE TABLE table_personnes (
    id_personne INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL
);

-- Table de liaison films-personnes
CREATE TABLE table_participations (
    id_film INT,
    id_personne INT,
    role ENUM('acteur', 'realisateur') NOT NULL,
    PRIMARY KEY (id_film, id_personne, role),
    FOREIGN KEY (id_film) REFERENCES table_films(id_film) ON DELETE CASCADE,
    FOREIGN KEY (id_personne) REFERENCES table_personnes(id_personne) ON DELETE CASCADE
);

-- Table des prédictions
CREATE TABLE table_predictions (
    id_prediction INT AUTO_INCREMENT PRIMARY KEY,
    id_film INT NOT NULL,
    prediction_entrees INT NOT NULL,
    date_prediction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_film) REFERENCES table_films(id_film) ON DELETE CASCADE
);
```

### 🔐 Conformité RGPD

#### Registre des traitements
| Traitement | Finalité | Base légale | Données | Conservation |
|------------|----------|-------------|---------|--------------|
| Scraping films | Analyse prédictive | Intérêt légitime | Données publiques films | 2 ans |
| Prédictions IA | Amélioration modèle | Intérêt légitime | Données agrégées | 1 an |
| Utilisateurs API | Authentification | Consentement | Login/mot de passe | 6 mois |

#### Procédures de conformité RGPD

##### 1. Droit à l'effacement
```sql
-- Procédure pour supprimer un film et ses données associées
DELIMITER //
CREATE PROCEDURE SupprimerFilm(IN film_id INT)
BEGIN
    DELETE FROM table_predictions WHERE id_film = film_id;
    DELETE FROM table_participations WHERE id_film = film_id;
    DELETE FROM table_films WHERE id_film = film_id;
END //
DELIMITER ;
```

##### 2. Droit d'accès
```sql
-- Procédure pour exporter les données d'un film
DELIMITER //
CREATE PROCEDURE ExporterDonneesFilm(IN film_id INT)
BEGIN
    SELECT 
        f.*,
        GROUP_CONCAT(p.nom) as acteurs,
        pred.prediction_entrees
    FROM table_films f
    LEFT JOIN table_participations part ON f.id_film = part.id_film
    LEFT JOIN table_personnes p ON part.id_personne = p.id_personne
    LEFT JOIN table_predictions pred ON f.id_film = pred.id_film
    WHERE f.id_film = film_id
    GROUP BY f.id_film;
END //
DELIMITER ;
```

##### 3. Procédures automatisées
```bash
#!/bin/bash
# Script de nettoyage automatique des données anciennes

# Supprimer les prédictions de plus d'1 an
mysql -u kevin -p cinapps -e "
DELETE FROM table_predictions 
WHERE date_prediction < DATE_SUB(NOW(), INTERVAL 1 YEAR);
"

# Supprimer les films sans prédiction de plus de 2 ans
mysql -u kevin -p cinapps -e "
DELETE FROM table_films 
WHERE date_sortie < DATE_SUB(NOW(), INTERVAL 2 YEAR)
AND is_pred = FALSE;
"
```

### 📦 Procédures d'installation

#### Script d'installation automatique
```bash
#!/bin/bash
# install_database.sh

echo "�� Installation de la base de données CinApps..."

# 1. Créer la base de données
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS cinapps;"

# 2. Créer l'utilisateur
mysql -u root -p -e "
CREATE USER IF NOT EXISTS 'kevin'@'%' IDENTIFIED BY 'kevinpass';
GRANT ALL PRIVILEGES ON cinapps.* TO 'kevin'@'%';
FLUSH PRIVILEGES;
"

# 3. Importer le schéma
mysql -u kevin -pkevinpass cinapps < mysql-init/init_bdd_app.sql

# 4. Vérifier l'installation
mysql -u kevin -pkevinpass cinapps -e "SHOW TABLES;"

echo "✅ Base de données installée avec succès!"
```

#### Script d'import des données
```python
# import_data.py
import mysql.connector
import pandas as pd

def import_csv_to_db(csv_file, table_name):
    """
    Importe un fichier CSV dans la base de données
    
    Args:
        csv_file (str): Chemin vers le fichier CSV
        table_name (str): Nom de la table cible
    """
    # Lire le CSV
    df = pd.read_csv(csv_file)
    
    # Connexion à la base
    conn = mysql.connector.connect(
        host='localhost',
        user='kevin',
        password='kevinpass',
        database='cinapps'
    )
    
    # Import des données
    for index, row in df.iterrows():
        # Logique d'import selon la table
        pass
    
    conn.close()
```

---

## C5 - Développer une API REST

### 📚 Documentation technique complète

#### Architecture de l'API


#### Endpoints principaux

##### 1. Authentification
```python
# POST /auth/token
{
    "username": "chouchou",
    "password": "chouchou123"
}

# Réponse
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
}
```

##### 2. Films
```python
# GET /films/ (avec JWT)
Authorization: Bearer <token>

# Réponse
[
    {
        "id_film": 1,
        "titre": "Nobody 2",
        "duree": 89,
        "genre": "Action",
        "date_sortie": "2025-01-15",
        "pays": "U.S.A.",
        "studio": "Universal",
        "budget": 50000000,
        "entrees": 1500000
    }
]

# POST /films/ (créer un film)
{
    "titre": "Nouveau Film",
    "duree": 120,
    "genre": "Drame",
    "date_sortie": "2025-06-01",
    "pays": "France",
    "studio": "Pathé",
    "budget": 3000000
}
```

##### 3. Prédictions
```python
# POST /prediction/
{
    "id_film": 1,
    "budget": 50000000,
    "duree": 89,
    "genre": "Action",
    "pays": "U.S.A.",
    "salles_premiere_semaine": 281,
    "scoring_acteurs_realisateurs": 2.5,
    "coeff_studio": 1,
    "year": 2025,
    "is_fictif": false
}

# Réponse
{
    "prediction": 1500000,
    "confidence": 0.85
}
```

### 🔐 Authentification et autorisation

#### Système JWT
```python
# Configuration JWT
SECRET_KEY = "votre_clé_secrète_très_longue"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Création du token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Vérification du token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")
```

#### Règles d'autorisation
```python
# Décorateur pour protéger les endpoints
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return username

# Utilisation
@router.get("/films/")
async def get_films(current_user: str = Depends(get_current_user)):
    # Seuls les utilisateurs authentifiés peuvent accéder
    return get_all_films()
```

### �� Documentation OpenAPI/Swagger

#### Configuration Swagger
```python
# main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="CinApps API",
    description="API pour la gestion des films et prédictions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="CinApps API",
        version="1.0.0",
        description="API complète pour CinApps",
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

#### Modèles Pydantic
```python
# models.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class FilmBase(BaseModel):
    titre: str = Field(..., description="Titre du film", max_length=255)
    duree: Optional[int] = Field(None, description="Durée en minutes", ge=1)
    genre: Optional[str] = Field(None, description="Genre du film", max_length=100)
    date_sortie: Optional[date] = Field(None, description="Date de sortie")
    pays: Optional[str] = Field(None, description="Pays de production", max_length=100)
    studio: Optional[str] = Field(None, description="Studio de production", max_length=100)
    budget: Optional[int] = Field(None, description="Budget en euros", ge=0)
    entrees: Optional[int] = Field(None, description="Nombre d'entrées", ge=0)

class FilmCreate(FilmBase):
    pass

class Film(FilmBase):
    id_film: int
    
    class Config:
        from_attributes = True

class PredictionRequest(BaseModel):
    id_film: int
    budget: float = Field(..., description="Budget du film")
    duree: int = Field(..., description="Durée en minutes")
    genre: str = Field(..., description="Genre du film")
    pays: str = Field(..., description="Pays de production")
    salles_premiere_semaine: int = Field(..., description="Nombre de salles")
    scoring_acteurs_realisateurs: float = Field(..., description="Score des acteurs")
    coeff_studio: int = Field(..., description="Coefficient studio")
    year: int = Field(..., description="Année de sortie")
    is_fictif: bool = Field(False, description="Film fictif ou réel")
```

### 🛡️ Sécurité OWASP Top 10

#### 1. Injection SQL
```python
# ✅ Bonne pratique - Utilisation de paramètres
def get_film_by_id(film_id: int):
    query = "SELECT * FROM table_films WHERE id_film = %s"
    cursor.execute(query, (film_id,))  # Paramètre sécurisé

# ❌ Mauvaise pratique - Concaténation directe
def get_film_by_id_unsafe(film_id: int):
    query = f"SELECT * FROM table_films WHERE id_film = {film_id}"  # DANGEREUX
```

#### 2. Authentification cassée
```python
# ✅ Bonne pratique - Hachage des mots de passe
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
```

#### 3. Exposition de données sensibles
```python
# ✅ Bonne pratique - Masquage des données sensibles
class UserResponse(BaseModel):
    id: int
    username: str
    # password: str  # ❌ Ne jamais exposer le mot de passe
    
    class Config:
        from_attributes = True
```

### 📊 Tests de l'API

#### Tests unitaires
```python
# test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_films_without_auth():
    """Test que l'accès sans authentification est refusé"""
    response = client.get("/films/")
    assert response.status_code == 401

def test_get_films_with_auth():
    """Test que l'accès avec authentification fonctionne"""
    # Obtenir un token
    auth_response = client.post("/auth/token", data={
        "username": "chouchou",
        "password": "chouchou123"
    })
    token = auth_response.json()["access_token"]
    
    # Utiliser le token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/films/", headers=headers)
    assert response.status_code == 200

def test_create_film():
    """Test de création d'un film"""
    # Authentification
    auth_response = client.post("/auth/token", data={
        "username": "chouchou",
        "password": "chouchou123"
    })
    token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Création du film
    film_data = {
        "titre": "Test Film",
        "duree": 120,
        "genre": "Action",
        "pays": "France"
    }
    response = client.post("/films/", json=film_data, headers=headers)
    assert response.status_code == 201
```

#### Tests d'intégration
```bash
#!/bin/bash
# test_integration.sh

echo "🧪 Tests d'intégration de l'API..."

# 1. Test de l'authentification
echo "Test authentification..."
curl -X POST "http://localhost:8002/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=chouchou&password=chouchou123"

# 2. Test de récupération des films
echo "Test récupération films..."
TOKEN=$(curl -s -X POST "http://localhost:8002/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=chouchou&password=chouchou123" | jq -r '.access_token')

curl -X GET "http://localhost:8002/films/" \
  -H "Authorization: Bearer $TOKEN"

echo "✅ Tests d'intégration terminés!"
```

---

## 📞 Support et contacts

### En cas de problème
1. **Vérifier les logs** : `docker logs cinapps-api`
2. **Tester l'API** : `curl http://localhost:8002/health`
3. **Vérifier la base** : `mysql -u kevin -p cinapps`
4. **Contacter l'équipe** : dev@cinapps.com

### Ressources utiles
- **Documentation FastAPI** : https://fastapi.tiangolo.com/
- **Documentation JWT** : https://jwt.io/
- **Guide OWASP** : https://owasp.org/www-project-top-ten/

---

*Documentation créée le 13/08/2025 - Version 1.0*
*Projet CinApps - Gestion des données*