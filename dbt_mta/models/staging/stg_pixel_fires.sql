WITH source AS (
    SELECT * FROM {{ source('raw', 'pixel_fires') }}
),

consent_filtered AS (
    SELECT
        pixel_fire_id,
        click_id,
        impression_id,
        timestamp AS fire_timestamp,
        person_id,
        cookie_id,
        device_type,
        campaign_id,
        advertiser_id,
        consent_status,
        pixel_source,
        page_url,
        event_type
    FROM source
    WHERE consent_status IN ('full_consent', 'us_exempt')
)

SELECT * FROM consent_filtered
