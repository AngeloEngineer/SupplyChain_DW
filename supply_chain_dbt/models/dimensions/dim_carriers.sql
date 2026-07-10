SELECT
   row_number() over (order by shipping_mode) as carrier_id,
   shipping_mode as carrier_name
FROM (select distinct shipping_mode from {{ ref('stg_orders') }}) distinct_modes