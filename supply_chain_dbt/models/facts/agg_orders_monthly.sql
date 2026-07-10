SELECT
   cast(format(o.order_date, 'yyyyMM') as int) as year_month,
   year(o.order_date) as year,
   month(o.order_date) as month,
   o.market,
   o.category_id,
   o.shipping_mode,
   o.customer_segment,

   count(distinct o.order_id) as total_orders,
   count(distinct o.customer_id) as total_customers,
   sum(o.quantity) as total_quantity,
   sum(o.sales_amount) as total_sales,
   sum(o.profit_amount) as total_profit,
   sum(o.discount_amount) as total_discount,

   sum(case when o.is_otif = 1 then 1 else 0 end) as otif_orders,
   sum(case when o.is_on_time = 1 then 1 else 0 end) as on_time_orders,
   sum(case when o.is_complete = 1 then 1 else 0 end) as complete_orders,
   sum(case when o.late_delivery_risk = 1 then 1 else 0 end) as late_orders,
   sum(case when o.profit_amount < 0 then 1 else 0 end) as loss_orders,

   avg(o.sales_amount) as avg_sales,
   avg(o.profit_amount) as avg_profit,
   avg(o.days_shipping_real) as avg_shipping_days,
   avg(o.days_shipping_scheduled) as avg_scheduled_days
FROM {{ ref('int_orders_enriched') }} o
GROUP BY
   cast(format(o.order_date, 'yyyyMM') as int),
   year(o.order_date), month(o.order_date),
   o.market, o.category_id, o.shipping_mode, o.customer_segment
