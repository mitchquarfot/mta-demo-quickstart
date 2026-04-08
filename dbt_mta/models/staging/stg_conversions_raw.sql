WITH source AS (
    SELECT * FROM {{ source('raw', 'conversions') }}
),

ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY person_id, DATE_TRUNC('minute', conversion_timestamp)
            ORDER BY
                CASE conversion_source
                    WHEN 'gcm_floodlight' THEN 1
                    WHEN 'gtm_pixel' THEN 2
                    WHEN 'ga4_goal' THEN 3
                    ELSE 4
                END
        ) AS dedup_rank
    FROM source
    WHERE consent_status IS NULL
       OR consent_status NOT IN ('rejected_all')
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
    is_duplicate,
    COALESCE(is_view_through, FALSE) AS is_view_through,
    view_through_channel,
    dedup_rank = 1 AS is_primary_conversion,
    dedup_rank
FROM ranked
