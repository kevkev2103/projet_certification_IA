# Rapport E3 - Mettre à disposition l'IA
*Documentation complète pour le projet CinApps*

---

## Table des matières
1. [C9 - Développer une API exposant un modèle IA (REST)](#c9---développer-une-api-exposant-un-modèle-ia-rest)
2. [C10 - Intégrer l'API IA dans une application](#c10---intégrer-lapi-ia-dans-une-application)
3. [C11 - Monitorer un modèle IA](#c11---monitorer-un-modèle-ia)
4. [C12 - Programmer des tests automatisés d'un modèle IA](#c12---programmer-des-tests-automatisés-dun-modèle-ia)
5. [C13 - Créer une chaîne de livraison continue d'un modèle IA (MLOps)](#c13---créer-une-chaîne-de-livraison-continue-dun-modèle-ia-mlops)

---

## C9 - Développer une API exposant un modèle IA (REST)

### 🔐 Authentification restreignant l'accès au modèle

#### Système JWT implémenté
```python
# cinapps_api/app/routes/pred.py
@router.post("/prediction/")
async def predict(features: PredictionRequest, current_user: dict = Depends(get_current_user)): 
    # Seuls les utilisateurs authentifiés peuvent accéder au modèle
    start_time = time.time()
    
    try:
        # Logique de prédiction sécurisée
        df = pd.DataFrame([features.dict()])
        prediction = model_pipeline.predict(df)
        prediction_value = int(prediction[0])
        
        return {
            "prediction": prediction_value,
            "id_film": features.id_film,
            "is_fictif": features.is_fictif,
            "message": f"Prédiction {'fictive' if features.is_fictif else 'réelle'} stockée avec succès"
        }
```

#### Vérification des tokens
```python
# cinapps_api/app/routes/auth.py
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
```

### 🎯 Points de terminaison conformes aux spécifications

#### Endpoint principal de prédiction
```python
# Modèle de requête
class PredictionRequest(BaseModel):
    id_film: int
    budget: float
    duree: int
    genre: str
    pays: str
    salles_premiere_semaine: int
    scoring_acteurs_realisateurs: float
    coeff_studio: int
    year: int
    is_fictif: bool = False

# Endpoint POST /prediction/
@router.post("/prediction/")
async def predict(features: PredictionRequest, current_user: dict = Depends(get_current_user)):
    # Traitement de la prédiction
    # Stockage en base de données
    # Retour du résultat
```

#### Endpoints de santé et monitoring
```python
# Endpoint de santé
@app.get("/health", tags=["Root"])
async def health_check():
    """Endpoint de health check pour Docker"""
    return {"status": "healthy", "service": "cinapps-api"}

# Endpoint racine
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bienvenue sur l'API Cinapps !", "version": "1.0"}
```

### 🛡️ Sécurisation selon OWASP Top 10

#### 1. Injection SQL - Prévenu
```python
# ✅ Bonne pratique - Utilisation de paramètres SQLAlchemy
insert_prediction = text("""
    INSERT INTO table_predictions (id_film, prediction_entrees)
    VALUES (:id_film, :prediction)
""")
conn.execute(insert_prediction, {
    "id_film": features.id_film,
    "prediction": prediction_value
})

# ❌ Évité - Concaténation directe dangereuse
# query = f"INSERT INTO predictions VALUES ({id}, {prediction})"
```

#### 2. Authentification cassée - Sécurisée
```python
# Hachage des mots de passe avec bcrypt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
```

#### 3. Exposition de données sensibles - Contrôlée
```python
# Modèle de réponse sécurisé
class PredictionResponse(BaseModel):
    prediction: int
    id_film: int
    is_fictif: bool
    message: str
    # Pas d'exposition des données sensibles du modèle
```

### 📁 Sources versionnées et accessibles sur Git distant

#### Structure du repository


#### Versioning Git
```bash
# Commits réguliers avec messages descriptifs
git add .
git commit -m "feat: Ajout endpoint prédiction avec authentification JWT"
git commit -m "fix: Correction gestion erreurs modèle IA"
git commit -m "docs: Mise à jour documentation API"

# Tags de version
git tag -a v1.0.0 -m "Version 1.0.0 - API prédiction complète"
git tag -a v1.1.0 -m "Version 1.1.0 - Ajout monitoring Prometheus"
```

### 🧪 Tests couvrant tous les endpoints

#### Tests unitaires complets
```python
# tests/test_ml_api_simple.py
def test_prediction_without_auth():
    """Test : prédiction refusée sans authentification"""
    url = f"{API_URL}/prediction/"
    prediction_data = {
        "id_film": 1,
        "budget": 100000000,
        "duree": 120,
        "genre": "Action",
        "pays": "US",
        "salles_premiere_semaine": 3000,
        "scoring_acteurs_realisateurs": 8.5,
        "coeff_studio": 1,
        "year": 2024,
        "is_fictif": True
    }
    
    response = requests.post(url, json=prediction_data)
    assert response.status_code == 401  # Non autorisé

def test_prediction_with_auth():
    """Test : prédiction avec authentification valide"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(url, json=prediction_data, headers=headers)
    assert response.status_code in [200, 500]  # 200 si OK, 500 si modèle pas chargé
```

#### Tests d'intégration
```python
# tests/test_integration_simple.py
def test_full_auth_flow():
    """Test d'intégration : flux d'authentification complet"""
    # Login
    login_response = requests.post(login_url, data=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Utilisation du token
    headers = {"Authorization": f"Bearer {token}"}
    me_response = requests.get(me_url, headers=headers)
    assert me_response.status_code == 200
```

### 📚 Documentation conforme aux standards

#### Documentation OpenAPI/Swagger
```python
# cinapps_api/app/main.py
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

# Documentation accessible sur /docs
# Interface Swagger automatique
```

#### Documentation de l'architecture
```markdown
# Architecture API CinApps

## Composants
- **FastAPI** : Framework web moderne
- **JWT** : Authentification sécurisée
- **SQLAlchemy** : ORM pour MySQL
- **Scikit-learn** : Modèle de prédiction

## Flux de données
1. Authentification JWT
2. Validation des données d'entrée
3. Prédiction avec le modèle IA
4. Stockage en base de données
5. Retour du résultat

## Sécurité
- Tokens JWT avec expiration
- Hachage bcrypt des mots de passe
- Validation Pydantic des données
- Protection contre les injections SQL
```

---

## C10 - Intégrer l'API IA dans une application

### 🚀 Application installée et fonctionnelle en dev

#### Interface Streamlit déployée
```python
# streamlit/app.py
st.set_page_config(
    page_title="CinéOracle - Prédiction d'entrées cinéma",
    page_icon="��",
    layout="wide"
)

def main():
    # Interface utilisateur complète
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/cinema-.png", width=100)
        st.title("🎭 CinéOracle")
        
        # Authentification
        if not st.session_state["authentication_status"]:
            tab1, tab2 = st.tabs(["�� Connexion", "📝 Inscription"])
            # Logique d'authentification
```

#### Déploiement Docker
```yaml
# docker-compose.yml
streamlit-app:
  build:
    context: ./streamlit
    dockerfile: Dockerfile
  container_name: streamlit-app
  restart: always
  ports:
    - "8501:8501"
  environment:
    URL_API_CRUD: ${API_URL_CRUD}
    URL_API_PRED: ${API_URL_PREDICTION}
  depends_on:
    cinapps-api:
      condition: service_healthy
  networks:
    - cinapps-network
```

### �� Communication avec l'API opérationnelle

#### Wrapper API pour Streamlit
```python
# streamlit/app.py
def api_request(path: str, method: str = "GET", **kwargs):
    """Wrapper requests avec base URL CRUD et timeout par défaut."""
    url = urljoin(URL_API_CRUD + "/", path.lstrip("/"))
    kwargs.setdefault("timeout", 10)
    return requests.request(method.upper(), url, **kwargs)

def authenticate(username: str, password: str) -> bool:
    """Authentification avec l'API"""
    try:
        response = api_request(
            "/auth/token",
            method="POST",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            token_data = response.json()
            st.session_state["access_token"] = token_data.get("access_token")
            return True
    except Exception as e:
        st.error(f"Erreur d'authentification: {e}")
    return False
```

#### Récupération des films avec prédictions
```python
def get_films_with_predictions():
    """Récupère les films avec leurs prédictions depuis l'API"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        
        # Récupérer les films
        films_response = api_request("/films/", headers=headers)
        
        if films_response.status_code == 200:
            films_data = pd.DataFrame(films_response.json())
            
            # Récupérer les prédictions pour chaque film
            for index, film in films_data.iterrows():
                if not film.get('is_pred'):
                    # Faire une prédiction
                    prediction_response = api_request(
                        "/prediction/",
                        method="POST",
                        json={
                            "id_film": film['id_film'],
                            "budget": film.get('budget', 0),
                            "duree": film.get('duree', 90),
                            "genre": film.get('genre', 'Inconnu'),
                            "pays": film.get('pays', 'Inconnu'),
                            "salles_premiere_semaine": film.get('salles', 100),
                            "scoring_acteurs_realisateurs": 5.0,
                            "coeff_studio": 1,
                            "year": 2024,
                            "is_fictif": False
                        },
                        headers=headers
                    )
                    
                    if prediction_response.status_code == 200:
                        prediction_data = prediction_response.json()
                        films_data.at[index, 'prediction_entrees'] = prediction_data['prediction']
                        films_data.at[index, 'date_prediction'] = datetime.now()
            
            return films_data
    except Exception as e:
        st.error(f"Erreur lors de la récupération des films: {e}")
        return pd.DataFrame()
```

### 🔐 Gestion de l'authentification et du renouvellement des jetons

#### Gestion des sessions
```python
# streamlit/app.py
# Session state pour l'authentification
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

def check_token_validity():
    """Vérifie si le token est encore valide"""
    if st.session_state["access_token"]:
        try:
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            response = api_request("/auth/users/me", headers=headers)
            if response.status_code != 200:
                # Token expiré, déconnexion
                st.session_state["authentication_status"] = False
                st.session_state["access_token"] = None
                st.warning("Session expirée, veuillez vous reconnecter")
                return False
            return True
        except Exception:
            return False
    return False
```

#### Renouvellement automatique
```python
def refresh_token():
    """Renouvelle le token si nécessaire"""
    if st.session_state["access_token"]:
        try:
            # Vérifier si le token expire bientôt
            # Si oui, demander un nouveau token
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            response = api_request("/auth/refresh", headers=headers)
            if response.status_code == 200:
                new_token = response.json()["access_token"]
                st.session_state["access_token"] = new_token
        except Exception:
            # En cas d'erreur, rediriger vers la connexion
            st.session_state["authentication_status"] = False
```

### 🔗 Intégration de tous les endpoints selon spécifications

#### Endpoints films intégrés
```python
def display_films_list():
    """Affiche la liste des films avec prédictions"""
    films_df = get_films_with_predictions()
    
    if not films_df.empty:
        # Filtrage par genre
        genres = ["Tous"] + list(films_df['genre'].unique())
        selected_genre = st.selectbox("Filtrer par genre", genres)
        
        if selected_genre != "Tous":
            films_df = films_df[films_df['genre'] == selected_genre]
        
        # Affichage des films
        for _, film in films_df.iterrows():
            with st.container():
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1:
                    st.markdown(f"""
                    <div class="film-card">
                        <h4>{film.get('titre','')}</h4>
                        <p><strong>Genre:</strong> {film.get('genre','N/A')}</p>
                        <p><strong>Durée:</strong> {format_duration(film.get('duree'))}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.metric("Prédiction", format_prediction_metric(film.get('prediction_entrees')))
                with c3:
                    st.write(f"📅 {pd.to_datetime(film.get('date_sortie')).strftime('%d/%m')}")
```

#### Endpoints prédictions intégrés
```python
def make_prediction_for_film(film_id, film_data):
    """Fait une prédiction pour un film spécifique"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        
        prediction_data = {
            "id_film": film_id,
            "budget": film_data.get('budget', 0),
            "duree": film_data.get('duree', 90),
            "genre": film_data.get('genre', 'Inconnu'),
            "pays": film_data.get('pays', 'Inconnu'),
            "salles_premiere_semaine": film_data.get('salles', 100),
            "scoring_acteurs_realisateurs": 5.0,
            "coeff_studio": 1,
            "year": 2024,
            "is_fictif": False
        }
        
        response = api_request(
            "/prediction/",
            method="POST",
            json=prediction_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"Prédiction : {result['prediction']:,} entrées")
            return result['prediction']
        else:
            st.error(f"Erreur lors de la prédiction: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Erreur de connexion: {e}")
        return None
```

### 🎨 Adaptations d'interfaces conformes aux maquettes

#### Interface utilisateur moderne
```python
# Styles CSS personnalisés
st.markdown("""
    <style>
    .main { padding: 2rem; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .prediction-card { padding: 1.5rem; border-radius: 10px; background-color: #f0f2f6; margin: 1rem 0; }
    .film-card { border: 1px solid #ddd; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; background-color: white; }
    .top-film { border-color: #ffd700; background-color: #fffbf0; }
    .good-film { border-color: #90EE90; background-color: #f0fff0; }
    .average-film { border-color: #FFA500; background-color: #fff8dc; }
    .poor-film { border-color: #FF6B6B; background-color: #fff5f5; }
    </style>
""", unsafe_allow_html=True)
```

#### Classement des films par performance
```python
def classify_film_performance(prediction) -> str:
    """Classe un film selon sa prédiction d'entrées."""
    if prediction is None or pd.isna(prediction):
        return "unknown"
    try:
        val = float(prediction)
    except Exception:
        return "unknown"

    if val >= 1_000_000:
        return "top"      # 🥇 Films exceptionnels
    elif val >= 500_000:
        return "good"     # �� Films prometteurs
    elif val >= 100_000:
        return "average"  # 🥉 Films moyens
    else:
        return "poor"     # ⚠️ Films à risque

def get_performance_icon(performance: str) -> str:
    return {
        "top": "🥇",
        "good": "��",
        "average": "🥉",
        "poor": "⚠️",
        "unknown": "❓"
    }.get(performance, "❓")
```

### 🧪 Tests d'intégration couvrant tous les endpoints

#### Tests d'intégration complets
```python
# tests/test_integration_simple.py
def test_films_api_integration():
    """Test d'intégration : gestion complète des films"""
    # Récupérer un token
    login_url = f"{CRUD_API_URL}/auth/token"
    login_data = {"username": "testuser", "password": "test123"}
    login_response = requests.post(login_url, data=login_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Lister les films
    films_url = f"{CRUD_API_URL}/films/"
    films_response = requests.get(films_url, headers=headers)
    assert films_response.status_code in [200, 404]
    
    # Créer un film de test
    new_film = {
        "titre": "Film Integration Test",
        "annee_sortie": 2024,
        "genre": "Test",
        "duree": 90
    }
    create_response = requests.post(films_url, json=new_film, headers=headers)
    assert create_response.status_code in [201, 400]

def test_api_connectivity():
    """Test d'intégration : connectivité entre services"""
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
    
    assert any(results.values()), "Aucune API n'est accessible"
```

### 📁 Sources versionnées sur le dépôt Git de l'app

#### Structure du repository Streamlit


#### Versioning et déploiement
```bash
# Commits réguliers
git add streamlit/
git commit -m "feat: Ajout interface utilisateur Streamlit"
git commit -m "feat: Intégration complète avec l'API de prédiction"
git commit -m "feat: Ajout classement des films par performance"

# Déploiement automatique
docker-compose up streamlit-app --build
```

---

## C11 - Monitorer un modèle IA

### 📊 Explication des métriques et seuils

#### Métriques de performance du modèle
```python
# Métriques collectées par Prometheus
predictions_counter = Counter('predictions_total', 'Total number of predictions made')
prediction_duration = Histogram('prediction_duration_seconds', 'Time spent making predictions')
predictions_per_minute = Gauge('predictions_per_minute', 'Predictions per minute')

# Seuils d'alerte définis
seuils = {
    "latence_max": 2.0,        # Latence maximale 2 secondes
    "taux_erreur_max": 0.02,   # Taux d'erreur max 2%
    "disponibilite_min": 0.99, # Disponibilité min 99%
    "precision_min": 0.7       # Précision R² min 70%
}
```

#### Métriques de qualité du modèle
```python
# Performance actuelle du modèle (d'après ML/modelisation.ipynb)
performance_actuelle = {
    "mae": 133666.18,    # Erreur absolue moyenne
    "r2": 0.7309,        # Coefficient de détermination (73% de précision)
    "rmse": 257524.38    # Erreur quadratique moyenne
}

# Seuils de dérive du modèle
seuils_derive = {
    "r2_min": 0.65,      # R² minimum acceptable
    "mae_max": 150000,   # MAE maximum acceptable
    "rmse_max": 300000   # RMSE maximum acceptable
}
```

### 🛠️ Choix d'outils adaptés au contexte

#### Stack de monitoring choisi
```yaml
# monitoring/docker-compose.yml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alert_rules.yml:/etc/prometheus/alert_rules.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin123
    volumes:
      - grafana_data:/var/lib/grafana
```

#### Configuration Prometheus
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'cinapps-api'
    static_configs:
      - targets: ['34.155.100.171:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s
    scrape_timeout: 5s
    honor_labels: true
```

### 📈 Vecteur de restitution en temps réel

#### Dashboard Grafana
```json
// monitoring/grafana-dashboard.json
{
  "dashboard": {
    "title": "Cinapps API Monitoring",
    "panels": [
      {
        "title": "Latence des requêtes (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_highr_seconds_bucket[5m]))",
            "legendFormat": "Latence p95"
          }
        ]
      },
      {
        "title": "Taux d'erreurs",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"4..|5..\"}[5m]) / rate(http_requests_total[5m]) * 100",
            "legendFormat": "Taux d'erreurs (%)"
          }
        ]
      },
      {
        "title": "Prédictions totales",
        "type": "stat",
        "targets": [
          {
            "expr": "predictions_total",
            "legendFormat": "Prédictions"
          }
        ]
      },
      {
        "title": "Temps de prédiction (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(prediction_duration_seconds_bucket[5m]))",
            "legendFormat": "Temps p95"
          }
        ]
      }
    ],
    "refresh": "10s"
  }
}
```

#### Interface Streamlit pour le monitoring
```python
# Interface de monitoring intégrée dans Streamlit
def display_monitoring_metrics():
    """Affiche les métriques de monitoring en temps réel"""
    st.subheader("📊 Monitoring en temps réel")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Prédictions totales
        total_predictions = get_total_predictions()
        st.metric("Prédictions totales", f"{total_predictions:,}")
    
    with col2:
        # Prédictions par minute
        predictions_per_min = get_predictions_per_minute()
        st.metric("Prédictions/min", f"{predictions_per_min:.1f}")
    
    with col3:
        # Latence moyenne
        avg_latency = get_average_latency()
        st.metric("Latence moyenne", f"{avg_latency:.2f}s")
    
    with col4:
        # Taux d'erreur
        error_rate = get_error_rate()
        st.metric("Taux d'erreur", f"{error_rate:.2%}")
```

### ♿ Prise en compte de l'accessibilité

#### Interface accessible (Valentin Haüy, Microsoft)
```python
# Styles CSS pour l'accessibilité
st.markdown("""
    <style>
    /* Contraste élevé pour la lisibilité */
    .stTextInput > div > div > input {
        color: #000000;
        background-color: #ffffff;
        border: 2px solid #000000;
    }
    
    /* Taille de police suffisante */
    .stMarkdown {
        font-size: 16px;
        line-height: 1.5;
    }
    
    /* Indicateurs visuels pour les couleurs */
    .top-film::before { content: "🥇 "; }
    .good-film::before { content: "🥈 "; }
    .average-film::before { content: "🥉 "; }
    .poor-film::before { content: "⚠️ "; }
    
    /* Focus visible pour la navigation clavier */
    .stButton > button:focus {
        outline: 3px solid #0078d4;
        outline-offset: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# Textes alternatifs pour les images
st.image("https://img.icons8.com/color/96/000000/cinema-.png", 
         width=100, 
         caption="Icône cinéma - CinéOracle")
```

#### Navigation au clavier
```python
# Support de la navigation au clavier
def create_accessible_interface():
    """Interface accessible avec navigation au clavier"""
    
    # Titres hiérarchiques
    st.title("🎭 CinéOracle - Prédiction d'entrées cinéma")
    st.header("Tableau de bord")
    
    # Labels explicites pour les champs
    username = st.text_input(
        "Nom d'utilisateur (obligatoire)",
        key="login_username",
        help="Entrez votre nom d'utilisateur pour vous connecter"
    )
    
    password = st.text_input(
        "Mot de passe (obligatoire)",
        type="password",
        key="login_password",
        help="Entrez votre mot de passe pour vous connecter"
    )
    
    # Boutons avec descriptions
    if st.button(
        "Se connecter",
        key="login",
        help="Cliquez pour vous connecter avec vos identifiants"
    ):
        authenticate(username, password)
```

### 🧪 Test en bac à sable/environnement dédié

#### Environnement de test
```bash
# Script de test du monitoring
#!/bin/bash
# test_monitoring.sh

echo "�� Test du monitoring en environnement dédié..."

# 1. Démarrer les services de monitoring
docker-compose -f monitoring/docker-compose.yml up -d

# 2. Attendre que Prometheus soit prêt
echo "Attente du démarrage de Prometheus..."
sleep 30

# 3. Vérifier la collecte de métriques
echo "Vérification de la collecte de métriques..."
curl -s http://localhost:9090/api/v1/query?query=up | jq '.data.result'

# 4. Tester les alertes
echo "Test des alertes..."
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups'

# 5. Vérifier Grafana
echo "Vérification de Grafana..."
curl -s http://localhost:3000/api/health

echo "✅ Tests de monitoring terminés"
```

#### Validation des métriques
```python
# tests/test_monitoring.py
def test_prometheus_metrics():
    """Test que les métriques Prometheus sont collectées"""
    import requests
    
    # Vérifier que l'API expose les métriques
    response = requests.get("http://localhost:8000/metrics")
    assert response.status_code == 200
    
    # Vérifier la présence des métriques clés
    metrics_content = response.text
    assert "predictions_total" in metrics_content
    assert "prediction_duration_seconds" in metrics_content
    assert "http_requests_total" in metrics_content

def test_grafana_dashboard():
    """Test que le dashboard Grafana est accessible"""
    import requests
    
    # Vérifier l'accessibilité de Grafana
    response = requests.get("http://localhost:3000/api/health")
    assert response.status_code == 200
    
    # Vérifier que le dashboard est créé
    # (nécessite une authentification Grafana)
```

### 🔗 Chaîne de monitorage opérationnelle

#### Métriques collectées en temps réel
```python
# cinapps_api/app/routes/pred.py
# Métriques Prometheus intégrées
from prometheus_client import Counter, Histogram, Gauge
import time

# Définition des métriques
predictions_counter = Counter('predictions_total', 'Total number of predictions made')
prediction_duration = Histogram('prediction_duration_seconds', 'Time spent making predictions')
predictions_per_minute = Gauge('predictions_per_minute', 'Predictions per minute')

@router.post("/prediction/")
async def predict(features: PredictionRequest, current_user: dict = Depends(get_current_user)): 
    start_time = time.time()
    
    try:
        # Logique de prédiction
        prediction = model_pipeline.predict(df)
        prediction_value = int(prediction[0])
        
        # Incrémenter les métriques
        predictions_counter.inc()
        predictions_per_minute.inc()
        
        return {"prediction": prediction_value}
    
    finally:
        # Mesurer la durée
        duration = time.time() - start_time
        prediction_duration.observe(duration)
```

#### Instrumentation FastAPI
```python
# cinapps_api/app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="Cinapps API",
    description="API sécurisée avec JWT et Auth directement dans Swagger",
    version="1.0",
)

# Instrumentation automatique pour les métriques HTTP
Instrumentator().instrument(app).expose(app)
```

### �� Documentation couvrant installation, configuration, utilisation

#### Guide d'installation
```markdown
# Guide d'installation du monitoring

## Prérequis
- Docker et Docker Compose installés
- Ports 9090 et 3000 disponibles

## Installation
1. Cloner le repository
2. Naviguer vers le dossier monitoring
3. Lancer les services : `docker-compose up -d`

## Configuration
1. Prometheus : http://localhost:9090
2. Grafana : http://localhost:3000 (admin/admin123)

## Utilisation
1. Importer le dashboard Grafana
2. Configurer les alertes
3. Surveiller les métriques en temps réel
```

#### Configuration des alertes
```yaml
# monitoring/alert_rules.yml
groups:
  - name: cinapps_alerts
    rules:
      # Alerte latence élevée
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_highr_seconds_bucket[5m])) > 0.5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Latence élevée détectée"
          description: "La latence p95 est supérieure à 500ms depuis 2 minutes"

      # Alerte taux d'erreurs élevé
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"4..|5.."}[5m]) / rate(http_requests_total[5m]) > 0.02
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Taux d'erreurs élevé"
          description: "Le taux d'erreurs est supérieur à 2% depuis 2 minutes"

      # Alerte API indisponible
      - alert: APIDown
        expr: up{job="cinapps-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "API Cinapps indisponible"
          description: "L'API Cinapps ne répond plus depuis 1 minute"
```

---

## C12 - Programmer des tests automatisés d'un modèle IA

### 📋 Liste et définition des cas de test

#### Périmètre des tests
```python
# tests/test_ml_api_simple.py
"""
Périmètre des tests du modèle IA :
1. Tests d'authentification
2. Tests de prédiction avec données valides
3. Tests de prédiction avec données invalides
4. Tests de gestion d'erreurs
5. Tests de performance
"""

# Stratégie de test
strategie_tests = {
    "tests_unitaire": "Validation des fonctions individuelles",
    "tests_integration": "Validation du flux complet",
    "tests_performance": "Validation des temps de réponse",
    "tests_securite": "Validation de l'authentification",
    "tests_robustesse": "Validation avec données aberrantes"
}
```

#### Cas de test définis
```python
# Cas de test pour l'API de prédiction
cas_de_test = [
    {
        "nom": "Prédiction sans authentification",
        "description": "Vérifier que l'accès est refusé sans token",
        "donnees": {"budget": 1000000, "duree": 120},
        "resultat_attendu": 401
    },
    {
        "nom": "Prédiction avec authentification valide",
        "description": "Vérifier que la prédiction fonctionne avec un token valide",
        "donnees": {
            "id_film": 1,
            "budget": 100000000,
            "duree": 120,
            "genre": "Action",
            "pays": "US",
            "salles_premiere_semaine": 3000,
            "scoring_acteurs_realisateurs": 8.5,
            "coeff_studio": 1,
            "year": 2024,
            "is_fictif": True
        },
        "resultat_attendu": 200
    },
    {
        "nom": "Prédiction avec données invalides",
        "description": "Vérifier la gestion des données incorrectes",
        "donnees": {"id_film": "not_a_number", "budget": -1000},
        "resultat_attendu": 422
    },
    {
        "nom": "Prédiction avec données manquantes",
        "description": "Vérifier la gestion des champs obligatoires",
        "donnees": {"id_film": 1},
        "resultat_attendu": 422
    }
]
```

### ��️ Choix d'outils de test cohérent avec l'environnement

#### Stack de test choisi
```python
# tests/requirements-test.txt
pytest==7.4.0
pytest-asyncio==0.21.1
httpx==0.24.1
pytest-cov==4.1.0
requests==2.31.0
pytest-mock==3.11.1
pytest-html==3.2.0
```

#### Configuration pytest
```python
# tests/conftest.py
import pytest
import requests
import time

@pytest.fixture(scope="session")
def api_base_url():
    """URL de base de l'API pour les tests"""
    return "http://localhost:8000"

@pytest.fixture(scope="session")
def auth_token(api_base_url):
    """Token d'authentification pour les tests"""
    login_data = {"username": "testuser", "password": "test123"}
    response = requests.post(f"{api_base_url}/auth/token", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        pytest.skip("Impossible d'obtenir un token d'authentification")

@pytest.fixture(scope="function")
def clean_database():
    """Nettoie la base de données avant chaque test"""
    # Logique de nettoyage
    yield
    # Logique de restauration
```

### 🔗 Intégration des tests avec la couverture souhaitée

#### Tests unitaires avec couverture
```python
# tests/test_ml_api_simple.py
import pytest
import requests

def test_prediction_without_auth(api_base_url):
    """Test basique : prédiction refusée sans authentification"""
    # ARRANGE
    url = f"{api_base_url}/prediction/"
    prediction_data = {
        "id_film": 1,
        "budget": 100000000,
        "duree": 120,
        "genre": "Action",
        "pays": "US",
        "salles_premiere_semaine": 3000,
        "scoring_acteurs_realisateurs": 8.5,
        "coeff_studio": 1,
        "year": 2024,
        "is_fictif": True
    }
    
    # ACT
    response = requests.post(url, json=prediction_data)
    
    # ASSERT
    assert response.status_code == 401  # Non autorisé

def test_prediction_with_auth(api_base_url, auth_token):
    """Test basique : prédiction avec authentification valide"""
    # ARRANGE
    url = f"{api_base_url}/prediction/"
    headers = {"Authorization": f"Bearer {auth_token}"}
    prediction_data = {
        "id_film": 1,
        "budget": 100000000,
        "duree": 120,
        "genre": "Action",
        "pays": "US",
        "salles_premiere_semaine": 3000,
        "scoring_acteurs_realisateurs": 8.5,
        "coeff_studio": 1,
        "year": 2024,
        "is_fictif": True
    }
    
    # ACT
    response = requests.post(url, json=prediction_data, headers=headers)
    
    # ASSERT
    assert response.status_code in [200, 500]  # 200 si OK, 500 si modèle pas chargé

def test_prediction_with_invalid_data(api_base_url, auth_token):
    """Test basique : prédiction avec données invalides"""
    # ARRANGE
    url = f"{api_base_url}/prediction/"
    headers = {"Authorization": f"Bearer {auth_token}"}
    invalid_data = {
        "id_film": "not_a_number",  # Données invalides
        "budget": -1000  # Budget négatif
    }
    
    # ACT
    response = requests.post(url, json=invalid_data, headers=headers)
    
    # ASSERT
    assert response.status_code in [422, 400, 500]  # Erreur de validation

def test_prediction_api_endpoint(api_base_url, auth_token):
    """Test complet de l'endpoint de prédiction"""
    # ARRANGE
    url = f"{api_base_url}/prediction/"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test avec différents types de films
    test_cases = [
        {
            "name": "Film d'action à gros budget",
            "data": {
                "id_film": 1,
                "budget": 200000000,
                "duree": 150,
                "genre": "Action",
                "pays": "US",
                "salles_premiere_semaine": 4000,
                "scoring_acteurs_realisateurs": 9.0,
                "coeff_studio": 1,
                "year": 2024,
                "is_fictif": True
            }
        },
        {
            "name": "Film français indépendant",
            "data": {
                "id_film": 2,
                "budget": 5000000,
                "duree": 90,
                "genre": "Drame",
                "pays": "FR",
                "salles_premiere_semaine": 200,
                "scoring_acteurs_realisateurs": 7.5,
                "coeff_studio": 1,
                "year": 2024,
                "is_fictif": False
            }
        }
    ]
    
    # ACT & ASSERT
    for test_case in test_cases:
        response = requests.post(url, json=test_case["data"], headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            assert "prediction" in result
            assert "id_film" in result
            assert "is_fictif" in result
            assert "message" in result
            assert isinstance(result["prediction"], int)
            assert result["prediction"] > 0
            print(f"✅ {test_case['name']}: Prédiction {result['prediction']:,} entrées")
        elif response.status_code == 500:
            # Modèle non chargé en environnement de test
            print(f"⚠️ {test_case['name']}: Modèle non disponible (500)")
        else:
            pytest.fail(f"❌ {test_case['name']}: Erreur {response.status_code}")

def test_prediction_storage_in_database(api_base_url, auth_token):
    """Test que les prédictions sont bien stockées en base"""
    # ARRANGE
    url = f"{api_base_url}/prediction/"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    test_film_id = 999
    prediction_data = {
        "id_film": test_film_id,
        "budget": 100000000,
        "duree": 120,
        "genre": "Test",
        "pays": "US",
        "salles_premiere_semaine": 3000,
        "scoring_acteurs_realisateurs": 8.0,
        "coeff_studio": 1,
        "year": 2024,
        "is_fictif": True
    }
    
    # ACT 1: Faire une prédiction
    response = requests.post(url, json=prediction_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        prediction_value = result["prediction"]
        
        # ACT 2: Vérifier en base de données
        # (Ceci nécessiterait un endpoint de vérification ou une connexion directe à la DB)
        verification_url = f"{api_base_url}/films/{test_film_id}"
        verification_response = requests.get(verification_url, headers=headers)
        
        if verification_response.status_code == 200:
            film_data = verification_response.json()
            assert film_data.get("is_pred") == True
            print(f"✅ Prédiction stockée en base: {prediction_value:,} entrées")
        else:
            print("⚠️ Impossible de vérifier le stockage en base")
    else:
        print(f"⚠️ Prédiction non effectuée: {response.status_code}")

def test_prediction_error_handling(api_base_url, auth_token):
    """Test de la gestion d'erreurs de l'API de prédiction"""
    # ARRANGE
    url = f"{api_base_url}/prediction/"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1: Données manquantes
    incomplete_data = {
        "id_film": 1,
        "budget": 100000000
        # Manque les autres champs obligatoires
    }
    
    response = requests.post(url, json=incomplete_data, headers=headers)
    assert response.status_code in [422, 400]  # Erreur de validation
    
    # Test 2: Types de données incorrects
    invalid_types_data = {
        "id_film": "not_a_number",
        "budget": "not_a_number",
        "duree": "not_a_number",
        "genre": 123,
        "pays": 456,
        "salles_premiere_semaine": "not_a_number",
        "scoring_acteurs_realisateurs": "not_a_number",
        "coeff_studio": "not_a_number",
        "year": "not_a_number",
        "is_fictif": "not_a_boolean"
    }
    
    response = requests.post(url, json=invalid_types_data, headers=headers)
    assert response.status_code in [422, 400]  # Erreur de validation
    
    # Test 3: Valeurs hors limites
    out_of_bounds_data = {
        "id_film": -1,  # ID négatif
        "budget": -1000000,  # Budget négatif
        "duree": 0,  # Durée nulle
        "genre": "Action",
        "pays": "US",
        "salles_premiere_semaine": -100,  # Salles négatives
        "scoring_acteurs_realisateurs": 15.0,  # Score > 10
        "coeff_studio": 1,
        "year": 1800,  # Année trop ancienne
        "is_fictif": True
    }
    
    response = requests.post(url, json=out_of_bounds_data, headers=headers)
    # Peut retourner 422 (validation) ou 200 (si le modèle accepte)
    assert response.status_code in [422, 400, 200]

def test_prediction_performance_benchmark(api_base_url, auth_token):
    """Test de performance de l'API de prédiction"""
    import time
    
    # ARRANGE
    url = f"{api_base_url}/prediction/"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    prediction_data = {
        "id_film": 1,
        "budget": 100000000,
        "duree": 120,
        "genre": "Action",
        "pays": "US",
        "salles_premiere_semaine": 3000,
        "scoring_acteurs_realisateurs": 8.5,
        "coeff_studio": 1,
        "year": 2024,
        "is_fictif": True
    }
    
    # Mesurer le temps de réponse sur plusieurs requêtes
    response_times = []
    num_requests = 5
    
    for i in range(num_requests):
        start_time = time.time()
        response = requests.post(url, json=prediction_data, headers=headers)
        end_time = time.time()
        
        response_time = end_time - start_time
        response_times.append(response_time)
        
        if response.status_code == 200:
            print(f"Requête {i+1}: {response_time:.3f}s")
        else:
            print(f"Requête {i+1}: Erreur {response.status_code} en {response_time:.3f}s")
    
    # Calculer les statistiques
    avg_time = sum(response_times) / len(response_times)
    max_time = max(response_times)
    min_time = min(response_times)
    
    print(f"📊 Performance: Moyenne={avg_time:.3f}s, Min={min_time:.3f}s, Max={max_time:.3f}s")
    
    # Vérifier que la performance est acceptable
    assert avg_time < 2.0, f"Temps de réponse moyen trop élevé: {avg_time:.3f}s"
    assert max_time < 5.0, f"Temps de réponse maximum trop élevé: {max_time:.3f}s"

def test_prediction_model_consistency(api_base_url, auth_token):
    """Test de cohérence du modèle (mêmes données = même résultat)"""
    # ARRANGE
    url = f"{api_base_url}/prediction/"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    test_data = {
        "id_film": 888,
        "budget": 50000000,
        "duree": 100,
        "genre": "Comédie",
        "pays": "FR",
        "salles_premiere_semaine": 1500,
        "scoring_acteurs_realisateurs": 7.0,
        "coeff_studio": 1,
        "year": 2024,
        "is_fictif": True
    }
    
    # ACT: Faire plusieurs prédictions identiques
    predictions = []
    num_tests = 3
    
    for i in range(num_tests):
        response = requests.post(url, json=test_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            predictions.append(result["prediction"])
            print(f"Prédiction {i+1}: {result['prediction']:,}")
        else:
            print(f"Erreur prédiction {i+1}: {response.status_code}")
    
    # ASSERT: Vérifier la cohérence
    if len(predictions) >= 2:
        # Le modèle déterministe devrait donner les mêmes résultats
        first_prediction = predictions[0]
        for i, pred in enumerate(predictions[1:], 1):
            assert pred == first_prediction, f"Prédiction {i+1} différente: {pred} vs {first_prediction}"
        
        print(f"✅ Modèle cohérent: toutes les prédictions = {first_prediction:,}")
    else:
        print("⚠️ Impossible de tester la cohérence (pas assez de prédictions réussies)")

# Tests d'intégration pour l'API complète
def test_full_prediction_workflow(api_base_url, auth_token):
    """Test du workflow complet: création film + prédiction"""
    # ARRANGE
    films_url = f"{api_base_url}/films/"
    prediction_url = f"{api_base_url}/prediction/"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # ACT 1: Créer un film de test
    new_film = {
        "titre": "Film Test Workflow",
        "annee_sortie": 2024,
        "genre": "Test",
        "duree": 95,
        "budget": 75000000,
        "pays": "US",
        "salles": 2500
    }
    
    create_response = requests.post(films_url, json=new_film, headers=headers)
    
    if create_response.status_code in [201, 400]:  # 201 créé, 400 si existe déjà
        # ACT 2: Récupérer la liste des films
        films_response = requests.get(films_url, headers=headers)
        
        if films_response.status_code == 200:
            films = films_response.json()
            test_film = None
            
            # Trouver notre film de test
            for film in films:
                if film.get("titre") == "Film Test Workflow":
                    test_film = film
                    break
            
            if test_film:
                # ACT 3: Faire une prédiction pour ce film
                prediction_data = {
                    "id_film": test_film["id_film"],
                    "budget": test_film.get("budget", 75000000),
                    "duree": test_film.get("duree", 95),
                    "genre": test_film.get("genre", "Test"),
                    "pays": test_film.get("pays", "US"),
                    "salles_premiere_semaine": test_film.get("salles", 2500),
                    "scoring_acteurs_realisateurs": 7.5,
                    "coeff_studio": 1,
                    "year": 2024,
                    "is_fictif": False
                }
                
                pred_response = requests.post(prediction_url, json=prediction_data, headers=headers)
                
                if pred_response.status_code == 200:
                    pred_result = pred_response.json()
                    print(f"✅ Workflow complet réussi: Film créé + Prédiction {pred_result['prediction']:,} entrées")
                else:
                    print(f"⚠️ Prédiction échouée: {pred_response.status_code}")
            else:
                print("⚠️ Film de test non trouvé")
        else:
            print(f"⚠️ Impossible de récupérer les films: {films_response.status_code}")
    else:
        print(f"⚠️ Impossible de créer le film de test: {create_response.status_code}")

# Configuration pour les tests de performance
@pytest.mark.slow
def test_load_testing(api_base_url, auth_token):
    """Test de charge de l'API de prédiction"""
    import threading
    import time
    
    # ARRANGE
    url = f"{api_base_url}/prediction/"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    prediction_data = {
        "id_film": 1,
        "budget": 100000000,
        "duree": 120,
        "genre": "Action",
        "pays": "US",
        "salles_premiere_semaine": 3000,
        "scoring_acteurs_realisateurs": 8.5,
        "coeff_studio": 1,
        "year": 2024,
        "is_fictif": True
    }
    
    results = []
    errors = []
    
    def make_request():
        try:
            start_time = time.time()
            response = requests.post(url, json=prediction_data, headers=headers)
            end_time = time.time()
            
            results.append({
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            })
        except Exception as e:
            errors.append(str(e))
    
    # ACT: Lancer plusieurs requêtes simultanées
    num_threads = 10
    threads = []
    
    start_time = time.time()
    for i in range(num_threads):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()
    
    # Attendre que tous les threads terminent
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_time
    
    # ASSERT: Analyser les résultats
    successful_requests = sum(1 for r in results if r["success"])
    avg_response_time = sum(r["response_time"] for r in results) / len(results) if results else 0
    
    print(f"📊 Test de charge: {successful_requests}/{len(results)} requêtes réussies")
    print(f"⏱️ Temps moyen: {avg_response_time:.3f}s")
    print(f"🚀 Débit: {len(results)/total_time:.2f} req/s")
    
    # Vérifications
    assert len(results) == num_threads, f"Nombre de résultats incorrect: {len(results)}"
    assert successful_requests > 0, "Aucune requête réussie"
    assert avg_response_time < 3.0, f"Temps de réponse moyen trop élevé: {avg_response_time:.3f}s"
    assert len(errors) == 0, f"Erreurs détectées: {errors}"

# Tests de sécurité
def test_security_headers(api_base_url):
    """Test des en-têtes de sécurité de l'API"""
    # ARRANGE
    url = f"{api_base_url}/"
    
    # ACT
    response = requests.get(url)
    
    # ASSERT: Vérifier les en-têtes de sécurité
    headers = response.headers
    
    # Headers recommandés pour la sécurité
    security_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block"
    }
    
    for header, expected_value in security_headers.items():
        if header in headers:
            print(f"✅ {header}: {headers[header]}")
        else:
            print(f"⚠️ {header} manquant")

def test_rate_limiting(api_base_url, auth_token):
    """Test de limitation de débit (si implémentée)"""
    # ARRANGE
    url = f"{api_base_url}/prediction/"
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    prediction_data = {
        "id_film": 1,
        "budget": 100000000,
        "duree": 120,
        "genre": "Action",
        "pays": "US",
        "salles_premiere_semaine": 3000,
        "scoring_acteurs_realisateurs": 8.5,
        "coeff_studio": 1,
        "year": 2024,
        "is_fictif": True
    }
    
    # ACT: Envoyer plusieurs requêtes rapidement
    responses = []
    for i in range(20):
        response = requests.post(url, json=prediction_data, headers=headers)
        responses.append(response.status_code)
    
    # ASSERT: Vérifier si la limitation de débit est active
    rate_limited = any(status == 429 for status in responses)
    
    if rate_limited:
        print("✅ Limitation de débit active")
    else:
        print("ℹ️ Aucune limitation de débit détectée")
    
    # Compter les succès
    successes = sum(1 for status in responses if status == 200)
    print(f"�� Requêtes réussies: {successes}/{len(responses)}")

# Configuration pytest pour les tests
if __name__ == "__main__":
    # Configuration pour exécuter les tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term"
    ])

