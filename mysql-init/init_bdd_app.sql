CREATE DATABASE IF NOT EXISTS cinapps;
USE cinapps;

CREATE TABLE IF NOT EXISTS main_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS table_films (
    id_film INT AUTO_INCREMENT PRIMARY KEY,
    titre VARCHAR(255) NOT NULL,
    duree INT,
    salles INT,
    genre VARCHAR(255),
    date_sortie DATE,
    pays VARCHAR(255),
    studio VARCHAR(255),
    description TEXT,
    image VARCHAR(255),
    budget INT,
    entrees INT,
    anecdotes VARCHAR(255),
    film_url VARCHAR(255),
    is_pred BOOLEAN DEFAULT FALSE
);

-- NOUVELLE TABLE POUR LES FILMS FICTIFS (SOURCE FICHIER PLAT)
CREATE TABLE IF NOT EXISTS film_fictif (
    id_film_fictif INT AUTO_INCREMENT PRIMARY KEY,
    titre VARCHAR(255) NOT NULL,
    acteurs TEXT,
    budget INT,
    compositeur VARCHAR(255),
    duree INT,
    entrees_premiere_semaine INT,
    franchise VARCHAR(255),
    genre VARCHAR(255),
    pays VARCHAR(255),
    producteur VARCHAR(255),
    realisateur VARCHAR(255),
    remake VARCHAR(255),
    salles_premiere_semaine INT,
    studio VARCHAR(255),
    scoring_acteurs DECIMAL(18,16),
    scoring_acteurs_realisateurs DECIMAL(18,16),
    season VARCHAR(50),
    coeff_studio INT,
    year INT,
    date_import TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) DEFAULT 'fichier_plat'
);

CREATE TABLE IF NOT EXISTS table_personnes (
    id_personne INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS table_participations (
    id_film INT,
    id_personne INT,
    role ENUM('acteur', 'realisateur') NOT NULL,
    PRIMARY KEY (id_film, id_personne, role),
    FOREIGN KEY (id_film) REFERENCES table_films(id_film) ON DELETE CASCADE,
    FOREIGN KEY (id_personne) REFERENCES table_personnes(id_personne) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS table_predictions (
    id_prediction INT AUTO_INCREMENT PRIMARY KEY,
    id_film INT NOT NULL,
    prediction_entrees INT NOT NULL,
    date_prediction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_film) REFERENCES table_films(id_film) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS prediction_fictive (
    id_prediction_fictive INT AUTO_INCREMENT PRIMARY KEY,
    id_film_fictif INT NOT NULL,
    prediction_entrees INT NOT NULL,
    date_prediction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_film_fictif) REFERENCES film_fictif(id_film_fictif) ON DELETE CASCADE
);

-- Créer un utilisateur de test (mot de passe: test123)
INSERT INTO main_user (username, password) 
VALUES ('testuser', 'pbkdf2_sha256$29000$s71byRcadMpk$YcEo+pttw3UVB/gpNS26xrc8bcX9OmzYjkPuSAviec0=')
ON DUPLICATE KEY UPDATE username=username;

