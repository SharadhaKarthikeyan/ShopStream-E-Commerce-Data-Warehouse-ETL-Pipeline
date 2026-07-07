with fact_orders as (
    select * from {{ ref('fact_orders') }}
),

campaigns as (
    select * from {{ ref('dim_marketing_campaigns') }}
)

select
    c.campaign_id,
    c.campaign_name,
    c.channel,
    c.budget,
    c.start_date,
    c.end_date,
    count(distinct o.order_id) as total_orders,
    sum(coalesce(o.net_revenue, 0.0)) as total_revenue,
    case 
        when c.budget > 0 then round(sum(coalesce(o.net_revenue, 0.0)) / c.budget, 2)
        else 0.00
    end as campaign_roi
from campaigns c
left join fact_orders o on c.campaign_id = o.campaign_id and o.order_status not in ('cancelled')
group by c.campaign_id, c.campaign_name, c.channel, c.budget, c.start_date, c.end_date
order by total_revenue desc
