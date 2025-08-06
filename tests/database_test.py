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
        
        # Créer une base SQLite vide - on laisse l'API créer ses tables
        conn = sqlite3.connect(db_path)
        conn.close()
        print("📝 Base SQLite vide créée - l'API va créer les tables")
        
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

def insert_test_user():
    """Insérer l'utilisateur de test APRÈS que l'API ait créé les tables"""
    if os.getenv('GITHUB_ACTIONS'):
        print("👤 Insertion utilisateur testuser...")
        
        conn = sqlite3.connect("test_cinapps.db")
        cursor = conn.cursor()
        
        # Vérifier quelle structure la table a
        cursor.execute("PRAGMA table_info(main_user)")
        columns = cursor.fetchall()
        print(f"📋 Structure détectée: {columns}")
        
        # Adapter selon la structure trouvée
        password_column = "password"
        for col in columns:
            if "password" in col[1].lower():
                password_column = col[1]
                break
        
        test_password = "test123"
        hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
        
        cursor.execute(f"""
            INSERT OR REPLACE INTO main_user (username, {password_column}) 
            VALUES (?, ?)
        """, ("testuser", hashed.decode('utf-8')))
        
        conn.commit()
        conn.close()
        print(f"✅ Utilisateur testuser inséré avec colonne {password_column}")