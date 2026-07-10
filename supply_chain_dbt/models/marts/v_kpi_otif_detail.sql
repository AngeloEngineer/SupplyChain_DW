WITH monthly_otif AS (
   SELECT
      year(o.order_date) as year,
      month(o.order_date) as month,
      datename(month, o.order_date) as month_name,
      o.market,
      o.shipping_mode,
      o.customer_segment,

      count(*) as total_orders,
      sum(case when o.is_otif = 1 then 1 else 0 end) as otif_orders,
      sum(case when o.is_on_time = 1 then 1 else 0 end) as on_time_orders,
      sum(case when o.is_complete = 1 then 1 else 0 end) as complete_orders,
      sum(case when o.late_delivery_risk = 1 then 1 else 0 end) as late_risk_orders,
      sum(case when o.delivery_status = 'Late delivery' then 1 else 0 end) as late_deliveries,
      sum(case when o.delivery_status = 'Shipping canceled' then 1 else 0 end) as canceled_deliveries,

      avg(o.days_shipping_real) as avg_shipping_days,
      avg(o.days_shipping_scheduled) as avg_scheduled_days
   FROM {{ ref('int_orders_enriched') }} o
   GROUP BY year(o.order_date), month(o.order_date), datename(month, o.order_date),
            o.market, o.shipping_mode, o.customer_segment
)
SELECT
   year, month, month_name,
   market, shipping_mode, customer_segment,
   total_orders,
   otif_orders, on_time_orders, complete_orders,
   late_risk_orders, late_deliveries, canceled_deliveries,

   cast(otif_orders as float) / nullif(total_orders, 0) * 100 as otif_rate,
   cast(on_time_orders as float) / nullif(total_orders, 0) * 100 as on_time_rate,
   cast(complete_orders as float) / nullif(total_orders, 0) * 100 as in_full_rate,
   cast(late_deliveries as float) / nullif(total_orders, 0) * 100 as late_delivery_rate,
   cast(canceled_deliveries as float) / nullif(total_orders, 0) * 100 as cancel_rate,

   avg_shipping_days, avg_scheduled_days,
   avg_shipping_days - avg_scheduled_days as avg_delay_days
FROM monthly_otif
