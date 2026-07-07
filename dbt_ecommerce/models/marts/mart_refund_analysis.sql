with refunds as (
    select * from {{ ref('fact_refunds') }}
),

orders as (
    select * from {{ ref('fact_orders') }}
),

store_totals as (
    select 
        sum(net_revenue) as total_store_sales,
        count(distinct order_id) as total_store_orders
    from orders
    where order_status not in ('cancelled')
)

select
    r.refund_reason,
    r.refund_status,
    count(r.refund_id) as refund_count,
    sum(r.refund_amount) as total_refund_amount,
    round(avg(r.refund_amount), 2) as average_refund_amount,
    (select total_store_sales from store_totals) as total_store_sales,
    case 
        when (select total_store_sales from store_totals) > 0 then
            round(sum(r.refund_amount) / (select total_store_sales from store_totals), 4)
        else 0.0000
    end as refund_to_sales_ratio
from refunds r
group by r.refund_reason, r.refund_status
order by total_refund_amount desc
