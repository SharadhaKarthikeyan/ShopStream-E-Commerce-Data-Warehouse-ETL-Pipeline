with delivery_metrics as (
    select * from {{ ref('int_delivery_metrics') }}
),

orders as (
    select 
        order_id,
        customer_id,
        order_date
    from {{ ref('stg_orders') }}
)

select
    dm.shipment_id,
    dm.order_id,
    o.customer_id,
    o.order_date,
    dm.shipment_date,
    dm.expected_delivery_date,
    dm.actual_delivery_date,
    dm.shipping_provider,
    dm.shipment_status,
    dm.delivery_duration_days,
    dm.is_delayed
from delivery_metrics dm
join orders o on dm.order_id = o.order_id
