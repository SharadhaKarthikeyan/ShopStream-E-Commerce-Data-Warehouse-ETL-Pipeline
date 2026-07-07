with source as (
    select * from {{ source('raw', 'order_items') }}
),

cleaned as (
    select
        trim(order_item_id) as order_item_id,
        trim(order_id) as order_id,
        trim(product_id) as product_id,
        quantity,
        unit_price,
        discount,
        tax,
        item_total,
        row_number() over (
            partition by order_item_id 
            order by item_total desc
        ) as rn
    from source
)

select
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    discount,
    tax,
    item_total
from cleaned
where rn = 1
