select 
    shipment_id, 
    shipment_date, 
    actual_delivery_date
from {{ ref('stg_shipments') }}
where actual_delivery_date < shipment_date
