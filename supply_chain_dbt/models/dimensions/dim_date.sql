WITH
  digits AS (SELECT n FROM (VALUES (0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) AS v(n)),
  numbers AS (
    SELECT a.n + 10*b.n + 100*c.n + 1000*d.n AS n
    FROM digits a
    CROSS JOIN digits b
    CROSS JOIN digits c
    CROSS JOIN digits d
    WHERE a.n + 10*b.n + 100*c.n + 1000*d.n <= datediff(day, '2015-01-01', '2020-12-31')
  ),
  dates AS (
    SELECT dateadd(day, n, '2015-01-01') AS dt FROM numbers
  )
SELECT
   cast(format(dt, 'yyyyMMdd') as int) as date_key,
   dt as date,
   year(dt) as year,
   month(dt) as month,
   datepart(quarter, dt) as quarter,
   datepart(week, dt) as week_of_year,
   datepart(dayofyear, dt) as day_of_year,
   datepart(weekday, dt) as day_of_week,
   datename(month, dt) as month_name,
   datename(weekday, dt) as weekday_name,
   cast(format(dt, 'yyyyMM') as int) as year_month,
   concat(year(dt), '-Q', datepart(quarter, dt)) as year_quarter,
   case when datepart(weekday, dt) in (1, 7) then 1 else 0 end as is_weekend,
   case when day(dt) = 1 then 1 else 0 end as is_month_start,
   case when day(dt) = day(eomonth(dt)) then 1 else 0 end as is_month_end,
   case when datepart(quarter, dt) = 1 then 1 else 0 end as is_q1,
   case when datepart(quarter, dt) = 2 then 1 else 0 end as is_q2,
   case when datepart(quarter, dt) = 3 then 1 else 0 end as is_q3,
   case when datepart(quarter, dt) = 4 then 1 else 0 end as is_q4
FROM dates
