/*
  advanced_queries.sql — SQL Avancé (Phase 7)

  Démonstration de :
    1. CTE Récursif (hiérarchie géographique)
    2. Fenêtrage (cumuls, moyennes mobiles, LAG)
    3. Pivot dynamique (marchés en colonnes)
    4. Rang et percentile (classement des catégories)
*/

-- ============================================================================
-- 1. CTE RÉCURSIF : Hiérarchie géographique descendante
-- ============================================================================
WITH geo_tree AS (
   -- Niveau racine : marchés
   SELECT DISTINCT market, cast(market as varchar(500)) as path, 1 as level
   FROM gold.dim_geography WHERE market IS NOT NULL
   UNION ALL
   -- Niveau région
   SELECT DISTINCT g.market,
          cast(concat(gt.path, ' > ', g.order_region) as varchar(500)),
          gt.level + 1
   FROM gold.dim_geography g
   JOIN geo_tree gt ON g.market = gt.market AND g.order_region IS NOT NULL
   WHERE gt.level = 1
   UNION ALL
   -- Niveau pays
   SELECT DISTINCT g.market,
          cast(concat(gt.path, ' > ', g.order_country) as varchar(500)),
          gt.level + 1
   FROM gold.dim_geography g
   JOIN geo_tree gt ON g.market = gt.market
   WHERE gt.level = 2 AND g.order_country IS NOT NULL
)
SELECT * FROM geo_tree ORDER BY path;

-- ============================================================================
-- 2. FENÊTRAGE : Analyse OTIF avec cumuls et comparaisons
-- ============================================================================
WITH monthly AS (
   SELECT
      year_month,
      year,
      month,
      market,
      sum(total_orders) as orders,
      sum(otif_orders) as otif,
      sum(total_sales) as sales,
      sum(total_profit) as profit
   FROM gold.agg_orders_monthly
   WHERE market IS NOT NULL
   GROUP BY year_month, year, month, market
)
SELECT
   year_month,
   market,
   orders,
   otif,
   cast(otif as float) / nullif(orders, 0) * 100 as otif_pct,

   -- Cumul annuel
   sum(orders) over (partition by year, market order by month) as orders_ytd,

   -- Moyenne mobile 3 mois de l'OTIF
   avg(cast(otif as float) / nullif(orders, 0)) over (
      partition by market order by year_month rows between 2 preceding and current row
   ) as otif_ma_3m,

   -- Évolution vs mois précédent
   lag(orders) over (partition by market order by year_month) as prev_orders,
   (orders - lag(orders) over (partition by market order by year_month))
      / nullif(lag(orders) over (partition by market order by year_month), 0) * 100 as orders_mom_change,

   -- Classement du marché par ventes
   row_number() over (partition by year_month order by sales desc) as market_rank_sales

FROM monthly
ORDER BY year_month, market_rank_sales;

-- ============================================================================
-- 3. PERCENTILE : Distribution des délais de livraison
-- ============================================================================
SELECT distinct
   percentile_cont(0.25) within group (order by days_shipping_real)
      over (partition by market) as p25_days,
   percentile_cont(0.50) within group (order by days_shipping_real)
      over (partition by market) as median_days,
   percentile_cont(0.75) within group (order by days_shipping_real)
      over (partition by market) as p75_days,
   percentile_cont(0.90) within group (order by days_shipping_real)
      over (partition by market) as p90_days,
   market
FROM silver.stg_orders
WHERE market IS NOT NULL;
