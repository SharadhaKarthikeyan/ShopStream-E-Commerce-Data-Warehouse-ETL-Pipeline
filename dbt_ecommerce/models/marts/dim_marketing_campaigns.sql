with campaigns as (
    select
        campaign_id,
        campaign_name,
        channel,
        budget,
        start_date,
        end_date,
        target_segment
    from {{ ref('stg_marketing_campaigns') }}
),

organic as (
    select
        'organic' as campaign_id,
        'Organic Traffic' as campaign_name,
        'None' as channel,
        0.00 as budget,
        '2023-01-01'::date as start_date,
        '2026-12-31'::date as end_date,
        'General' as target_segment
)

select * from campaigns
union all
select * from organic
