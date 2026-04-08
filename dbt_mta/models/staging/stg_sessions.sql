WITH source AS (
    SELECT * FROM {{ source('raw', 'sessions') }}
),

consent_filtered AS (
    SELECT
        session_id,
        click_id,
        timestamp AS session_timestamp,
        person_id,
        cookie_id,
        device_type,
        browser,
        campaign_id,
        advertiser_id,
        consent_status,
        session_source,
        landing_page,
        duration_seconds,
        pages_viewed,
        is_bounce
    FROM source
    WHERE consent_status != 'rejected_all'
)

SELECT * FROM consent_filtered
