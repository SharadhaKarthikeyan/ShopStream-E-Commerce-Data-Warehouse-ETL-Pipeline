with products as (
    select * from {{ ref('stg_products') }}
)

select
    product_id,
    product_name,
    category,
    subcategory,
    brand,
    unit_price,
    cost_price,
    (unit_price - cost_price) as markup_amount,
    case 
        when cost_price > 0 then round((unit_price - cost_price) / cost_price, 4)
        else 0
    end as markup_pct,
    is_active
from products
