SELECT
   cast(format(o.order_date, 'yyyyMMdd') as int) as date_key,
   o.product_id,
   o.departement_id as warehouse_id,
   o.category_id,
   o.market,
   o.shipping_mode,
   o.customer_segment,

   count(distinct o.order_id) as total_orders,
   count(distinct o.customer_id) as total_customers,
   sum(o.quantity) as total_quantity,
   sum(o.sales_amount) as total_sales,
   sum(o.profit_amount) as total_profit,
   sum(o.discount_amount) as total_discount,
   avg(o.sales_amount) as avg_sales_per_order,
   sum(case when o.is_otif = 1 then 1 else 0 end) as otif_orders,
   sum(case when o.is_on_time = 1 then 1 else 0 end) as on_time_orders,
   sum(case when o.is_complete = 1 then 1 else 0 end) as complete_orders,
   sum(case when o.late_delivery_risk = 1 then 1 else 0 end) as late_delivery_orders,
   sum(case when o.profit_amount < 0 then 1 else 0 end) as loss_orders,
   sum(case when o.discount_amount > 0 then 1 else 0 end) as discounted_orders,
   count(distinct o.product_id) as distinct_products,
   avg(o.days_shipping_real) as avg_shipping_days_real,
   avg(o.days_shipping_scheduled) as avg_shipping_days_scheduled
FROM {{ ref('int_orders_enriched') }} o
GROUP BY
   cast(format(o.order_date, 'yyyyMMdd') as int),
   o.product_id, o.departement_id, o.category_id,
   o.market, o.shipping_mode, o.customer_segment
