with daily_sales as (
    select
       cast(format(order_date, 'yyyyMMdd') as int) as date_key,
       product_id,
       departement_id as warehouse_id,
       sum(quantity) as total_quantity_sold,
       count(distinct order_id) as total_orders,
       sum(sales_amount) as total_sales_amount
    from {{ ref('stg_orders') }}
    group by
      cast(format(order_date, 'yyyyMMdd') as int),
      product_id,
      departement_id
)
select
   date_key,
   product_id,
   warehouse_id,
   total_quantity_sold,
   total_orders,
   total_sales_amount,
   sum(total_quantity_sold) over (
    partition by product_id, warehouse_id
    order by date_key
    rows between unbounded preceding and current row
   ) as cumulative_units_dispatched,
   avg(total_quantity_sold) over (
    partition by product_id, warehouse_id
    order by date_key
    rows between 6 preceding and current row
   ) as rolling_7day_avg_sold
from daily_sales