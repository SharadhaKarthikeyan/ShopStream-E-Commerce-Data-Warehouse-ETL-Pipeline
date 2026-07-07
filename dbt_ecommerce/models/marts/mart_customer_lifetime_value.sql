with dim_customers as (
    select * from {{ ref('dim_customers') }}
)

select
    customer_id,
    full_name,
    email,
    signup_date,
    city,
    state,
    customer_segment,
    total_orders,
    first_order_date,
    last_order_date,
    lifetime_value,
    average_order_value,
    is_repeat_customer,
    dense_rank() over (order by lifetime_value desc) as ltv_rank
from dim_customers
where total_orders > 0
order by lifetime_value desc
