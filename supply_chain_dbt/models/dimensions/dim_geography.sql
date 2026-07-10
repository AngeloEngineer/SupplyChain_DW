SELECT
   row_number() over (order by order_country, order_city, order_state, order_region, market) as geo_id,
   order_city,
   order_state,
   order_country,
   order_region,
   market
FROM (select distinct order_city, order_state, order_country, order_region, market from {{ ref('stg_orders') }}) distinct_geo