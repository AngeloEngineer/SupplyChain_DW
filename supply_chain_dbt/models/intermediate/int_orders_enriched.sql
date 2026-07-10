/*
================================================================================
  int_orders_enriched.sql — Couche Intermediate

  Objectif :
    Enrichir stg_orders avec des indicateurs calculés pour alimenter les faits.

  Colonnes ajoutées :
    - processing_days : délai entre commande et expédition
    - is_on_time : livraison réelle <= planifiée
    - is_complete : commande au statut COMPLETE
    - is_otif : is_on_time AND is_complete (indicateur Wal-Mart)
    - order_line_number : numéro de ligne dans la commande
    - total_lines_per_order : nombre total de lignes par commande
================================================================================
*/

SELECT
   o.order_id,
   o.order_item_id,
   o.customer_id,
   o.product_id,
   o.departement_id,
   o.order_date,
   o.shipping_date,
   o.days_shipping_real,
   o.days_shipping_scheduled,
   o.order_status,
   o.delivery_status,
   o.shipping_mode,
   o.late_delivery_risk,
   o.quantity,
   o.sales_amount,
   o.profit_amount,
   o.discount_amount,
   o.discount_rate,
   o.profit_ratio,
   o.product_name,
   o.category_id,
   o.category_name,
   o.department_name,
   o.product_status,
   o.order_city,
   o.order_state,
   o.order_country,
   o.order_region,
   o.market,
   o.customer_city,
   o.customer_state,
   o.customer_country,
   o.customer_zipcode,
   o.latitude,
   o.longitude,
   o.customer_segment,
   o.transaction_type,

   -- Indicateurs calculés
   datediff(day, o.order_date, o.shipping_date) as processing_days,
   case when o.days_shipping_real <= o.days_shipping_scheduled then 1 else 0 end as is_on_time,
   case when o.order_status = 'COMPLETE' then 1 else 0 end as is_complete,
   case
      when o.days_shipping_real <= o.days_shipping_scheduled
       and o.order_status = 'COMPLETE' then 1
      else 0
   end as is_otif,
   row_number() over (
      partition by o.order_id
      order by o.order_item_id
   ) as order_line_number,
   count(*) over (partition by o.order_id) as total_lines_per_order

FROM {{ ref('stg_orders') }} o