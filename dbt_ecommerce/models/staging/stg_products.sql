with source as (
    select * from {{ source('raw', 'products') }}
),

cleaned as (
    select
        trim(product_id) as product_id,
        trim(product_name) as product_name,
        trim(initcap(category)) as category,
        trim(initcap(subcategory)) as subcategory,
        trim(brand) as brand,
        unit_price,
        cost_price,
        case 
            when lower(trim(active_flag)) in ('true', 'active') then true
            else false
        end as is_active,
        row_number() over (
            partition by product_id 
            order by unit_price desc
        ) as rn
    from source
)

select
    product_id,
    product_name,
    category,
    subcategory,
    brand,
    unit_price,
    cost_price,
    is_active
from cleaned
where rn = 1
