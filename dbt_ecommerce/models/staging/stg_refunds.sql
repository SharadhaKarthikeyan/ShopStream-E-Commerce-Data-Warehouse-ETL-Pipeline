with source as (
    select * from {{ source('raw', 'refunds') }}
),

cleaned as (
    select
        trim(refund_id) as refund_id,
        trim(order_id) as order_id,
        trim(lower(refund_reason)) as refund_reason,
        trim(lower(refund_status)) as refund_status,
        refund_amount,
        refund_date,
        row_number() over (
            partition by refund_id 
            order by refund_date desc
        ) as rn
    from source
)

select
    refund_id,
    order_id,
    refund_reason,
    refund_status,
    refund_amount,
    refund_date
from cleaned
where rn = 1
