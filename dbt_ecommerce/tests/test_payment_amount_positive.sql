select 
    payment_id, 
    payment_amount
from {{ ref('stg_payments') }}
where payment_status = 'success' and payment_amount <= 0
