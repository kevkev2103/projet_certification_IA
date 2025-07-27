import mysql.connector
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de la base de données
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'cinapps',
    'user': 'kevin',
    'password': 'kevinpass',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

def clean_duplicate_predictions():
    """Nettoie les prédictions dupliquées"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Compter les prédictions avant nettoyage
        cursor.execute("SELECT COUNT(*) FROM prediction_fictive")
        count_before = cursor.fetchone()[0]
        logger.info(f"📊 Prédictions avant nettoyage: {count_before}")
        
        # Supprimer TOUTES les prédictions fictives pour repartir à zéro
        cursor.execute("DELETE FROM prediction_fictive")
        connection.commit()
        
        # Vérifier le nettoyage
        cursor.execute("SELECT COUNT(*) FROM prediction_fictive")
        count_after = cursor.fetchone()[0]
        logger.info(f"🧹 Prédictions après nettoyage: {count_after}")
        
        logger.info("✅ Nettoyage terminé - Table prediction_fictive vidée")
        logger.info("💡 Vous pouvez maintenant relancer le pipeline sans doublons")
        
    except mysql.connector.Error as e:
        logger.error(f"❌ Erreur: {e}")
        connection.rollback()
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    logger.info("🚀 NETTOYAGE DES PRÉDICTIONS FICTIVES DUPLIQUÉES")
    logger.info("=" * 50)
    clean_duplicate_predictions() 