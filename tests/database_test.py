# tests/database_test.py
# Configuration base de données pour les tests
import os
import sqlite3
from sqlalchemy import create_engine, text
import bcrypt

def setup_test_database():
    """Setup base SQLite pour les tests CI"""
    
    # Vérifier si on est en environnement CI
    if os.getenv('GITHUB_ACTIONS'):
        print("🔧 Configuration SQLite pour CI...")
        
        # Supprimer l'ancienne base si elle existe
        db_path = "test_cinapps.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            print("🗑️  Ancienne base SQLite supprimée")
        
        # Créer la nouvelle base SQLite
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Créer les tables nécessaires (structure minimale)
        cursor.execute("""
            CREATE TABLE main_user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE Films (
                id_film INTEGER PRIMARY KEY AUTOINCREMENT,
                titre VARCHAR(255) NOT NULL,
                annee_sortie INTEGER,
                genre VARCHAR(100),
                duree INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE table_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_film INTEGER,
                prediction_entrees INTEGER
            )
        """)
        
        # Créer l'utilisateur de test avec mot de passe hashé
        test_password = "test123"
        # Hash simple pour les tests (même logique que votre app)
        hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute("""
            INSERT INTO main_user (username, password) 
            VALUES (?, ?)
        """, ("testuser", hashed.decode('utf-8')))
        
        conn.commit()
        conn.close()
        
        print("✅ Base SQLite créée avec utilisateur testuser")
        
        # Retourner l'URL de la base SQLite
        return f"sqlite:///{db_path}"
    
    else:
        print("🔧 Utilisation MySQL local...")
        # Utiliser MySQL local (config normale)
        return None

def get_test_database_url():
    """Retourner l'URL de base appropriée pour les tests"""
    
    # Si on est en CI, utiliser SQLite
    if os.getenv('GITHUB_ACTIONS'):
        return setup_test_database()
    
    # Sinon, utiliser MySQL local
    mysql_url = os.getenv("DATABASE_URL", "mysql+pymysql://db_user:user_mdp@127.0.0.1:3306/db_name")
    return mysql_url