with payments as (
    select * from {{ ref('stg_payments') }}
),

orders as (
    select 
        order_id,
        customer_id,
        order_date
    from {{ ref('stg_orders') }}
)

select
    p.payment_id,
    p.order_id,
    o.customer_id,
    o.order_date,
    p.payment_method,
    p.payment_status,
    p.payment_amount,
    p.currency,
    p.transaction_id,
    p.payment_date
from payments p
join orders o on p.order_id = o.order_id
