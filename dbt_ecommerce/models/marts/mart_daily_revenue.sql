with fact_orders as (
    select * from {{ ref('fact_orders') }}
)

select
    order_date,
    count(distinct order_id) as total_orders,
    sum(gross_revenue) as gross_revenue,
    sum(total_discount) as total_discount,
    sum(total_tax) as total_tax,
    sum(net_revenue) as net_revenue,
    sum(total_items) as total_items_sold,
    case 
        when count(distinct order_id) > 0 then round(sum(net_revenue) / count(distinct order_id), 2)
        else 0.00
    end as average_order_value
from fact_orders
where order_status not in ('cancelled')
group by order_date
order by order_date desc
