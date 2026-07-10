SELECT
  [Order Id] as order_id,
  [Order Item Id] as order_item_id,
  try_convert(datetime, [order date (DateOrders)], 120) as order_date,
  try_convert(datetime, [Shipping date (DateOrders)], 120) as shipping_date,
  'Shipping date prior to Order date' as rejection_reason
FROM {{ source('supply_chain_raw', 'orders') }}
WHERE try_convert(datetime, [Shipping date (DateOrders)], 120) < try_convert(datetime, [order date (DateOrders)], 120)