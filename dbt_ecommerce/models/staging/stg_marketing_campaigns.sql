with source as (
    select * from {{ source('raw', 'marketing_campaigns') }}
),

cleaned as (
    select
        trim(campaign_id) as campaign_id,
        trim(campaign_name) as campaign_name,
        trim(initcap(channel)) as channel,
        budget,
        start_date,
        end_date,
        trim(initcap(target_segment)) as target_segment,
        row_number() over (
            partition by campaign_id 
            order by start_date desc
        ) as rn
    from source
)

select
    campaign_id,
    campaign_name,
    channel,
    budget,
    start_date,
    end_date,
    target_segment
from cleaned
where rn = 1
