SELECT DISTINCT
   product_id,
   max(product_name) as product_name,
   max(category_id) as category_id,
   max(category_name) as category_name
FROM {{ ref('stg_orders') }}
group by product_id