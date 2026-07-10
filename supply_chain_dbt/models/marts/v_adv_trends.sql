WITH monthly_agg AS (
   SELECT
      year_month,
      year,
      month,
      market,
      sum(total_sales) as sales,
      sum(total_orders) as orders,
      sum(total_profit) as profit,
      sum(otif_orders) as otif
   FROM {{ ref('agg_orders_monthly') }}
   WHERE market IS NOT NULL
   GROUP BY year_month, year, month, market
)
SELECT
   m.year_month,
   m.year,
   m.month,
   concat(m.year, '-', right(concat('0', m.month), 2)) as year_month_label,
   m.market,
   m.sales,
   m.orders,
   m.profit,

   sum(m.sales) over (partition by m.year, m.market order by m.month) as running_sales_ytd,

   avg(m.sales) over (partition by m.market order by m.year_month rows between 2 preceding and current row) as sales_ma_3m,

   lag(m.sales) over (partition by m.market order by m.year_month) as prev_month_sales,
   case when lag(m.sales) over (partition by m.market order by m.year_month) > 0
        then (m.sales - lag(m.sales) over (partition by m.market order by m.year_month))
             / nullif(lag(m.sales) over (partition by m.market order by m.year_month), 0) * 100
        else null
   end as sales_mom_pct,

   lag(m.sales, 12) over (partition by m.market order by m.year_month) as sales_prev_year_same_month,
   case when lag(m.sales, 12) over (partition by m.market order by m.year_month) > 0
        then (m.sales - lag(m.sales, 12) over (partition by m.market order by m.year_month))
             / nullif(lag(m.sales, 12) over (partition by m.market order by m.year_month), 0) * 100
        else null
   end as sales_yoy_pct,

   case when m.orders > 0
        then cast(m.otif as float) / m.orders * 100
        else null
   end as otif_rate,

   row_number() over (partition by m.year_month order by m.sales desc) as market_rank
FROM monthly_agg m
-- ORDER BY n'est pas autorisé dans les vues SQL Server
