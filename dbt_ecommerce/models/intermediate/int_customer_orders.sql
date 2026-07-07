with orders as (
    select * from {{ ref('stg_orders') }}
),

order_revenue as (
    select * from {{ ref('int_order_revenue') }}
),

customer_aggregates as (
    select
        o.customer_id,
        count(distinct o.order_id) as total_orders,
        min(o.order_date) as first_order_date,
        max(o.order_date) as last_order_date,
        sum(coalesce(r.net_revenue, 0)) as total_spend,
        avg(coalesce(r.net_revenue, 0)) as average_order_value
    from orders o
    left join order_revenue r on o.order_id = r.order_id
    group by o.customer_id
)

select * from customer_aggregates
