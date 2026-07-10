WITH geo_ordered AS (
   SELECT
      geo_id,
      order_city,
      order_state,
      order_country,
      order_region,
      market,
      row_number() over (partition by order_city, order_country order by geo_id) as rn
   FROM {{ ref('dim_geography') }}
)
SELECT
   geo_id,
   order_city,
   order_state,
   order_country,
   order_region,
   market,
   case
      when order_state is not null and order_region is not null
           then concat(order_city, ' > ', order_state, ' > ', order_country, ' > ', order_region, ' > ', market)
      when order_state is not null
           then concat(order_city, ' > ', order_state, ' > ', order_country, ' > ', market)
      else concat(order_city, ' > ', order_country, ' > ', market)
   end as geo_full_path
FROM geo_ordered
WHERE rn = 1
