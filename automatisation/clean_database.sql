-- Script de nettoyage de la base de données
-- À exécuter avant chaque scraping

USE cinapps;

-- Désactiver les contraintes de clé étrangère
SET FOREIGN_KEY_CHECKS = 0;

-- Vider toutes les tables dans l'ordre correct
TRUNCATE TABLE table_predictions;
TRUNCATE TABLE table_participations;
TRUNCATE TABLE table_films;
TRUNCATE TABLE table_personnes;

-- Réactiver les contraintes
SET FOREIGN_KEY_CHECKS = 1;

-- Vérifier que les tables sont vides
SELECT 'table_predictions' as table_name, COUNT(*) as count FROM table_predictions
UNION ALL
SELECT 'table_participations' as table_name, COUNT(*) as count FROM table_participations
UNION ALL
SELECT 'table_films' as table_name, COUNT(*) as count FROM table_films
UNION ALL
SELECT 'table_personnes' as table_name, COUNT(*) as count FROM table_personnes;

-- Message de confirmation
SELECT '✅ Base de données nettoyée avec succès' as status; 