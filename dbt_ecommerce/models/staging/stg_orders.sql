with source as (
    select * from {{ source('raw', 'orders') }}
),

cleaned as (
    select
        trim(order_id) as order_id,
        trim(customer_id) as customer_id,
        order_date,
        trim(lower(order_status)) as order_status,
        coalesce(nullif(trim(campaign_id), ''), 'organic') as campaign_id,
        row_number() over (
            partition by order_id 
            order by order_date desc
        ) as rn
    from source
)

select
    order_id,
    customer_id,
    order_date,
    order_status,
    campaign_id
from cleaned
where rn = 1
