WITH source AS (
    SELECT * FROM {{ source('raw', 'foot_traffic') }}
)

SELECT
    visit_id,
    person_id,
    visit_timestamp,
    dma_code,
    dma_name,
    dwell_time_minutes,
    campaign_id,
    advertiser_id,
    is_holdout_geo,
    is_treatment_geo,
    visit_source
FROM source
