create database if not exists bdd_projet;
use bdd_projet; -- à partir de maintenant je ne travaille que sur cette bdd

create table if not exists table_films (

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
 film_url VARCHAR(255)

);

CREATE TABLE IF NOT EXISTS table_personnes (
 id_personne INT AUTO_INCREMENT PRIMARY KEY,
 nom VARCHAR(255) NOT NULL
);

create table if not exists table_participations (
 id_film INT,
 id_personne INT,
 role ENUM('acteur', 'realisateur') NOT NULL,
 PRIMARY KEY (id_film, id_personne, role),
 FOREIGN KEY (id_film) REFERENCES table_films(id_film) ON DELETE CASCADE,
 FOREIGN KEY (id_personne) REFERENCES table_personnes(id_personne) ON DELETE CASCADE

);

