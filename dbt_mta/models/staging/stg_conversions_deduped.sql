WITH raw AS (
    SELECT * FROM {{ ref('stg_conversions_raw') }}
    WHERE is_primary_conversion = TRUE
)

SELECT
    conversion_id,
    person_id,
    cookie_id,
    device_type,
    campaign_id,
    advertiser_id,
    conversion_type,
    conversion_value,
    conversion_timestamp,
    triggering_click_id,
    triggering_impression_id,
    conversion_source,
    is_view_through,
    view_through_channel
FROM raw
