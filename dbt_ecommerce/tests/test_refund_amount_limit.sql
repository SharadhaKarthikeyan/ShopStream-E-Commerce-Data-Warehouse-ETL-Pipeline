select 
    r.refund_id, 
    r.refund_amount, 
    o.net_revenue
from {{ ref('stg_refunds') }} r
join {{ ref('int_order_revenue') }} o on r.order_id = o.order_id
where r.refund_status = 'processed' and r.refund_amount > o.net_revenue
