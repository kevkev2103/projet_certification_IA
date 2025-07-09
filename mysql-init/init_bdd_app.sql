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
    film_url VARCHAR(255),
    is_pred BOOLEAN DEFAULT FALSE
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

-- Créer un utilisateur de test (mot de passe: test123)
INSERT INTO main_user (username, password) 
VALUES ('testuser', 'pbkdf2_sha256$29000$s71byRcadMpk$YcEo+pttw3UVB/gpNS26xrc8bcX9OmzYjkPuSAviec0=')
ON DUPLICATE KEY UPDATE username=username;

