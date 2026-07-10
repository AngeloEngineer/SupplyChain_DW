{% snapshot orders_status_snapshot %}

{{
    config(
        target_database='SupplyChain_DW',
        target_schema='silver',
        unique_key='order_item_id',
        strategy='check',
        check_cols=['order_status', 'delivery_status'],
        invalidate_hard_deletes=True
    )
}}

SELECT
   cast([Order Item Id] as int) as order_item_id,
   cast([Order Id] as int) as order_id,
   [Order Status] as order_status,
   [Delivery Status] as delivery_status,
   getdate() as updated_at
FROM {{ source('supply_chain_raw', 'orders') }}

{% endsnapshot %}