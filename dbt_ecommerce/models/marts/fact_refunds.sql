with refunds as (
    select * from {{ ref('stg_refunds') }}
),

orders as (
    select 
        order_id,
        customer_id,
        order_date
    from {{ ref('stg_orders') }}
)

select
    r.refund_id,
    r.order_id,
    o.customer_id,
    o.order_date as order_date,
    r.refund_date,
    r.refund_reason,
    r.refund_status,
    r.refund_amount
from refunds r
join orders o on r.order_id = o.order_id
