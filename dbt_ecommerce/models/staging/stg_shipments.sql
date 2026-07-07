with source as (
    select * from {{ source('raw', 'shipments') }}
),

cleaned as (
    select
        trim(shipment_id) as shipment_id,
        trim(order_id) as order_id,
        shipment_date,
        expected_delivery_date,
        actual_delivery_date,
        trim(shipping_provider) as shipping_provider,
        trim(lower(shipment_status)) as shipment_status,
        row_number() over (
            partition by shipment_id 
            order by shipment_date desc
        ) as rn
    from source
)

select
    shipment_id,
    order_id,
    shipment_date,
    expected_delivery_date,
    actual_delivery_date,
    shipping_provider,
    shipment_status
from cleaned
where rn = 1
