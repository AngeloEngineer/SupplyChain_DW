SELECT DISTINCT
   departement_id as warehouse_id,
   max(department_name) as warehouse_name
FROM {{ ref('stg_orders') }}
group by departement_id