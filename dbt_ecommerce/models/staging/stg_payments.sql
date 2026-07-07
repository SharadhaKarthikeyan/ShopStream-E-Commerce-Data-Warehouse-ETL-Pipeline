with source as (
    select * from {{ source('raw', 'payments') }}
),

cleaned as (
    select
        trim(payment_id) as payment_id,
        trim(order_id) as order_id,
        trim(lower(payment_method)) as payment_method,
        trim(lower(payment_status)) as payment_status,
        payment_amount,
        trim(upper(currency)) as currency,
        trim(transaction_id) as transaction_id,
        payment_date,
        row_number() over (
            partition by payment_id 
            order by payment_date desc
        ) as rn
    from source
)

select
    payment_id,
    order_id,
    payment_method,
    payment_status,
    payment_amount,
    currency,
    transaction_id,
    payment_date
from cleaned
where rn = 1
