with customers as (
    select * from {{ ref('stg_customers') }}
),

customer_orders as (
    select * from {{ ref('int_customer_orders') }}
)

select
    c.customer_id,
    c.first_name,
    c.last_name,
    c.first_name || ' ' || c.last_name as full_name,
    c.email,
    c.signup_date,
    c.city,
    c.state,
    c.country,
    c.customer_segment,
    coalesce(co.total_orders, 0) as total_orders,
    co.first_order_date,
    co.last_order_date,
    coalesce(co.total_spend, 0.0) as lifetime_value,
    coalesce(co.average_order_value, 0.0) as average_order_value,
    case 
        when co.total_orders > 1 then true 
        else false 
    end as is_repeat_customer
from customers c
left join customer_orders co on c.customer_id = co.customer_id
