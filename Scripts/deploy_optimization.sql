USE SupplyChain_DW;
GO

-- ============================================================================
-- 1. INDEX SUR LES FAITS (gold.fct_orders_fulfillments)
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'ix_fct_orders_order_date_key')
    CREATE NONCLUSTERED INDEX ix_fct_orders_order_date_key
    ON gold.fct_orders_fulfillments (order_date_key)
    INCLUDE (sales_amount, profit_amount, quantity, is_otif);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'ix_fct_orders_shipping_date_key')
    CREATE NONCLUSTERED INDEX ix_fct_orders_shipping_date_key
    ON gold.fct_orders_fulfillments (shipping_date_key)
    INCLUDE (days_shipping_real, days_shipping_scheduled);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'ix_fct_orders_product_id')
    CREATE NONCLUSTERED INDEX ix_fct_orders_product_id
    ON gold.fct_orders_fulfillments (product_id)
    INCLUDE (quantity, sales_amount, is_otif);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'ix_fct_orders_warehouse_id')
    CREATE NONCLUSTERED INDEX ix_fct_orders_warehouse_id
    ON gold.fct_orders_fulfillments (warehouse_id)
    INCLUDE (quantity, sales_amount);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'ix_fct_orders_carrier_id')
    CREATE NONCLUSTERED INDEX ix_fct_orders_carrier_id
    ON gold.fct_orders_fulfillments (carrier_id)
    INCLUDE (days_shipping_real, days_shipping_scheduled, is_otif);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'ix_fct_orders_geo_id')
    CREATE NONCLUSTERED INDEX ix_fct_orders_geo_id
    ON gold.fct_orders_fulfillments (geo_id)
    INCLUDE (sales_amount, quantity, is_otif);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'ix_fct_orders_is_otif')
    CREATE NONCLUSTERED INDEX ix_fct_orders_is_otif
    ON gold.fct_orders_fulfillments (is_otif)
    INCLUDE (order_id, product_id, warehouse_id, sales_amount);
GO

-- ============================================================================
-- 2. INDEX SUR fct_inventory_levels
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'ix_fct_inventory_date_key')
    CREATE NONCLUSTERED INDEX ix_fct_inventory_date_key
    ON gold.fct_inventory_levels (date_key)
    INCLUDE (total_quantity_sold, cumulative_units_dispatched);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'ix_fct_inventory_product_id')
    CREATE NONCLUSTERED INDEX ix_fct_inventory_product_id
    ON gold.fct_inventory_levels (product_id)
    INCLUDE (warehouse_id, total_quantity_sold);
GO

-- ============================================================================
-- 3. INDEX SUR bronze.orders (Pipeline Watermark)
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'ix_bronze_orders_order_date')
    CREATE NONCLUSTERED INDEX ix_bronze_orders_order_date
    ON bronze.orders ([order date (DateOrders)])
    INCLUDE ([Order Id], [Order Item Id], [Shipping date (DateOrders)]);
GO

-- ============================================================================
-- 4. REBUILD INDEX FRAGMENTÉ
-- ============================================================================
ALTER INDEX uix_bronze_orders_item ON bronze.orders REBUILD;
GO

-- ============================================================================
-- 5. INDEX SECONDAIRES SUR LES DIMENSIONS
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'ix_dim_products_category')
    CREATE NONCLUSTERED INDEX ix_dim_products_category
    ON gold.dim_products (category_id, category_name)
    INCLUDE (product_name);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'ix_dim_geography_country_region')
    CREATE NONCLUSTERED INDEX ix_dim_geography_country_region
    ON gold.dim_geography (order_country, order_region)
    INCLUDE (order_city, market);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'ix_dim_geography_market')
    CREATE NONCLUSTERED INDEX ix_dim_geography_market
    ON gold.dim_geography (market)
    INCLUDE (order_country, order_region);
GO

-- ============================================================================
-- 6. PROCÉDURE STOCKÉE DE MAINTENANCE
-- ============================================================================
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_maintenance_weekly')
    DROP PROCEDURE gold.sp_maintenance_weekly;
GO

CREATE PROCEDURE gold.sp_maintenance_weekly
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @start DATETIME = GETDATE();
    PRINT '=== MAINTENANCE HEBDOMADAIRE ===';
    PRINT 'Debut: ' + CAST(@start AS VARCHAR(30));

    -- 6a. Mise à jour des statistiques
    UPDATE STATISTICS bronze.orders;
    UPDATE STATISTICS gold.fct_orders_fulfillments;
    UPDATE STATISTICS gold.fct_inventory_levels;
    UPDATE STATISTICS gold.dim_geography;
    UPDATE STATISTICS gold.dim_products;
    UPDATE STATISTICS gold.dim_date;
    UPDATE STATISTICS gold.dim_warehouses;
    UPDATE STATISTICS gold.dim_carriers;
    PRINT 'Statistiques mises a jour.';

    -- 6b. Rebuild indexes avec fragmentation > 30%
    DECLARE @sql NVARCHAR(500);
    DECLARE idx_cursor CURSOR FOR
        SELECT 'ALTER INDEX [' + i.name + '] ON [' + s.name + '].[' + t.name + '] REBUILD;'
        FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ips
        JOIN sys.indexes i ON ips.object_id = i.object_id AND ips.index_id = i.index_id
        JOIN sys.tables t ON i.object_id = t.object_id
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        WHERE ips.avg_fragmentation_in_percent > 30
          AND i.name IS NOT NULL;
    OPEN idx_cursor;
    FETCH NEXT FROM idx_cursor INTO @sql;
    WHILE @@FETCH_STATUS = 0
    BEGIN
        EXEC sp_executesql @sql;
        PRINT 'Rebuild: ' + @sql;
        FETCH NEXT FROM idx_cursor INTO @sql;
    END
    CLOSE idx_cursor;
    DEALLOCATE idx_cursor;

    -- 6c. Nettoyage des métadonnées batch (conserver 90 jours)
    DELETE FROM bronze.batch_metadata
    WHERE start_time < DATEADD(DAY, -90, GETDATE())
      AND status = 'COMPLETED';
    PRINT 'Nettoyage batch_metadata: OK';

    DECLARE @end DATETIME = GETDATE();
    DECLARE @dur INT = DATEDIFF(SECOND, @start, @end);
    PRINT CONCAT('Maintenance terminee en ', @dur, 's.');
END;
GO

-- ============================================================================
-- 7. MISE À JOUR INITIALE DES STATISTIQUES
-- ============================================================================
UPDATE STATISTICS gold.fct_orders_fulfillments;
UPDATE STATISTICS gold.fct_inventory_levels;
UPDATE STATISTICS gold.dim_geography;
UPDATE STATISTICS gold.dim_products;
UPDATE STATISTICS gold.dim_date;
UPDATE STATISTICS gold.dim_warehouses;
UPDATE STATISTICS gold.dim_carriers;
UPDATE STATISTICS bronze.orders;
GO

PRINT '=== Optimisation terminee ===';
GO
