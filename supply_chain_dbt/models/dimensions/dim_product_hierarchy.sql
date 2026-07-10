SELECT DISTINCT
   row_number() over (order by department_name, category_name, category_id) as hierarchy_id,
   category_id,
   category_name,
   department_name,
   concat(department_name, ' > ', category_name) as category_full_path
FROM {{ ref('stg_orders') }}
