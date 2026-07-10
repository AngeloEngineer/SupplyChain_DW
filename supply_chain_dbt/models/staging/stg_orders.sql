/*
================================================================================
  stg_orders.sql — Couche Silver (Staging)

  Objectif :
    Nettoyer, typer et normaliser les données brutes de bronze.orders.

  Règles de nettoyage appliquées :
    1. Exclusions :
       - Colonnes vides : Product Description (100% null), Order Zipcode (86% null)
       - Redondances (r=1.0) : Order Profit Per Order, Order Item Total,
         Product Category Id, Order Customer Id, Order Item Cardprod Id,
         Product Price, Sales per customer
       - PII : Customer Email, Customer Password, Customer Street,
         Customer Fname, Customer Lname, Product Image
     2. Typage fort : try_cast / try_convert pour échecs silencieux au lieu d'erreurs
    3. Normalisation : trim() sur toutes les chaînes
    4. Filtre métier : shipping_date >= order_date (anomalies isolées dans anomalies_orders)

  Source : {{ source('supply_chain_raw', 'orders') }} (bronze.orders)
  Destination : silver.stg_orders
================================================================================
*/

SELECT
   -- Identifiants
   try_cast([Order Id] as int) as order_id,
   try_cast([Order Item Id] as int) as order_item_id,
   try_cast([Customer Id] as int) as customer_id,
   try_cast([Product Card Id] as int) as product_id,
   try_cast([Department Id] as int) as departement_id,

   -- Dates (try_convert avec style 120 = ODBC canonical, neutre vis-à-vis DATEFORMAT)
   try_convert(datetime, [order date (DateOrders)], 120) as order_date,
   try_convert(datetime, [Shipping date (DateOrders)], 120) as shipping_date,

   -- Métriques logistiques
   try_cast([Days for shipping (real)] as int) as days_shipping_real,
   try_cast([Days for shipment (scheduled)] as int) as days_shipping_scheduled,

   -- Statuts (normalisés)
   ltrim(rtrim([Order Status])) as order_status,
   ltrim(rtrim([Delivery Status])) as delivery_status,
   ltrim(rtrim([Shipping Mode])) as shipping_mode,
   try_cast([Late_delivery_risk] as bit) as late_delivery_risk,

   -- Métriques financières
   try_cast([Order Item Quantity] as int) as quantity,
   try_cast([Sales] as decimal(18,2)) as sales_amount,
   try_cast([Benefit per order] as decimal(18,2)) as profit_amount,
   try_cast([Order Item Discount] as decimal(18,2)) as discount_amount,
   try_cast([Order Item Discount Rate] as decimal(5,4)) as discount_rate,
   try_cast([Order Item Profit Ratio] as decimal(5,2)) as profit_ratio,

   -- Produit
   ltrim(rtrim([Product Name])) as product_name,
   try_cast([Category Id] as int) as category_id,
   ltrim(rtrim([Category Name])) as category_name,
   ltrim(rtrim([Department Name])) as department_name,
   try_cast([Product Status] as bit) as product_status,

   -- Géographie (commande)
   ltrim(rtrim([Order City])) as order_city,
   ltrim(rtrim([Order State])) as order_state,
   ltrim(rtrim([Order Country])) as order_country,
   ltrim(rtrim([Order Region])) as order_region,
   ltrim(rtrim([Market])) as market,

   -- Géographie (client)
   ltrim(rtrim([Customer City])) as customer_city,
   ltrim(rtrim([Customer State])) as customer_state,
   ltrim(rtrim([Customer Country])) as customer_country,
   try_cast([Customer Zipcode] as int) as customer_zipcode,

   -- Géolocalisation
   try_cast([Latitude] as decimal(9,6)) as latitude,
   try_cast([Longitude] as decimal(9,6)) as longitude,

   -- Segmentation
   ltrim(rtrim([Customer Segment])) as customer_segment,
   ltrim(rtrim([Type])) as transaction_type

FROM {{ source('supply_chain_raw', 'orders') }}
WHERE try_convert(datetime, [Shipping date (DateOrders)], 120) >= try_convert(datetime, [order date (DateOrders)], 120)