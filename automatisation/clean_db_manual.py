#!/usr/bin/env python3
"""
Script de nettoyage manuel de la base de données
À exécuter avant chaque scraping
"""

import mysql.connector
import os
import logging
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

def clean_database():
    """Nettoie manuellement la base de données"""
    
    # Configuration de la base de données
    db_config = {
        'user': os.getenv('MYSQL_USER', 'kevin'),
        'password': os.getenv('MYSQL_PASSWORD', 'kevinpass'),
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'database': os.getenv('MYSQL_DATABASE', 'cinapps')
    }
    
    try:
        logger.info("🔌 Connexion à la base de données...")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        logger.info("🧹 Début du nettoyage de la base de données...")
        
        # Désactiver les contraintes de clé étrangère
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        logger.info("✅ Contraintes de clé étrangère désactivées")
        
        # Tables à nettoyer dans l'ordre
        tables = [
            'table_predictions',
            'table_participations',
            'table_films',
            'table_personnes'
        ]
        
        for table in tables:
            try:
                cursor.execute(f"TRUNCATE TABLE {table};")
                logger.info(f"✅ Table {table} vidée")
            except Exception as e:
                logger.error(f"❌ Erreur lors du vidage de {table}: {e}")
                # Fallback avec DELETE
                try:
                    cursor.execute(f"DELETE FROM {table};")
                    cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1;")
                    logger.info(f"✅ Table {table} vidée avec DELETE")
                except Exception as e2:
                    logger.error(f"❌ Erreur DELETE sur {table}: {e2}")
        
        # Réactiver les contraintes
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        logger.info("✅ Contraintes de clé étrangère réactivées")
        
        # Commit des changements
        conn.commit()
        logger.info("🎉 Base de données nettoyée avec succès!")
        
        # Vérifier que les tables sont vides
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            logger.info(f"📊 Table {table}: {count} enregistrements")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Erreur critique: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise

if __name__ == "__main__":
    logger.info("🚀 Démarrage du nettoyage manuel de la base de données")
    clean_database()
    logger.info("✅ Nettoyage terminé avec succès") 