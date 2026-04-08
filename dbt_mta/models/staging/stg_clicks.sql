WITH source AS (
    SELECT * FROM {{ source('raw', 'clicks') }}
)

SELECT
    click_id,
    impression_id,
    timestamp AS click_timestamp,
    person_id,
    cookie_id,
    device_type,
    browser,
    channel,
    campaign_id,
    campaign_name,
    advertiser_id,
    advertiser_name,
    creative_id,
    dma_code,
    consent_status,
    landing_page
FROM source
