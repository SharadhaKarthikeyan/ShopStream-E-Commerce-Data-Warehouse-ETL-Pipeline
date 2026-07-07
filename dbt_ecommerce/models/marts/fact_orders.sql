with orders as (
    select * from {{ ref('stg_orders') }}
),

order_revenue as (
    select * from {{ ref('int_order_revenue') }}
),

refund_metrics as (
    select * from {{ ref('int_refund_metrics') }}
)

select
    o.order_id,
    o.customer_id,
    o.campaign_id,
    o.order_date,
    o.order_status,
    coalesce(r.gross_revenue, 0.0) as gross_revenue,
    coalesce(r.total_discount, 0.0) as total_discount,
    coalesce(r.total_tax, 0.0) as total_tax,
    coalesce(r.net_revenue, 0.0) as net_revenue,
    coalesce(r.total_items, 0) as total_items,
    coalesce(rm.total_refunded_amount, 0.0) as refunded_amount,
    case 
        when rm.total_refunded_amount > 0 then true 
        else false 
    end as is_refunded
from orders o
left join order_revenue r on o.order_id = r.order_id
left join refund_metrics rm on o.order_id = rm.order_id
