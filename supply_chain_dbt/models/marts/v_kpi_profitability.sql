WITH profit_data AS (
   SELECT
      year(o.order_date) as year,
      month(o.order_date) as month,
      o.market,
      o.category_name,
      o.customer_segment,
      o.shipping_mode,

      count(*) as total_orders,
      sum(o.sales_amount) as total_sales,
      sum(o.profit_amount) as total_profit,
      sum(o.discount_amount) as total_discount,
      sum(o.quantity) as total_quantity,

      sum(case when o.profit_amount < 0 then 1 else 0 end) as loss_orders,
      sum(case when o.profit_amount < 0 then o.profit_amount else 0 end) as loss_amount,
      sum(case when o.profit_amount >= 0 then o.profit_amount else 0 end) as gain_amount,

      sum(case when o.discount_amount > 0 then 1 else 0 end) as discounted_orders,
      sum(case when o.transaction_type = 'DEBIT' then 1 else 0 end) as debit_orders,
      sum(case when o.transaction_type = 'TRANSFER' then 1 else 0 end) as transfer_orders
   FROM {{ ref('int_orders_enriched') }} o
   GROUP BY year(o.order_date), month(o.order_date),
            o.market, o.category_name, o.customer_segment, o.shipping_mode
)
SELECT
   year, month,
   market, category_name, customer_segment, shipping_mode,

   total_orders, total_sales, total_profit, total_discount, total_quantity,

   loss_orders, discounted_orders, debit_orders, transfer_orders,
   loss_amount, gain_amount,

   cast(total_profit as float) / nullif(total_sales, 0) * 100 as profit_margin_pct,
   cast(loss_orders as float) / nullif(total_orders, 0) * 100 as loss_rate_pct,
   cast(discounted_orders as float) / nullif(total_orders, 0) * 100 as discount_rate_pct,
   total_profit / nullif(total_quantity, 0) as profit_per_unit,
   total_sales / nullif(total_orders, 0) as avg_order_value
FROM profit_data
