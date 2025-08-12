import os
import time
from datetime import datetime, timedelta
from urllib.parse import urljoin

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from dotenv import load_dotenv

# =========================
# Config page Streamlit
# =========================
st.set_page_config(
    page_title="CinéOracle - Prédiction d'entrées cinéma",
    page_icon="🎬",
    layout="wide"
)

# =========================
# Styles CSS
# =========================
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

# =========================
# Variables d'environnement
# =========================
load_dotenv()

def _norm(url: str) -> str:
    return (url or "").rstrip("/")

# Par défaut en réseau Docker : http://cinapps-api:8000
URL_API_CRUD = _norm(os.getenv("URL_API_CRUD") or "http://cinapps-api:8000")
URL_API_PRED = _norm(os.getenv("URL_API_PRED") or "http://cinapps-api:8000")

# Chemin du CSV acteurs (compatible montage fichier)
ACTEURS_COEF_PATH = os.getenv("ACTEURS_COEF_PATH", "/app/acteurs_coef.csv")

# =========================
# Helpers
# =========================
def api_request(path: str, method: str = "GET", **kwargs):
    """Wrapper requests avec base URL CRUD et timeout par défaut."""
    url = urljoin(URL_API_CRUD + "/", path.lstrip("/"))
    kwargs.setdefault("timeout", 10)
    return requests.request(method.upper(), url, **kwargs)

@st.cache_data
def load_actors_data(path: str):
    """Charge le CSV des coefficients acteurs/réalisateurs."""
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"Erreur lors du chargement des acteurs ({path}) : {e}")
        return pd.DataFrame(columns=["name", "coef_personne"])

actors_df = load_actors_data(ACTEURS_COEF_PATH)

# =========================
# Session state
# =========================
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None
if "registration_success" not in st.session_state:
    st.session_state["registration_success"] = False
if "registration_message" not in st.session_state:
    st.session_state["registration_message"] = ""

# =========================
# Authentification
# =========================
def authenticate(username: str, password: str) -> bool:
    try:
        response = api_request(
            "/auth/token",
            method="POST",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            token_data = response.json()
            st.session_state["access_token"] = token_data.get("access_token")
            st.session_state["user_info"] = {
                "username": username,
                "token_type": token_data.get("token_type", "bearer")
            }
            return True
        return False
    except Exception as e:
        st.error(f"Erreur d'authentification: {str(e)}")
        return False

def register_user(username: str, password: str, confirm_password: str) -> bool:
    try:
        if password != confirm_password:
            st.error("❌ Les mots de passe ne correspondent pas")
            return False
        if len(password) < 6:
            st.error("❌ Le mot de passe doit contenir au moins 6 caractères")
            return False

        response = api_request(
            "/auth/register",
            method="POST",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            st.session_state["registration_success"] = True
            st.session_state["registration_message"] = (
                f"✅ Inscription réussie pour '{username}'! Vous pouvez maintenant vous connecter."
            )
            return True
        else:
            # Si JSON non lisible, fallback
            detail = None
            try:
                detail = response.json().get("detail")
            except Exception:
                detail = response.text
            st.error(f"❌ Erreur d'inscription: {detail or 'Erreur inconnue'}")
            return False
    except Exception as e:
        st.error(f"❌ Erreur lors de l'inscription: {str(e)}")
        return False

# =========================
# Logique métier
# =========================
def get_studio_coefficient(studio: str) -> int:
    studio_coefficients = {
        'major': ('Walt Disney Pictures', 'Warner Bros.', 'Paramount', 'Sony Pictures',
                  'Universal', '20th Century Fox', 'Lionsgate', 'Columbia'),
        'medium': ('Pathé', 'Studiocanal', 'Gaumont', 'UGC Distribution', 'SND',
                   'Le Pacte', 'Metropolitan', 'EuropaCorp', 'GBVI', 'Wild Bunch'),
        'small': ('Gébéka', 'Memento Films', 'KMBO', 'Océan Films', 'AMLF',
                  'MK2 Diffusion', 'Gaumont Sony', 'Apollo Films')
    }
    if studio in studio_coefficients['major']:
        return 3
    elif studio in studio_coefficients['medium']:
        return 2
    elif studio in studio_coefficients['small']:
        return 1
    return 0

def calculate_casting_score(film_id: int) -> float:
    if not st.session_state["access_token"]:
        return 0.0

    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    total_score = 0.0
    try:
        acteurs = api_request(f"/films/{film_id}/acteurs/", headers=headers).json()
        realisateurs = api_request(f"/films/{film_id}/realisateurs/", headers=headers).json()

        for personne in (acteurs or []) + (realisateurs or []):
            nom = personne.get('nom', '')
            if not actors_df.empty and nom in actors_df['name'].values:
                score = actors_df.loc[actors_df['name'] == nom, 'coef_personne'].values[0]
                total_score += score
        return total_score
    except Exception as e:
        st.error(f"Erreur lors du calcul du score du casting: {str(e)}")
        return 0.0

@st.cache_data(ttl=300)
def fetch_films_with_predictions():
    if not st.session_state["access_token"]:
        return pd.DataFrame()

    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    try:
        response = api_request("/films/", headers=headers)
        if response.status_code == 200:
            films_data = pd.DataFrame(response.json() or [])
            predictions_response = api_request("/predictions/", headers=headers)
            if predictions_response.status_code == 200:
                predictions_data = pd.DataFrame(predictions_response.json() or [])
                if not predictions_data.empty:
                    films_data = films_data.merge(
                        predictions_data[['id_film', 'prediction_entrees', 'date_prediction']],
                        on='id_film', how='left'
                    )
                else:
                    films_data['prediction_entrees'] = None
                    films_data['date_prediction'] = None
            return films_data
        else:
            st.error(f"Erreur lors de la récupération des films: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")
        return pd.DataFrame()

def get_weekly_films(films_df: pd.DataFrame) -> pd.DataFrame:
    """Filtre les films sortis dans les 7 derniers jours (et +3 jours futurs)."""
    if films_df.empty:
        return films_df.copy()

    df = films_df.copy()
    # Sécuriser le format des dates
    df['date_sortie'] = pd.to_datetime(df['date_sortie'], errors='coerce')

    today = datetime.now()
    start_date = today - timedelta(days=7)
    end_date = today + timedelta(days=3)

    weekly = df[(df['date_sortie'] >= start_date) & (df['date_sortie'] <= end_date)].copy()
    return weekly

def classify_film_performance(prediction) -> str:
    """Classe un film selon sa prédiction d'entrées."""
    if prediction is None or pd.isna(prediction):
        return "unknown"
    try:
        val = float(prediction)
    except Exception:
        return "unknown"

    if val >= 1_000_000:
        return "top"
    elif val >= 500_000:
        return "good"
    elif val >= 100_000:
        return "average"
    else:
        return "poor"

def get_performance_icon(performance: str) -> str:
    return {
        "top": "🥇",
        "good": "🥈",
        "average": "🥉",
        "poor": "⚠️",
        "unknown": "❓"
    }.get(performance, "❓")

def format_budget(budget) -> str:
    if pd.isna(budget) or budget is None:
        return "N/A"
    try:
        return f"{float(budget):,.0f} €"
    except Exception:
        return "N/A"

def format_duration(duration) -> str:
    if pd.isna(duration) or duration is None:
        return "N/A"
    try:
        return f"{int(duration)} min"
    except Exception:
        return "N/A"

def format_prediction_metric(prediction) -> str:
    if pd.notna(prediction):
        try:
            return f"{float(prediction):,.0f}"
        except Exception:
            return "N/A"
    return "N/A"

# =========================
# UI
# =========================
def main():
    # ---- Sidebar (auth) ----
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/cinema-.png", width=100)
        st.title("🎭 CinéOracle")

        if not st.session_state["authentication_status"]:
            tab1, tab2 = st.tabs(["🔑 Connexion", "📝 Inscription"])

            with tab1:
                st.subheader("Connexion")
                username = st.text_input("👤 Nom d'utilisateur", key="login_username")
                password = st.text_input("🔑 Mot de passe", type="password", key="login_password")

                if st.button("Se connecter", key="login"):
                    if authenticate(username, password):
                        st.session_state["authentication_status"] = True
                        st.session_state["registration_success"] = False
                        st.session_state["registration_message"] = ""
                        st.success("✅ Connexion réussie!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Identifiants incorrects")

            with tab2:
                st.subheader("Inscription")

                if st.session_state["registration_success"]:
                    st.success(st.session_state["registration_message"])
                    st.info("🔄 Allez maintenant dans l'onglet 'Connexion' pour vous connecter avec vos identifiants.")
                    if st.button("📝 Créer un autre compte", key="new_registration"):
                        st.session_state["registration_success"] = False
                        st.session_state["registration_message"] = ""
                        st.rerun()
                else:
                    new_username = st.text_input("👤 Nouveau nom d'utilisateur", key="register_username")
                    new_password = st.text_input("🔑 Nouveau mot de passe", type="password", key="register_password")
                    confirm_password = st.text_input("🔐 Confirmer le mot de passe", type="password", key="confirm_password")
                    st.info("💡 Le mot de passe doit contenir au moins 6 caractères")

                    if st.button("S'inscrire", key="register"):
                        if register_user(new_username, new_password, confirm_password):
                            st.rerun()
        else:
            st.success("✅ Connecté")
            if st.session_state["user_info"]:
                st.write(f"👤 **{st.session_state['user_info']['username']}**")
            if st.button("Se déconnecter", key="logout"):
                st.session_state["authentication_status"] = False
                st.session_state["access_token"] = None
                st.session_state["user_info"] = None
                st.rerun()

    # ---- Contenu principal ----
    if st.session_state["authentication_status"]:
        st.title("📊 Par les pouvoirs qui me sont conférés, je vous présente les prédictions des sorties récentes!")

        today = datetime.now()
        start_date = today - timedelta(days=7)
        end_date = today + timedelta(days=3)
        st.info(f"📅 **Films sortis du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}**")

        with st.spinner("Chargement des données..."):
            films_df = fetch_films_with_predictions()

        if not films_df.empty:
            weekly_films = get_weekly_films(films_df)

            if not weekly_films.empty:
                weekly_films = weekly_films.sort_values('prediction_entrees', ascending=False)
                weekly_films['performance'] = weekly_films['prediction_entrees'].apply(classify_film_performance)

                st.subheader("🏆 Classement des sorties récentes")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Nombre de films", len(weekly_films))
                with col2:
                    valid_predictions = weekly_films['prediction_entrees'].dropna()
                    try:
                        avg_prediction = float(valid_predictions.mean()) if not valid_predictions.empty else 0
                    except Exception:
                        avg_prediction = 0
                    st.metric("Moyenne des prédictions", f"{avg_prediction:,.0f}")
                with col3:
                    titre0 = weekly_films.iloc[0]['titre']
                    st.metric("Meilleur film", (titre0[:20] + "...") if isinstance(titre0, str) and len(titre0) > 20 else titre0)
                with col4:
                    try:
                        max_prediction = float(valid_predictions.max()) if not valid_predictions.empty else 0
                    except Exception:
                        max_prediction = 0
                    st.metric("Prédiction max", f"{max_prediction:,.0f}")

                tabs = st.tabs(["🥇 Top Films", "🥈 Films Prometteurs", "🥉 Films Moyens", "⚠️ Films à Risque"])

                def _render_list(df_cat: pd.DataFrame, css_class: str, perf_key: str):
                    if df_cat.empty:
                        st.info("Aucun film dans cette catégorie pour cette période")
                        return
                    for _, film in df_cat.iterrows():
                        with st.container():
                            c1, c2, c3 = st.columns([2, 1, 1])
                            with c1:
                                st.markdown(f"""
                                <div class="film-card {css_class}">
                                    <h4>{get_performance_icon(perf_key)} {film.get('titre','')}</h4>
                                    <p><strong>Genre:</strong> {film.get('genre','N/A')} | <strong>Studio:</strong> {film.get('studio','N/A')}</p>
                                    <p><strong>Durée:</strong> {format_duration(film.get('duree'))} | <strong>Budget:</strong> {format_budget(film.get('budget'))}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            with c2:
                                st.metric("Prédiction", format_prediction_metric(film.get('prediction_entrees')))
                            with c3:
                                try:
                                    dt = film.get('date_sortie')
                                    st.write(f"📅 {pd.to_datetime(dt).strftime('%d/%m') if pd.notna(dt) else 'N/A'}")
                                except Exception:
                                    st.write("📅 N/A")

                with tabs[0]:
                    _render_list(weekly_films[weekly_films['performance'] == 'top'], "top-film", "top")
                with tabs[1]:
                    _render_list(weekly_films[weekly_films['performance'] == 'good'], "good-film", "good")
                with tabs[2]:
                    _render_list(weekly_films[weekly_films['performance'] == 'average'], "average-film", "average")
                with tabs[3]:
                    _render_list(weekly_films[weekly_films['performance'] == 'poor'], "poor-film", "poor")

                # -------- Graphiques --------
                st.subheader("📈 Analyses visuelles")
                c1, c2 = st.columns(2)

                with c1:
                    fig1 = px.bar(
                        weekly_films,
                        x='titre',
                        y='prediction_entrees',
                        title="Prédictions d'entrées par film",
                        labels={'prediction_entrees': 'Entrées prédites', 'titre': 'Film'},
                        color='performance',
                        color_discrete_map={
                            'top': '#FFD700',
                            'good': '#90EE90',
                            'average': '#FFA500',
                            'poor': '#FF6B6B',
                            'unknown': '#CCCCCC'
                        }
                    )
                    fig1.update_xaxes(tickangle=45)
                    st.plotly_chart(fig1, use_container_width=True)

                with c2:
                    genre_avg = (
                        weekly_films
                        .dropna(subset=["genre"])
                        .groupby('genre', dropna=True)['prediction_entrees']
                        .mean()
                        .reset_index()
                    )
                    fig2 = px.pie(
                        genre_avg,
                        values='prediction_entrees',
                        names='genre',
                        title="Répartition des prédictions par genre"
                    )
                    st.plotly_chart(fig2, use_container_width=True)

                # -------- Tableau --------
                st.subheader("📋 Tableau complet des sorties récentes")
                display_df = weekly_films[['titre', 'genre', 'studio', 'budget', 'duree', 'date_sortie', 'prediction_entrees']].copy()

                display_df['budget_formatted'] = display_df['budget'].apply(format_budget)
                display_df['duree_formatted'] = display_df['duree'].apply(format_duration)
                display_df['date_formatted'] = display_df['date_sortie'].apply(
                    lambda x: pd.to_datetime(x).strftime('%d/%m/%Y') if pd.notna(x) else 'N/A'
                )
                display_df['prediction_formatted'] = display_df['prediction_entrees'].apply(
                    lambda x: f"{float(x):,.0f}" if pd.notna(x) else 'N/A'
                )

                st.dataframe(
                    display_df[['titre', 'genre', 'studio', 'budget_formatted', 'duree_formatted', 'date_formatted', 'prediction_formatted']]
                    .rename(columns={
                        'budget_formatted': 'Budget',
                        'duree_formatted': 'Durée',
                        'date_formatted': 'Date de sortie',
                        'prediction_formatted': 'Prédiction entrées'
                    })
                )
            else:
                st.warning("⚠️ Aucun film trouvé pour cette période dans la base de données")
                st.info("💡 Les films sont ajoutés automatiquement via le scraping Allociné")
        else:
            st.warning("⚠️ Aucun film disponible dans la base de données")
            st.info("💡 Vérifiez que le scraping Allociné a bien fonctionné")
    else:
        st.markdown("""
        ### Bonjour et bienvenue sur notre application
        Connectez-vous afin de découvrir les sorties de la semaine et nos prédictions!
        """)

if __name__ == "__main__":
    main()
