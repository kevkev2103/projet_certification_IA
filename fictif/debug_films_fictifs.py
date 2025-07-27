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

def debug_films_fictifs():
    """Analyse la table film_fictif pour détecter les doublons"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        logger.info("🔍 ANALYSE DE LA TABLE film_fictif")
        logger.info("=" * 50)
        
        # 1. Compter total des films
        cursor.execute("SELECT COUNT(*) as total FROM film_fictif")
        total = cursor.fetchone()['total']
        logger.info(f"📊 Total films dans film_fictif: {total}")
        
        # 2. Vérifier les doublons par titre
        cursor.execute("""
            SELECT titre, COUNT(*) as nb_occurences 
            FROM film_fictif 
            GROUP BY titre 
            HAVING COUNT(*) > 1
            ORDER BY nb_occurences DESC
        """)
        doublons_titre = cursor.fetchall()
        
        if doublons_titre:
            logger.warning(f"⚠️  DOUBLONS DÉTECTÉS par titre:")
            for row in doublons_titre:
                logger.warning(f"   - '{row['titre']}': {row['nb_occurences']} occurrences")
        else:
            logger.info("✅ Aucun doublon par titre")
        
        # 3. Lister tous les films avec leurs IDs
        cursor.execute("""
            SELECT id_film_fictif, titre, source, date_import 
            FROM film_fictif 
            ORDER BY id_film_fictif
        """)
        tous_films = cursor.fetchall()
        
        logger.info(f"\n📋 LISTE COMPLÈTE DES FILMS ({len(tous_films)}):")
        for film in tous_films:
            logger.info(f"   ID:{film['id_film_fictif']:2d} | {film['titre']} | {film['source']} | {film['date_import']}")
        
        # 4. Vérifier les prédictions existantes
        cursor.execute("SELECT COUNT(*) as total FROM prediction_fictive")
        predictions_total = cursor.fetchone()['total']
        logger.info(f"\n🎯 Total prédictions: {predictions_total}")
        
        # 5. Analyser les prédictions par film
        cursor.execute("""
            SELECT pf.id_film_fictif, ff.titre, COUNT(*) as nb_predictions
            FROM prediction_fictive pf
            JOIN film_fictif ff ON pf.id_film_fictif = ff.id_film_fictif
            GROUP BY pf.id_film_fictif, ff.titre
            ORDER BY pf.id_film_fictif
        """)
        predictions_par_film = cursor.fetchall()
        
        if predictions_par_film:
            logger.info("\n🎬 PRÉDICTIONS PAR FILM:")
            for pred in predictions_par_film:
                status = "⚠️ MULTIPLE" if pred['nb_predictions'] > 1 else "✅"
                logger.info(f"   {status} Film ID:{pred['id_film_fictif']:2d} | {pred['titre']} | {pred['nb_predictions']} prédiction(s)")
        
        # 6. Identifier les films sans prédiction
        cursor.execute("""
            SELECT ff.id_film_fictif, ff.titre
            FROM film_fictif ff
            LEFT JOIN prediction_fictive pf ON ff.id_film_fictif = pf.id_film_fictif
            WHERE pf.id_prediction_fictive IS NULL
            ORDER BY ff.id_film_fictif
        """)
        films_sans_pred = cursor.fetchall()
        
        logger.info(f"\n📝 Films SANS prédiction ({len(films_sans_pred)}):")
        for film in films_sans_pred:
            logger.info(f"   ID:{film['id_film_fictif']:2d} | {film['titre']}")
        
        logger.info("=" * 50)
        logger.info("🎯 DIAGNOSTIC:")
        if total > 10:
            logger.warning(f"   ⚠️  Trop de films dans film_fictif ({total} au lieu de 10)")
        if predictions_total > 10:
            logger.warning(f"   ⚠️  Trop de prédictions ({predictions_total} au lieu de 10)")
        if doublons_titre:
            logger.warning("   ⚠️  Doublons détectés dans film_fictif")
        if not doublons_titre and total == 10:
            logger.info("   ✅ Structure film_fictif correcte")
            
    except mysql.connector.Error as e:
        logger.error(f"❌ Erreur: {e}")
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    debug_films_fictifs() 