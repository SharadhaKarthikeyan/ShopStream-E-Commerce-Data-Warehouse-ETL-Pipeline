with fact_shipments as (
    select * from {{ ref('fact_shipments') }}
)

select
    shipping_provider,
    count(shipment_id) as total_shipments,
    count(case when shipment_status = 'delivered' then 1 end) as completed_deliveries,
    round(avg(delivery_duration_days), 2) as average_delivery_days,
    sum(is_delayed) as delayed_shipments,
    round(sum(is_delayed)::numeric / count(shipment_id), 4) as delay_rate
from fact_shipments
group by shipping_provider
order by delay_rate desc
