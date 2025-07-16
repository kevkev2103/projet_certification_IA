import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import plotly.express as px
from datetime import datetime, timedelta
import time

# Configuration de la page
st.set_page_config(
    page_title="CinéOracle - Prédiction d'entrées cinéma",
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
    .film-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: white;
    }
    .top-film {
        border-color: #ffd700;
        background-color: #fffbf0;
    }
    .good-film {
        border-color: #90EE90;
        background-color: #f0fff0;
    }
    .average-film {
        border-color: #FFA500;
        background-color: #fff8dc;
    }
    .poor-film {
        border-color: #FF6B6B;
        background-color: #fff5f5;
    }
    </style>
""", unsafe_allow_html=True)

# Chargement des variables d'environnement
load_dotenv()
URL_API_CRUD = os.getenv('URL_API_CRUD', 'http://localhost:8000')
URL_API_PRED = os.getenv('URL_API_PRED', 'http://localhost:8001')

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
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None
if "registration_success" not in st.session_state:
    st.session_state["registration_success"] = False
if "registration_message" not in st.session_state:
    st.session_state["registration_message"] = ""

# Fonction d'authentification améliorée
def authenticate(username: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{URL_API_CRUD}/auth/token",
            data={"username": username, "password": password}
        )
        print(response.json())
        print(response.status_code)
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

# Fonction d'inscription
def register_user(username: str, password: str, confirm_password: str) -> bool:
    try:
        # Vérifier que les mots de passe correspondent
        if password != confirm_password:
            st.error("❌ Les mots de passe ne correspondent pas")
            return False
        
        # Vérifier la longueur du mot de passe
        if len(password) < 6:
            st.error("❌ Le mot de passe doit contenir au moins 6 caractères")
            return False
        
        # Appel à l'API d'inscription
        response = requests.post(
            f"{URL_API_CRUD}/auth/register",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            st.session_state["registration_success"] = True
            st.session_state["registration_message"] = f"✅ Inscription réussie pour '{username}'! Vous pouvez maintenant vous connecter."
            return True
        else:
            error_data = response.json()
            st.error(f"❌ Erreur d'inscription: {error_data.get('detail', 'Erreur inconnue')}")
            return False
            
    except Exception as e:
        st.error(f"❌ Erreur lors de l'inscription: {str(e)}")
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

# Fonction pour récupérer les films avec prédictions
@st.cache_data(ttl=300)  # Cache de 5 minutes
def fetch_films_with_predictions():
    if not st.session_state["access_token"]:
        return pd.DataFrame()
    
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    try:
        # Récupérer les films
        response = requests.get(f"{URL_API_CRUD}/films/", headers=headers)
        print("*"*50)
        print(response)
        print("*"*50)
        if response.status_code == 200:
            films_data = pd.DataFrame(response.json())
            
            # Récupérer les prédictions
            predictions_response = requests.get(f"{URL_API_CRUD}/predictions/", headers=headers)
            if predictions_response.status_code == 200:
                predictions_data = pd.DataFrame(predictions_response.json())
                
                # Fusionner les films avec leurs prédictions
                if not predictions_data.empty:
                    films_data = films_data.merge(
                        predictions_data[['id_film', 'prediction_entrees', 'date_prediction']], 
                        on='id_film', 
                        how='left'
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

# Fonction pour filtrer les films de la semaine
def get_weekly_films(films_df: pd.DataFrame) -> pd.DataFrame:
    """Filtre les films sortis cette semaine"""
    if films_df.empty:
        return films_df
    
    # Convertir la colonne date_sortie en datetime
    films_df['date_sortie'] = pd.to_datetime(films_df['date_sortie'], errors='coerce')
    
    # Calculer la date de début de semaine (lundi)
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Filtrer les films de cette semaine
    weekly_films = films_df[
        (films_df['date_sortie'] >= start_of_week) & 
        (films_df['date_sortie'] <= end_of_week)
    ].copy()
    
    return weekly_films

# Fonction pour classer les films par performance
def classify_film_performance(prediction) -> str:
    """Classe un film selon sa prédiction d'entrées"""
    # Gérer les valeurs None ou NaN
    if prediction is None or pd.isna(prediction):
        return "unknown"
    
    print("*"*50)
    print(prediction)
    print("*"*50)   
    
    if prediction >= 1000000:  # Plus d'1 million d'entrées
        return "top"
    elif prediction >= 500000:  # Plus de 500k entrées
        return "good"
    elif prediction >= 100000:  # Plus de 100k entrées
        return "average"
    else:
        return "poor"

# Fonction pour obtenir l'icône de performance
def get_performance_icon(performance: str) -> str:
    icons = {
        "top": "🥇",
        "good": "🥈", 
        "average": "🥉",
        "poor": "⚠️",
        "unknown": "❓"
    }
    return icons.get(performance, "❓")

def format_budget(budget) -> str:
    """Formate le budget de manière sécurisée"""
    if pd.isna(budget) or budget is None:
        return "N/A"
    try:
        return f"{budget:,.0f} €"
    except:
        return "N/A"

def format_duration(duration) -> str:
    """Formate la durée de manière sécurisée"""
    if pd.isna(duration) or duration is None:
        return "N/A"
    return f"{duration} min"

def format_prediction_metric(prediction) -> str:
    """Formate la prédiction pour les métriques"""
    if pd.notna(prediction):
        return f"{prediction:,.0f}"
    return "N/A"

# Interface utilisateur
def main():
    # Sidebar pour l'authentification
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/cinema-.png", width=100)
        st.title("🎭 CinéOracle")
        
        if not st.session_state["authentication_status"]:
            # Onglets pour Connexion et Inscription
            tab1, tab2 = st.tabs(["🔑 Connexion", "📝 Inscription"])
            
            with tab1:
                st.subheader("Connexion")
                username = st.text_input("👤 Nom d'utilisateur", key="login_username")
                password = st.text_input("🔑 Mot de passe", type="password", key="login_password")
                
                if st.button("Se connecter", key="login"):
                    if authenticate(username, password):
                        st.session_state["authentication_status"] = True
                        # Réinitialiser le statut d'inscription
                        st.session_state["registration_success"] = False
                        st.session_state["registration_message"] = ""
                        st.success("✅ Connexion réussie!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Identifiants incorrects")
            
            with tab2:
                st.subheader("Inscription")
                
                # Afficher le message de succès si l'inscription a réussi
                if st.session_state["registration_success"]:
                    st.success(st.session_state["registration_message"])
                    st.info("🔄 Allez maintenant dans l'onglet 'Connexion' pour vous connecter avec vos identifiants.")
                    
                    # Bouton pour réinitialiser et permettre une nouvelle inscription
                    if st.button("📝 Créer un autre compte", key="new_registration"):
                        st.session_state["registration_success"] = False
                        st.session_state["registration_message"] = ""
                        st.rerun()
                else:
                    # Formulaire d'inscription normal
                    new_username = st.text_input("👤 Nouveau nom d'utilisateur", key="register_username")
                    new_password = st.text_input("🔑 Nouveau mot de passe", type="password", key="register_password")
                    confirm_password = st.text_input("🔐 Confirmer le mot de passe", type="password", key="confirm_password")
                    
                    # Afficher des informations d'aide
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

    # Contenu principal
    if st.session_state["authentication_status"]:
        st.title("📊 Par les pouvoirs qui me sont conférés, je vous présente les prédictions de la première semaine!")
        
        # Informations sur la semaine
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        st.info(f"📅 **Semaine du {start_of_week.strftime('%d/%m/%Y')} au {end_of_week.strftime('%d/%m/%Y')}**")
        
        # Chargement des films
        with st.spinner("Chargement des données..."):
            films_df = fetch_films_with_predictions()
        
        if not films_df.empty:
            # Filtrer les films de la semaine
            weekly_films = get_weekly_films(films_df)
            
            if not weekly_films.empty:
                # Trier par prédiction (du meilleur au moins bien)
                weekly_films = weekly_films.sort_values('prediction_entrees', ascending=False)
                
                # Ajouter la classification de performance
                weekly_films['performance'] = weekly_films['prediction_entrees'].apply(classify_film_performance)
                
                # Affichage du classement
                st.subheader("🏆 Classement des films de la semaine")
                
                # Métriques globales
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Nombre de films", len(weekly_films))
                with col2:
                    # Calculer la moyenne en excluant les valeurs None
                    valid_predictions = weekly_films['prediction_entrees'].dropna()
                    avg_prediction = valid_predictions.mean() if not valid_predictions.empty else 0
                    st.metric("Moyenne des prédictions", f"{avg_prediction:,.0f}")
                with col3:
                    st.metric("Meilleur film", weekly_films.iloc[0]['titre'][:20] + "..." if len(weekly_films.iloc[0]['titre']) > 20 else weekly_films.iloc[0]['titre'])
                with col4:
                    # Calculer le max en excluant les valeurs None
                    max_prediction = valid_predictions.max() if not valid_predictions.empty else 0
                    st.metric("Prédiction max", f"{max_prediction:,.0f}")
                
                # Affichage des films par performance
                tabs = st.tabs(["🥇 Top Films", "🥈 Films Prometteurs", "🥉 Films Moyens", "⚠️ Films à Risque"])
                
                # Top films (plus d'1M d'entrées)
                with tabs[0]:
                    top_films = weekly_films[weekly_films['performance'] == 'top']
                    if not top_films.empty:
                        for _, film in top_films.iterrows():
                            with st.container():
                                col1, col2, col3 = st.columns([2, 1, 1])
                                with col1:
                                    st.markdown(f"""
                                    <div class="film-card top-film">
                                        <h4>{get_performance_icon('top')} {film['titre']}</h4>
                                        <p><strong>Genre:</strong> {film['genre']} | <strong>Studio:</strong> {film['studio']}</p>
                                        <p><strong>Durée:</strong> {format_duration(film['duree'])} | <strong>Budget:</strong> {format_budget(film['budget'])}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                with col2:
                                    st.metric("Prédiction", format_prediction_metric(film['prediction_entrees']))
                                with col3:
                                    st.write(f"📅 {film['date_sortie'].strftime('%d/%m')}")
                    else:
                        st.info("Aucun film dans cette catégorie cette semaine")
                
                # Films prometteurs (500k-1M entrées)
                with tabs[1]:
                    good_films = weekly_films[weekly_films['performance'] == 'good']
                    if not good_films.empty:
                        for _, film in good_films.iterrows():
                            with st.container():
                                col1, col2, col3 = st.columns([2, 1, 1])
                                with col1:
                                    st.markdown(f"""
                                    <div class="film-card good-film">
                                        <h4>{get_performance_icon('good')} {film['titre']}</h4>
                                        <p><strong>Genre:</strong> {film['genre']} | <strong>Studio:</strong> {film['studio']}</p>
                                        <p><strong>Durée:</strong> {format_duration(film['duree'])} | <strong>Budget:</strong> {format_budget(film['budget'])}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                with col2:
                                    st.metric("Prédiction", format_prediction_metric(film['prediction_entrees']))
                                with col3:
                                    st.write(f"📅 {film['date_sortie'].strftime('%d/%m')}")
                    else:
                        st.info("Aucun film dans cette catégorie cette semaine")
                
                # Films moyens (100k-500k entrées)
                with tabs[2]:
                    avg_films = weekly_films[weekly_films['performance'] == 'average']
                    if not avg_films.empty:
                        for _, film in avg_films.iterrows():
                            with st.container():
                                col1, col2, col3 = st.columns([2, 1, 1])
                                with col1:
                                    st.markdown(f"""
                                    <div class="film-card average-film">
                                        <h4>{get_performance_icon('average')} {film['titre']}</h4>
                                        <p><strong>Genre:</strong> {film['genre']} | <strong>Studio:</strong> {film['studio']}</p>
                                        <p><strong>Durée:</strong> {format_duration(film['duree'])} | <strong>Budget:</strong> {format_budget(film['budget'])}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                with col2:
                                    st.metric("Prédiction", format_prediction_metric(film['prediction_entrees']))
                                with col3:
                                    st.write(f"📅 {film['date_sortie'].strftime('%d/%m')}")
                    else:
                        st.info("Aucun film dans cette catégorie cette semaine")
                
                # Films à risque (moins de 100k entrées)
                with tabs[3]:
                    poor_films = weekly_films[weekly_films['performance'] == 'poor']
                    if not poor_films.empty:
                        for _, film in poor_films.iterrows():
                            with st.container():
                                col1, col2, col3 = st.columns([2, 1, 1])
                                with col1:
                                    st.markdown(f"""
                                    <div class="film-card poor-film">
                                        <h4>{get_performance_icon('poor')} {film['titre']}</h4>
                                        <p><strong>Genre:</strong> {film['genre']} | <strong>Studio:</strong> {film['studio']}</p>
                                        <p><strong>Durée:</strong> {format_duration(film['duree'])} | <strong>Budget:</strong> {format_budget(film['budget'])}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                with col2:
                                    st.metric("Prédiction", format_prediction_metric(film['prediction_entrees']))
                                with col3:
                                    st.write(f"📅 {film['date_sortie'].strftime('%d/%m')}")
                    else:
                        st.info("Aucun film dans cette catégorie cette semaine")
                
                # Graphiques
                st.subheader("📈 Analyses visuelles")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Graphique des prédictions par film
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
                
                with col2:
                    # Graphique des prédictions moyennes par genre
                    genre_avg = weekly_films.groupby('genre')['prediction_entrees'].mean().reset_index()
                    fig2 = px.pie(
                        genre_avg,
                        values='prediction_entrees',
                        names='genre',
                        title="Répartition des prédictions par genre"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Tableau complet
                st.subheader("📋 Tableau complet des films de la semaine")
                
                # Préparer les données pour l'affichage
                display_df = weekly_films[['titre', 'genre', 'studio', 'budget', 'duree', 'date_sortie', 'prediction_entrees']].copy()
                
                # Formater les colonnes de manière sécurisée
                display_df['budget_formatted'] = display_df['budget'].apply(format_budget)
                display_df['duree_formatted'] = display_df['duree'].apply(format_duration)
                display_df['date_formatted'] = display_df['date_sortie'].apply(
                    lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) else 'N/A'
                )
                display_df['prediction_formatted'] = display_df['prediction_entrees'].apply(
                    lambda x: f"{x:,.0f}" if pd.notna(x) else 'N/A'
                )
                
                # Afficher le tableau avec les colonnes formatées
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
                st.warning("⚠️ Aucun film sorti cette semaine dans la base de données")
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
