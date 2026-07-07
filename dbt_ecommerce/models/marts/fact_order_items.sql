with order_items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select 
        order_id,
        customer_id,
        order_date,
        campaign_id
    from {{ ref('stg_orders') }}
)

select
    oi.order_item_id,
    oi.order_id,
    oi.product_id,
    o.customer_id,
    o.campaign_id,
    o.order_date,
    oi.quantity,
    oi.unit_price,
    oi.discount,
    oi.tax,
    oi.item_total
from order_items oi
join orders o on oi.order_id = o.order_id
