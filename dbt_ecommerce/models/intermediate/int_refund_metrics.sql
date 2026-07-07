with refunds as (
    select * from {{ ref('stg_refunds') }}
)

select
    order_id,
    count(refund_id) as total_refund_claims,
    sum(case when refund_status = 'processed' then refund_amount else 0 end) as total_refunded_amount,
    count(case when refund_status = 'processed' then 1 end) as processed_refund_count
from refunds
group by order_id
