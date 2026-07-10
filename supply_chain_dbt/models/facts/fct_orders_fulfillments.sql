SELECT
   o.order_id,
   o.order_item_id,
   o.product_id,
   o.departement_id as warehouse_id,
   g.geo_id,
   c.carrier_id,
   cast(format(o.order_date, 'yyyyMMdd') as int) as order_date_key,
   cast(format(o.shipping_date, 'yyyyMMdd') as int) as shipping_date_key,
   o.days_shipping_real,
   o.days_shipping_scheduled,
   o.is_otif,
   o.is_on_time,
   o.is_complete,
   o.quantity,
   o.sales_amount,
   o.profit_amount,
   o.discount_amount,
   o.processing_days,
   o.total_lines_per_order,
   o.customer_id
FROM {{ ref('int_orders_enriched') }} o
left join {{ ref('dim_geography') }} g
  on o.order_city = g.order_city
  and o.order_country = g.order_country
  and isnull(o.order_state, '') = isnull(g.order_state, '')
  and isnull(o.order_region, '') = isnull(g.order_region, '')
  and o.market = g.market
left join {{ ref('dim_carriers') }} c
  on o.shipping_mode = c.carrier_name