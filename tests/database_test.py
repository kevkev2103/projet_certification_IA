# tests/database_test.py
# Configuration base de données pour les tests
import os
import sqlite3
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# 🔐 Configuration pour pbkdf2_sha256 (compatible Django) - MÊME QUE L'API
pwd_context = CryptContext(schemes=["django_pbkdf2_sha256"], deprecated="auto")

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
        
        # Créer la base SQLite avec la table main_user PRÊTE
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Créer la table main_user AVANT que l'API démarre
        cursor.execute("""
            CREATE TABLE main_user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL
            )
        """)
        
        # Créer l'utilisateur de test avec la MÊME méthode de hachage que l'API
        test_password = "test123"
        hashed = pwd_context.hash(test_password)  # Utilise django_pbkdf2_sha256 comme l'API
        
        cursor.execute("""
            INSERT INTO main_user (username, hashed_password) 
            VALUES (?, ?)
        """, ("testuser", hashed))
        
        conn.commit()
        conn.close()
        
        print("✅ Base SQLite créée avec table main_user et utilisateur testuser")
        print(f"🔐 Hash utilisé: {hashed[:50]}...")
        
        # Retourner l'URL de la base SQLite
        return f"sqlite:///{db_path}"
    
    else:
        print("🔧 Utilisation MySQL local...")
        return None

def get_test_database_url():
    """Retourner l'URL de base appropriée pour les tests"""
    
    # Si on est en CI, utiliser SQLite
    if os.getenv('GITHUB_ACTIONS'):
        return setup_test_database()
    
    # Sinon, utiliser MySQL local
    mysql_url = os.getenv("DATABASE_URL", "mysql+pymysql://db_user:user_mdp@127.0.0.1:3306/db_name")
    return mysql_url