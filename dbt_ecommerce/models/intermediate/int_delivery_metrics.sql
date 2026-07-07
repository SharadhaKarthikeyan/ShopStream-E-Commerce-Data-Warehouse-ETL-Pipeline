with shipments as (
    select * from {{ ref('stg_shipments') }}
)

select
    shipment_id,
    order_id,
    shipment_date,
    expected_delivery_date,
    actual_delivery_date,
    shipping_provider,
    shipment_status,
    case 
        when actual_delivery_date is not null then (actual_delivery_date - shipment_date)
        else null
    end as delivery_duration_days,
    case 
        when actual_delivery_date > expected_delivery_date then 1 
        else 0 
    end as is_delayed
from shipments
