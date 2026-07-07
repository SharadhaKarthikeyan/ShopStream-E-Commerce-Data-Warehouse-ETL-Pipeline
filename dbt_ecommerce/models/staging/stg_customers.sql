with source as (
    select * from {{ source('raw', 'customers') }}
),

cleaned as (
    select
        trim(customer_id) as customer_id,
        trim(first_name) as first_name,
        trim(last_name) as last_name,
        trim(lower(email)) as email,
        signup_date,
        trim(initcap(city)) as city,
        trim(upper(state)) as state,
        trim(upper(country)) as country,
        trim(initcap(customer_segment)) as customer_segment,
        row_number() over (
            partition by customer_id 
            order by signup_date desc
        ) as rn
    from source
)

select
    customer_id,
    first_name,
    last_name,
    email,
    signup_date,
    city,
    state,
    country,
    customer_segment
from cleaned
where rn = 1
