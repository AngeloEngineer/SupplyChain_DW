/*
  deploy_database.sql — Déploiement complet de la base SupplyChain_DW

  Usage :
    1. Ouvrir SSMS et se connecter au serveur local
    2. Exécuter ce script en étant connecté à la base master
    3. Le script crée la base, les schémas, les tables et les index

  Compatible : SQL Server 2016+
*/

-- ============================================================================
-- 0. CRÉATION DE LA BASE
-- ============================================================================
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'SupplyChain_DW')
BEGIN
    CREATE DATABASE SupplyChain_DW;
    PRINT 'Base SupplyChain_DW créée.';
END
GO

USE SupplyChain_DW;
GO

-- ============================================================================
-- 1. SCHÉMAS (Medallion Architecture)
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'bronze')
    EXEC('CREATE SCHEMA bronze');
GO
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'silver')
    EXEC('CREATE SCHEMA silver');
GO
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'gold')
    EXEC('CREATE SCHEMA gold');
GO
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'analytics')
    EXEC('CREATE SCHEMA analytics');
GO

PRINT 'Schémas bronze/silver/gold/analytics prêts.';

-- ============================================================================
-- 2. TABLE BRONZE.ORDERS (Landing — données brutes miroir du CSV)
-- ============================================================================
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

-- Index UNIQUE avec IGNORE_DUP_KEY pour idempotence du pipeline
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'uix_bronze_orders_item')
    CREATE UNIQUE NONCLUSTERED INDEX uix_bronze_orders_item
    ON bronze.orders ([Order Item Id])
    WITH (IGNORE_DUP_KEY = ON);
GO
PRINT 'Index idempotence créé sur bronze.orders.';

-- ============================================================================
-- 3. TABLE DE WATERMARK
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'watermark_tracking' AND schema_id = SCHEMA_ID('bronze'))
BEGIN
    CREATE TABLE bronze.watermark_tracking (
        table_name      VARCHAR(100) PRIMARY KEY,
        last_load_date  DATETIME,
        rows_loaded     INT DEFAULT 0,
        loaded_at       DATETIME DEFAULT GETDATE()
    );
    INSERT INTO bronze.watermark_tracking (table_name, last_load_date)
    VALUES ('bronze.orders', '2015-01-01 00:00:00');
    PRINT 'Table bronze.watermark_tracking créée et initialisée.';
END
GO

-- ============================================================================
-- 4. TABLE DE MÉTADONNÉES BATCH
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'batch_metadata' AND schema_id = SCHEMA_ID('bronze'))
BEGIN
    CREATE TABLE bronze.batch_metadata (
        batch_id        UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
        table_name      VARCHAR(100) NOT NULL,
        batch_date      DATE,
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
    CREATE INDEX ix_batch_metadata_start ON bronze.batch_metadata(start_time DESC);
    PRINT 'Table bronze.batch_metadata créée.';
END
GO

-- ============================================================================
-- 5. PARTITIONNEMENT (Mensuel pour la table de faits)
-- ============================================================================
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
    CREATE PARTITION SCHEME ps_monthly_orders
    AS PARTITION pf_monthly_orders ALL TO ([PRIMARY]);
    PRINT 'Partitionnement mensuel créé.';
END
GO

PRINT '
=== Déploiement terminé ===
';
GO
