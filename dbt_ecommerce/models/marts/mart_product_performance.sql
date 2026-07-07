with order_items as (
    select * from {{ ref('fact_order_items') }}
),

products as (
    select * from {{ ref('dim_products') }}
),

refunds as (
    select * from {{ ref('fact_refunds') }}
)

select
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.brand,
    sum(oi.quantity) as total_units_sold,
    sum(oi.item_total) as net_revenue,
    sum(oi.quantity * p.cost_price) as total_cost,
    sum(oi.item_total) - sum(oi.quantity * p.cost_price) as gross_profit,
    count(distinct case when r.refund_id is not null then oi.order_id end) as order_refund_count,
    sum(case when r.refund_id is not null then oi.item_total else 0.0 end) as estimated_refund_amount,
    case 
        when sum(oi.quantity) > 0 then 
            round(sum(case when r.refund_id is not null then oi.quantity else 0 end)::numeric / sum(oi.quantity), 4)
        else 0.0000
    end as refund_rate_by_unit
from products p
left join order_items oi on p.product_id = oi.product_id
left join refunds r on oi.order_id = r.order_id and r.refund_status = 'processed'
group by p.product_id, p.product_name, p.category, p.subcategory, p.brand
order by net_revenue desc
