import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import plotly.express as px
from datetime import datetime
import time

# Configuration de la page
st.set_page_config(
    page_title="CinéPredict - Prédiction d'entrées cinéma",
    page_icon="🎬",
    layout="wide"
)

# Styles CSS personnalisés
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .prediction-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Chargement des variables d'environnement
load_dotenv()
URL_API_CRUD = os.getenv('URL_API_CRUD')
URL_API_PRED = os.getenv('URL_API')

# Chargement des données des acteurs
@st.cache_data
def load_actors_data():
    try:
        return pd.read_csv("acteurs_coef.csv")
    except Exception as e:
        st.error(f"Erreur lors du chargement des données des acteurs: {str(e)}")
        return pd.DataFrame()

actors_df = load_actors_data()

# Initialisation des états de session
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = False

# Fonction d'authentification
def authenticate(username: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{URL_API_CRUD}/auth/token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            st.session_state["access_token"] = response.json().get("access_token")
            return True
        return False
    except Exception as e:
        st.error(f"Erreur d'authentification: {str(e)}")
        return False

# Fonction pour obtenir le coefficient du studio
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

# Fonction pour calculer le score du casting
def calculate_casting_score(film_id: int) -> float:
    if not st.session_state["access_token"]:
        return 0.0
    
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    total_score = 0.0
    
    try:
        # Récupération des acteurs et réalisateurs
        acteurs = requests.get(f"{URL_API_CRUD}/films/{film_id}/acteurs/", headers=headers).json()
        realisateurs = requests.get(f"{URL_API_CRUD}/films/{film_id}/realisateurs/", headers=headers).json()
        
        # Calcul du score
        for personne in acteurs + realisateurs:
            nom = personne.get('nom', '')
            if nom in actors_df['name'].values:
                score = actors_df.loc[actors_df['name'] == nom, 'coef_personne'].values[0]
                total_score += score
        
        return total_score
    except Exception as e:
        st.error(f"Erreur lors du calcul du score du casting: {str(e)}")
        return 0.0

# Fonction pour récupérer les films
@st.cache_data(ttl=300)  # Cache de 5 minutes
def fetch_films():
    if not st.session_state["access_token"]:
        return pd.DataFrame()
    
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    try:
        response = requests.get(f"{URL_API_CRUD}/films/", headers=headers)
        if response.status_code == 200:
            films_data = pd.DataFrame(response.json())
            return films_data
        else:
            st.error(f"Erreur lors de la récupération des films: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")
        return pd.DataFrame()

# Fonction de prédiction
def predict_entries(film: pd.Series) -> float:
    try:
        # Préparation des données
        year = pd.to_datetime(film.get('date_sortie', datetime.now())).year
        data = {
            'budget': float(film.get('budget', 25000000)),
            'duree': int(film.get('duree', 107)),
            'genre': str(film.get('genre', 'missing')),
            'pays': str(film.get('pays', 'missing')),
            'salles_premiere_semaine': int(film.get('salles', 100)),
            'scoring_acteurs_realisateurs': calculate_casting_score(film.get('id_film')),
            'coeff_studio': get_studio_coefficient(film.get('studio', '')),
            'year': year
        }
        
        # Appel à l'API de prédiction
        response = requests.post(URL_API_PRED, json=data)
        if response.status_code == 200:
            return float(response.json().get('prediction', 0))
        return 0.0
    except Exception as e:
        st.error(f"Erreur de prédiction: {str(e)}")
        return 0.0

# Interface utilisateur
def main():
    # Sidebar pour l'authentification
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/cinema-.png", width=100)
        st.title("🎬 CinéPredict")
        
        if not st.session_state["authentication_status"]:
            st.subheader("Connexion")
            username = st.text_input("👤 Nom d'utilisateur")
            password = st.text_input("🔑 Mot de passe", type="password")
            
            if st.button("Se connecter", key="login"):
                if authenticate(username, password):
                    st.session_state["authentication_status"] = True
                    st.success("✅ Connexion réussie!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
        else:
            st.success("✅ Connecté")
            if st.button("Se déconnecter", key="logout"):
                st.session_state["authentication_status"] = False
                st.session_state["access_token"] = None
                st.rerun()

    # Contenu principal
    if st.session_state["authentication_status"]:
        st.title("📊 Prédiction d'entrées cinéma")
        
        # Chargement des films
        with st.spinner("Chargement des données..."):
            films_df = fetch_films()
        
        if not films_df.empty:
            # Filtres
            col1, col2, col3 = st.columns(3)
            with col1:
                genre_filter = st.multiselect(
                    "Filtrer par genre",
                    options=sorted(films_df['genre'].unique())
                )
            with col2:
                studio_filter = st.multiselect(
                    "Filtrer par studio",
                    options=sorted(films_df['studio'].unique())
                )
            with col3:
                min_budget = st.number_input(
                    "Budget minimum (millions €)",
                    min_value=0.0,
                    value=0.0
                )
            
            # Application des filtres
            filtered_df = films_df.copy()
            if genre_filter:
                filtered_df = filtered_df[filtered_df['genre'].isin(genre_filter)]
            if studio_filter:
                filtered_df = filtered_df[filtered_df['studio'].isin(studio_filter)]
            filtered_df = filtered_df[filtered_df['budget'] >= min_budget * 1_000_000]
            
            # Calcul des prédictions
            with st.spinner("Calcul des prédictions..."):
                filtered_df['prediction_entrees'] = filtered_df.apply(predict_entries, axis=1)
            
            # Affichage des résultats
            tab1, tab2 = st.tabs(["📊 Tableau", "📈 Graphiques"])
            
            with tab1:
                st.dataframe(
                    filtered_df[['titre', 'genre', 'studio', 'budget', 'prediction_entrees']]
                    .sort_values('prediction_entrees', ascending=False)
                    .style.format({
                        'budget': '{:,.0f} €',
                        'prediction_entrees': '{:,.0f}'
                    })
                )
            
            with tab2:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Graphique des prédictions par film
                    fig1 = px.bar(
                        filtered_df.nlargest(10, 'prediction_entrees'),
                        x='titre',
                        y='prediction_entrees',
                        title="Top 10 des prédictions d'entrées",
                        labels={'prediction_entrees': 'Entrées prédites', 'titre': 'Film'}
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Graphique des prédictions moyennes par genre
                    genre_avg = filtered_df.groupby('genre')['prediction_entrees'].mean().reset_index()
                    fig2 = px.bar(
                        genre_avg,
                        x='genre',
                        y='prediction_entrees',
                        title="Moyenne des prédictions par genre",
                        labels={'prediction_entrees': 'Moyenne des entrées prédites', 'genre': 'Genre'}
                    )
                    st.plotly_chart(fig2, use_container_width=True)
            
            # Métriques globales
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Nombre de films",
                    len(filtered_df)
                )
            with col2:
                st.metric(
                    "Moyenne des prédictions",
                    f"{filtered_df['prediction_entrees'].mean():,.0f}"
                )
            with col3:
                st.metric(
                    "Total des budgets",
                    f"{filtered_df['budget'].sum():,.0f} €"
                )
        else:
            st.warning("⚠️ Aucun film disponible")
    else:
        st.info("👋 Veuillez vous connecter pour accéder aux prédictions")

if __name__ == "__main__":
    main()
