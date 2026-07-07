with date_series as (
    select 
        date_actual::date as date_day
    from generate_series(
        '2023-01-01'::date,
        '2026-12-31'::date,
        '1 day'::interval
    ) as date_actual
)

select
    date_day,
    extract(year from date_day)::int as year,
    extract(month from date_day)::int as month,
    to_char(date_day, 'Month') as month_name,
    to_char(date_day, 'DY') as day_of_week,
    extract(day from date_day)::int as day_of_month,
    extract(quarter from date_day)::int as quarter,
    case 
        when extract(isodow from date_day) in (6, 7) then true
        else false
    end as is_weekend
from date_series
order by date_day asc
