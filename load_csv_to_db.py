#!/usr/bin/env python3
"""
Script pour charger les films fictifs depuis un fichier CSV vers la base de données.
Ce script fait partie de la deuxième source de données pour la certification.
Configuration basée sur les fichiers .env du projet.
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error as MySQLError
import os
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CSVToDBLoader:
    """Classe pour charger des données CSV dans la base de données MySQL"""
    
    def __init__(self):
        """
        Initialise la connexion à la base de données
        Configuration basée sur les fichiers .env du projet :
        - .env racine : MYSQL_USER=kevin, MYSQL_PASSWORD=kevinpass
        - cinapps_api/.env : DATABASE_URL=mysql+pymysql://kevin:kevinpass@localhost:3306/cinapps
        - API_s/.env : DATABASE_URL=mysql+pymysql://kevin:kevinpass@localhost:3306/cinapps
        """
        self.db_config = {
            'host': 'localhost',       # Consistent across all .env files
            'port': 3306,             # Standard MySQL port
            'database': 'cinapps',    # Database name from .env files
            'user': 'kevin',          # MYSQL_USER from root .env
            'password': 'kevinpass',  # MYSQL_PASSWORD from root .env
            'charset': 'utf8mb4',     # From DATABASE_URL charset
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': False,      # For transaction control
            'raise_on_warnings': True
        }
        self.connection = None
        self.cursor = None
    
    def connect_db(self):
        """Établit la connexion à la base de données"""
        try:
            logger.info("🔌 Configuration de connexion :")
            logger.info(f"   Host: {self.db_config['host']}:{self.db_config['port']}")
            logger.info(f"   Database: {self.db_config['database']}")
            logger.info(f"   User: {self.db_config['user']}")
            logger.info(f"   Charset: {self.db_config['charset']}")
            
            self.connection = mysql.connector.connect(**self.db_config)
            self.cursor = self.connection.cursor()
            
            # Test de la connexion
            self.cursor.execute("SELECT DATABASE(), USER(), VERSION()")
            db_info = self.cursor.fetchone()
            logger.info(f"✅ Connexion établie à MySQL {db_info[2]}")
            logger.info(f"📊 Base active: {db_info[0]} | Utilisateur: {db_info[1]}")
            
            # Vérifier que la table film_fictif existe
            self.cursor.execute("SHOW TABLES LIKE 'film_fictif'")
            if not self.cursor.fetchone():
                logger.error("❌ Table 'film_fictif' introuvable !")
                logger.error("💡 Exécutez d'abord : mysql -u kevin -pkevinpass cinapps < mysql-init/init_bdd_app.sql")
                return False
            
            logger.info("✅ Table 'film_fictif' trouvée")
            return True
            
        except MySQLError as e:
            logger.error(f"❌ Erreur de connexion MySQL : {e}")
            logger.error("💡 Vérifications à faire :")
            logger.error("   1. Docker MySQL lancé : docker-compose up mysql -d")
            logger.error("   2. Port 3306 accessible : netstat -an | grep 3306")
            logger.error("   3. Identifiants corrects dans .env")
            logger.error("   4. Base 'cinapps' créée")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur inattendue : {e}")
            return False
    
    def disconnect_db(self):
        """Ferme la connexion à la base de données"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("🔌 Connexion fermée")
    
    def clean_existing_data(self):
        """Supprime les données existantes de source fichier_plat"""
        try:
            # Compter les enregistrements existants
            count_query = "SELECT COUNT(*) FROM film_fictif WHERE source = 'fichier_plat'"
            self.cursor.execute(count_query)
            existing_count = self.cursor.fetchone()[0]
            
            if existing_count > 0:
                logger.info(f"🗑️ {existing_count} films fictifs existants trouvés")
                
                # Supprimer
                delete_query = "DELETE FROM film_fictif WHERE source = 'fichier_plat'"
                self.cursor.execute(delete_query)
                deleted_rows = self.cursor.rowcount
                self.connection.commit()
                
                logger.info(f"🧹 {deleted_rows} enregistrements supprimés")
            else:
                logger.info("ℹ️ Aucun film fictif existant (première insertion)")
            
            return True
            
        except MySQLError as e:
            logger.error(f"❌ Erreur lors du nettoyage : {e}")
            self.connection.rollback()
            return False
    
    def load_csv_data(self, csv_file_path):
        """
        Charge les données depuis un fichier CSV vers la table film_fictif
        
        Args:
            csv_file_path (str): Chemin vers le fichier CSV
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            # Vérifier l'existence du fichier
            if not os.path.exists(csv_file_path):
                logger.error(f"❌ Fichier CSV introuvable : {csv_file_path}")
                logger.error(f"💡 Chemin actuel : {os.getcwd()}")
                logger.error(f"💡 Fichiers disponibles : {os.listdir('.')}")
                return False
            
            # Lire le fichier CSV
            logger.info(f"📖 Lecture du fichier : {csv_file_path}")
            df = pd.read_csv(csv_file_path)
            logger.info(f"📊 {len(df)} lignes lues")
            logger.info(f"📝 Colonnes : {list(df.columns)}")
            
            # Nettoyer les données existantes
            if not self.clean_existing_data():
                return False
            
            # Préparer la requête d'insertion
            insert_query = """
            INSERT INTO film_fictif (
                titre, acteurs, budget, compositeur, duree, entrees_premiere_semaine,
                franchise, genre, pays, producteur, realisateur, remake,
                salles_premiere_semaine, studio, scoring_acteurs, scoring_acteurs_realisateurs,
                season, coeff_studio, year, source
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            # Insérer chaque ligne avec gestion d'erreurs détaillée
            success_count = 0
            error_count = 0
            
            logger.info("🚀 Début de l'insertion...")
            
            for index, row in df.iterrows():
                try:
                    # Préparer les données avec conversion de types appropriée
                    data = (
                        str(row['titre']),
                        str(row['acteurs']),
                        int(row['budget']) if pd.notna(row['budget']) else None,
                        str(row['compositeur']) if pd.notna(row['compositeur']) else None,
                        int(row['duree']) if pd.notna(row['duree']) else None,
                        int(row['entrees_premiere_semaine']) if pd.notna(row['entrees_premiere_semaine']) else None,
                        str(row['franchise']) if pd.notna(row['franchise']) else None,
                        str(row['genre']),
                        str(row['pays']),
                        str(row['producteur']) if pd.notna(row['producteur']) else None,
                        str(row['realisateur']) if pd.notna(row['realisateur']) else None,
                        str(row['remake']) if pd.notna(row['remake']) else None,
                        int(row['salles_premiere_semaine']) if pd.notna(row['salles_premiere_semaine']) else None,
                        str(row['studio']),
                        float(row['scoring_acteurs']) if pd.notna(row['scoring_acteurs']) else None,
                        float(row['scoring_acteurs_realisateurs']) if pd.notna(row['scoring_acteurs_realisateurs']) else None,
                        str(row['season']) if pd.notna(row['season']) else None,
                        int(row['coeff_studio']) if pd.notna(row['coeff_studio']) else None,
                        int(row['year']) if pd.notna(row['year']) else None,
                        'fichier_plat'
                    )
                    
                    self.cursor.execute(insert_query, data)
                    success_count += 1
                    logger.info(f"✅ [{success_count:2d}/10] {row['titre']}")
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"❌ Erreur film '{row['titre']}' : {e}")
                    logger.error(f"   Données : {data}")
            
            # Valider toutes les insertions
            self.connection.commit()
            
            logger.info("=" * 50)
            logger.info(f"🎯 RÉSUMÉ FINAL :")
            logger.info(f"   ✅ Succès : {success_count} films")
            logger.info(f"   ❌ Erreurs : {error_count} films")
            logger.info(f"   📊 Taux de réussite : {(success_count/len(df)*100):.1f}%")
            
            return error_count == 0
            
        except Exception as e:
            logger.error(f"❌ Erreur générale : {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def verify_load(self):
        """Vérifie le chargement avec des statistiques détaillées"""
        try:
            # Compter les films
            count_query = "SELECT COUNT(*) FROM film_fictif WHERE source = 'fichier_plat'"
            self.cursor.execute(count_query)
            count = self.cursor.fetchone()[0]
            
            logger.info("=" * 50)
            logger.info(f"📊 VÉRIFICATION POST-CHARGEMENT")
            logger.info(f"   Films en base : {count}")
            
            if count > 0:
                # Statistiques par genre
                stats_query = """
                SELECT genre, COUNT(*) as nb_films, AVG(budget) as budget_moyen
                FROM film_fictif 
                WHERE source = 'fichier_plat' 
                GROUP BY genre 
                ORDER BY nb_films DESC
                """
                self.cursor.execute(stats_query)
                stats = self.cursor.fetchall()
                
                logger.info("   Répartition par genre :")
                for genre, nb, budget_moy in stats:
                    budget_str = f"{budget_moy:,.0f}€" if budget_moy else "N/A"
                    logger.info(f"     - {genre}: {nb} films (budget moy: {budget_str})")
                
                # Exemples de films
                sample_query = """
                SELECT titre, genre, pays, budget 
                FROM film_fictif 
                WHERE source = 'fichier_plat' 
                ORDER BY budget DESC 
                LIMIT 3
                """
                self.cursor.execute(sample_query)
                samples = self.cursor.fetchall()
                
                logger.info("   Top 3 budgets :")
                for titre, genre, pays, budget in samples:
                    budget_str = f"{budget:,}€" if budget else "N/A"
                    logger.info(f"     - {titre} ({genre}, {pays}) : {budget_str}")
            
            return count
            
        except MySQLError as e:
            logger.error(f"❌ Erreur lors de la vérification : {e}")
            return 0

def main():
    """Fonction principale"""
    csv_file = "films_fictifs_source2.csv"
    
    logger.info("🚀 CHARGEMENT FILMS FICTIFS - SOURCE FICHIER PLAT")
    logger.info("=" * 50)
    
    # Créer l'instance du loader
    loader = CSVToDBLoader()
    
    try:
        # Connexion
        if not loader.connect_db():
            return False
        
        # Chargement
        success = loader.load_csv_data(csv_file)
        
        if success:
            # Vérification
            count = loader.verify_load()
            logger.info("=" * 50)
            logger.info(f"🎉 SUCCÈS ! {count} films chargés en base")
            logger.info("💡 Prochaine étape : Vérifier dans votre API/Streamlit")
        else:
            logger.error("❌ ÉCHEC du chargement")
            
        return success
        
    except KeyboardInterrupt:
        logger.info("⚠️ Interruption utilisateur")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur fatale : {e}")
        return False
    finally:
        loader.disconnect_db()

if __name__ == "__main__":
    print("🎬 CHARGEUR CSV → BASE DE DONNÉES")
    print("📋 Configuration : MySQL kevin@localhost:3306/cinapps")
    print("📁 Fichier source : films_fictifs_source2.csv")
    print("🎯 Table cible : film_fictif")
    print()
    
    success = main()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ PROCESSUS TERMINÉ AVEC SUCCÈS !")
        print("💡 Votre deuxième source de données est opérationnelle")
    else:
        print("❌ PROCESSUS TERMINÉ AVEC ERREURS")
        print("💡 Vérifiez les logs ci-dessus pour diagnostiquer")
    print("=" * 50) 