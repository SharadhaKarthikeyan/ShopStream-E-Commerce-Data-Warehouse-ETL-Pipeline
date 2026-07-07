with order_items as (
    select * from {{ ref('stg_order_items') }}
)

select
    order_id,
    sum(quantity * unit_price) as gross_revenue,
    sum(discount) as total_discount,
    sum(tax) as total_tax,
    sum(item_total) as net_revenue,
    sum(quantity) as total_items
from order_items
group by order_id
