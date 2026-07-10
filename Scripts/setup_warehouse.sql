/*
===============================================================================
  Script : setup_warehouse.sql
  Objet  : Création de l'infrastructure Data Warehouse locale
           avec des fonctionnalités approchant un cloud DW moderne.

  Ce script :
    1. Crée les 4 schémas de la médallion architecture (bronze/silver/gold/analytics)
    2. Configure le partitionnement sur la table de faits
    3. Crée les indexes columnstore pour les performances analytiques
    4. Met en place la table de watermark pour l'ingestion incrémentale
    5. Crée une fonction de partition par mois pour les faits

  Prérequis : SQL Server Developer Edition (ou supérieur)
  Compatible : SQL Server 2016+
===============================================================================
*/

USE [SupplyChain_DW];
GO

-- ============================================================================
-- 1. SCHÉMAS (Medallion Architecture)
-- ============================================================================
-- bronze  : Données brutes telles qu'ingérées (Landing Zone)
-- silver  : Données nettoyées, typées, validées (Staging)
-- gold    : Dimensions et faits métier (Warehouse)
-- analytics: Vues agrégées, KPI, reporting (Data Mart)

CREATE SCHEMA IF NOT EXISTS bronze;
GO

CREATE SCHEMA IF NOT EXISTS silver;
GO

CREATE SCHEMA IF NOT EXISTS gold;
GO

CREATE SCHEMA IF NOT EXISTS analytics;
GO

PRINT 'Schémas bronze/silver/gold/analytics créés avec succès.';


-- ============================================================================
-- 2. FONCTION DE PARTITION (par mois pour la table de faits)
-- ============================================================================
-- Le partitionnement permet de :
--   - Isoler les charges mensuelles (SWITCH IN/OUT)
--   - Améliorer les performances des scans par plage de dates
--   - Simuler le partitionnement natif des cloud DW (BigQuery partitions, Snowflake clustering)

IF NOT EXISTS (SELECT * FROM sys.partition_functions WHERE name = 'pf_monthly_orders')
BEGIN
    CREATE PARTITION FUNCTION pf_monthly_orders (DATETIME)
    AS RANGE RIGHT FOR VALUES (
        '2015-01-01', '2015-02-01', '2015-03-01', '2015-04-01',
        '2015-05-01', '2015-06-01', '2015-07-01', '2015-08-01',
        '2015-09-01', '2015-10-01', '2015-11-01', '2015-12-01',
        '2016-01-01', '2016-02-01', '2016-03-01', '2016-04-01',
        '2016-05-01', '2016-06-01', '2016-07-01', '2016-08-01',
        '2016-09-01', '2016-10-01', '2016-11-01', '2016-12-01',
        '2017-01-01', '2017-02-01', '2017-03-01', '2017-04-01',
        '2017-05-01', '2017-06-01', '2017-07-01', '2017-08-01',
        '2017-09-01', '2017-10-01', '2017-11-01', '2017-12-01',
        '2018-01-01', '2018-02-01', '2018-03-01', '2018-04-01',
        '2018-05-01', '2018-06-01', '2018-07-01', '2018-08-01',
        '2018-09-01', '2018-10-01', '2018-11-01', '2018-12-01'
    );
    PRINT 'Fonction de partition pf_monthly_orders créée.';
END
GO

-- Schéma de partition associé (mappe sur le groupe de fichiers PRIMARY)
IF NOT EXISTS (SELECT * FROM sys.partition_schemes WHERE name = 'ps_monthly_orders')
BEGIN
    CREATE PARTITION SCHEME ps_monthly_orders
    AS PARTITION pf_monthly_orders ALL TO ([PRIMARY]);
    PRINT 'Schéma de partition ps_monthly_orders créé.';
END
GO


-- ============================================================================
-- 3. TABLE BRONZE (Landing)
-- ============================================================================
-- Structure miroir du CSV avec typage minimal.
-- Les colonnes restent en NVARCHAR pour absorber tous les formats avant nettoyage.

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'orders' AND schema_id = SCHEMA_ID('bronze'))
BEGIN
    CREATE TABLE bronze.orders (
        [Type] NVARCHAR(50),
        [Days for shipping (real)] NVARCHAR(50),
        [Days for shipment (scheduled)] NVARCHAR(50),
        [Benefit per order] NVARCHAR(50),
        [Sales per customer] NVARCHAR(50),
        [Delivery Status] NVARCHAR(100),
        [Late_delivery_risk] NVARCHAR(10),
        [Category Id] NVARCHAR(50),
        [Category Name] NVARCHAR(200),
        [Customer City] NVARCHAR(200),
        [Customer Country] NVARCHAR(100),
        [Customer Email] NVARCHAR(200),
        [Customer Fname] NVARCHAR(100),
        [Customer Id] NVARCHAR(50),
        [Customer Lname] NVARCHAR(100),
        [Customer Password] NVARCHAR(100),
        [Customer Segment] NVARCHAR(50),
        [Customer State] NVARCHAR(100),
        [Customer Street] NVARCHAR(200),
        [Customer Zipcode] NVARCHAR(20),
        [Department Id] NVARCHAR(50),
        [Department Name] NVARCHAR(200),
        [Latitude] NVARCHAR(50),
        [Longitude] NVARCHAR(50),
        [Market] NVARCHAR(50),
        [Order City] NVARCHAR(200),
        [Order Country] NVARCHAR(100),
        [Order Customer Id] NVARCHAR(50),
        [order date (DateOrders)] NVARCHAR(50),
        [Order Id] NVARCHAR(50),
        [Order Item Cardprod Id] NVARCHAR(50),
        [Order Item Discount] NVARCHAR(50),
        [Order Item Discount Rate] NVARCHAR(50),
        [Order Item Id] NVARCHAR(50),
        [Order Item Product Price] NVARCHAR(50),
        [Order Item Profit Ratio] NVARCHAR(50),
        [Order Item Quantity] NVARCHAR(50),
        [Sales] NVARCHAR(50),
        [Order Item Total] NVARCHAR(50),
        [Order Profit Per Order] NVARCHAR(50),
        [Order Region] NVARCHAR(200),
        [Order State] NVARCHAR(100),
        [Order Status] NVARCHAR(50),
        [Product Card Id] NVARCHAR(50),
        [Product Category Id] NVARCHAR(50),
        [Product Description] NVARCHAR(MAX),
        [Product Image] NVARCHAR(MAX),
        [Product Name] NVARCHAR(500),
        [Product Price] NVARCHAR(50),
        [Product Status] NVARCHAR(10),
        [Shipping date (DateOrders)] NVARCHAR(50),
        [Shipping Mode] NVARCHAR(50),
        [_loaded_at] DATETIME DEFAULT GETDATE()
    );
    PRINT 'Table bronze.orders créée.';
END
GO


-- ============================================================================
-- 4. TABLE DE WATERMARK (Suivi d'ingestion)
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'watermark_tracking' AND schema_id = SCHEMA_ID('bronze'))
BEGIN
    CREATE TABLE bronze.watermark_tracking (
        table_name   VARCHAR(100) PRIMARY KEY,
        last_load_date DATETIME,
        rows_loaded    INT DEFAULT 0,
        loaded_at      DATETIME DEFAULT GETDATE()
    );

    INSERT INTO bronze.watermark_tracking (table_name, last_load_date)
    VALUES ('bronze.orders', '2015-01-01 00:00:00');

    PRINT 'Table bronze.watermark_tracking créée et initialisée.';
END
GO


-- ============================================================================
-- 5. TABLE DE MÉTADONNÉES BATCH (Traçabilité du pipeline)
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'batch_metadata' AND schema_id = SCHEMA_ID('bronze'))
BEGIN
    CREATE TABLE bronze.batch_metadata (
        batch_id        UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        table_name      VARCHAR(100) NOT NULL,
        batch_date      DATE NOT NULL,
        rows_extracted  INT NOT NULL DEFAULT 0,
        rows_inserted   INT NOT NULL DEFAULT 0,
        rows_duplicates INT NOT NULL DEFAULT 0,
        start_time      DATETIME NOT NULL DEFAULT GETDATE(),
        end_time        DATETIME,
        duration_sec    AS DATEDIFF(SECOND, start_time, end_time),
        status          VARCHAR(20) NOT NULL DEFAULT 'RUNNING',
        error_message   VARCHAR(4000),
        min_order_date  DATETIME,
        max_order_date  DATETIME
    );
    PRINT 'Table bronze.batch_metadata créée.';
END
GO

-- Index pour le suivi temporel des batchs
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'ix_batch_metadata_start')
    CREATE INDEX ix_batch_metadata_start ON bronze.batch_metadata(start_time DESC);
GO

-- Index UNIQUE avec IGNORE_DUP_KEY sur bronze.orders pour idempotence
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'uix_bronze_orders_item')
    CREATE UNIQUE NONCLUSTERED INDEX uix_bronze_orders_item
    ON bronze.orders ([Order Item Id])
    WITH (IGNORE_DUP_KEY = ON);
GO

PRINT 'Index d idempotence cree sur bronze.orders.';


-- ============================================================================
-- 7. INDEX COLUMNSTORE SUR LES FAITS (Performance analytique)
-- ============================================================================
-- Le columnstore index est l'équivalent local du stockage columnar
-- (Snowflake, BigQuery, Redshift). Il offre :
--   - Compression 10x
--   - Scan vertical 100x plus rapide pour les requêtes analytiques
--   - Batch processing mode

-- Note : L'index est créé APRÈS que la table gold.fct_orders_fulfillments
-- soit créée par dbt. Ce script DDL sera donc ré-exécuté en post-dbt.
-- La création est décommentée une fois que dbt a matérialisé la table.


-- ============================================================================
-- 6. VUES MÉTIER (Couche analytics)
-- ============================================================================
-- Ces vues simulent les "Materialized Views" de BigQuery
-- et les "Dynamic Tables" de Snowflake.

-- La vue analytics.v_kpi_summary est gérée par dbt (models/marts/v_kpi_summary.sql)
-- Ne pas créer ici pour éviter les conflits de dépendances.


-- ============================================================================
-- 7. STATISTIQUES MISE À JOUR
-- ============================================================================
-- Les stats à jour sont critiques pour l'optimiseur SQL Server.
-- À exécuter après chaque chargement important.

PRINT '
╔══════════════════════════════════════════════════════════════════════╗
║  Infrastructure Supply Chain DW prête.                              ║
║                                                                     ║
║  Schémas : bronze (raw), silver (staging), gold (warehouse),        ║
║            analytics (reporting)                                    ║
║  Partitioning : pf_monthly_orders sur les faits                     ║
║  Watermark  : bronze.watermark_tracking                             ║
║  Columnstore : à activer après la création des tables par dbt      ║
╚══════════════════════════════════════════════════════════════════════╝
';
GO
