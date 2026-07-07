select 
    shipment_id,
    shipment_status,
    actual_delivery_date
from {{ ref('stg_shipments') }}
where shipment_status = 'delivered' and actual_delivery_date is null
