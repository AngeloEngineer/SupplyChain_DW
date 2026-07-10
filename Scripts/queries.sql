CREATE DATABASE SupplyChain_DW ;
USE SupplyChain_DW;
--Création d'un schema d'atterissage
--On va isoler l'ingestion dans un schéma dédié nommé enregistrements

CREATE SCHEMA enregistrements;
GO

--Création d'une table de suivie du Watermark
/**
Cette table va mémoriser jusqu'à quelle date mon pipeline a lu le fichier CSV 
pour éviter de réimporter l'intégralité du dataset à chaque exécution
**/

CREATE TABLE enregistrements.watermark_tracking(
    table_name VARCHAR(100) PRIMARY KEY,
    last_load_date DATETIME
);
GO

-- Initialisation": On va dire au systèmes de charger les données à partir du 1er janvier 
INSERT INTO enregistrements.watermark_tracking(table_name, last_load_date)
VALUES ('raw_orders', '2015-01-01 00:00:00') ;
GO

--SELECT * FROM enregistrements.watermark_tracking ;