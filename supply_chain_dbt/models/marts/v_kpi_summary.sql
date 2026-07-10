SELECT
    d.year,
    d.month,
    d.month_name,
    d.quarter,
    d.year_quarter,

    count(distinct o.order_id) as total_orders,
    count(distinct o.order_item_id) as total_order_lines,
    count(distinct o.customer_id) as total_customers,
    sum(o.quantity) as total_units_sold,
    sum(o.sales_amount) as total_sales,
    sum(o.profit_amount) as total_profit,
    sum(o.discount_amount) as total_discounts,

    avg(cast(o.is_otif as float)) * 100 as otif_rate,
    avg(cast(o.is_on_time as float)) * 100 as on_time_rate,
    avg(cast(o.is_complete as float)) * 100 as in_full_rate,

    avg(cast(o.days_shipping_real as float)) as avg_delivery_days,
    avg(cast(o.days_shipping_scheduled as float)) as avg_scheduled_days,
    avg(cast(o.days_shipping_real - o.days_shipping_scheduled as float)) as avg_delay_days,
    avg(cast(o.processing_days as float)) as avg_processing_days,

    sum(o.sales_amount) / nullif(count(distinct o.order_id), 0) as avg_order_value,
    sum(o.profit_amount) / nullif(sum(o.sales_amount), 0) * 100 as profit_margin_pct,

    avg(o.sales_amount) as avg_sales_per_line,
    avg(o.quantity) as avg_units_per_order,
    count(distinct o.product_id) as distinct_products_sold,

    sum(case when o.profit_amount < 0 then 1 else 0 end) as loss_orders,
    cast(sum(case when o.profit_amount < 0 then 1 else 0 end) as float)
        / nullif(count(*), 0) * 100 as loss_rate_pct

FROM {{ ref('fct_orders_fulfillments') }} o
JOIN {{ ref('dim_date') }} d ON o.order_date_key = d.date_key
GROUP BY d.year, d.month, d.month_name, d.quarter, d.year_quarter
