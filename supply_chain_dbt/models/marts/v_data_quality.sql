/*
  v_data_quality.sql — Tableau de bord qualité des données

  Objectif :
    Monitorer le pipeline de nettoyage et fournir des métriques de qualité
    à chaque étape du processing.

  Métriques :
    - Total brut vs nettoyé
    - Taux d'anomalies rejetées
    - Valeurs manquantes par colonne clé
    - Distribution des status
    - Alertes qualité
*/

with bronze_stats as (
    select
        count(*) as total_raw_rows,
        count(case when try_cast([Order Id] as int) is null then 1 end) as null_order_ids,
        count(case when try_cast([Order Item Id] as int) is null then 1 end) as null_order_item_ids,
        count(case when try_cast([Shipping date (DateOrders)] as datetime) < try_cast([order date (DateOrders)] as datetime) then 1 end) as shipping_anomalies,
        min(try_cast([order date (DateOrders)] as datetime)) as min_order_date,
        max(try_cast([order date (DateOrders)] as datetime)) as max_order_date
    from {{ source('supply_chain_raw', 'orders') }}
),

silver_stats as (
    select
        count(*) as total_clean_rows,
        count(case when order_date is null then 1 end) as null_order_dates,
        count(case when shipping_date is null then 1 end) as null_shipping_dates,
        count(case when sales_amount is null then 1 end) as null_sales,
        count(case when profit_amount is null then 1 end) as null_profits,
        count(case when customer_id is null then 1 end) as null_customers
    from {{ ref('stg_orders') }}
),

anomaly_stats as (
    select count(*) as total_anomalies
    from {{ ref('anomalies_orders') }}
)

select
    bs.total_raw_rows,
    sil.total_clean_rows,
    anom.total_anomalies,
    bs.total_raw_rows - sil.total_clean_rows as rows_removed,
    round(100.0 * (bs.total_raw_rows - sil.total_clean_rows) / nullif(bs.total_raw_rows, 0), 2) as pct_removed,
    round(100.0 * anom.total_anomalies / nullif(bs.total_raw_rows, 0), 2) as pct_anomalies,
    sil.null_order_dates,
    sil.null_shipping_dates,
    sil.null_sales,
    sil.null_profits,
    sil.null_customers,
    bs.min_order_date,
    bs.max_order_date
from bronze_stats bs
cross join silver_stats sil
cross join anomaly_stats anom