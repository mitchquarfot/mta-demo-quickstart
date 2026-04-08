WITH source AS (
    SELECT * FROM {{ source('raw', 'impressions') }}
),

itp_flagged AS (
    SELECT
        impression_id,
        timestamp AS impression_timestamp,
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
        creative_format,
        dma_code,
        dma_name,
        consent_status,
        is_itp_affected,
        in_holdout_geo,
        cpm,
        CASE
            WHEN is_itp_affected THEN 'itp_rotated'
            ELSE 'stable'
        END AS cookie_reliability,
        CASE
            WHEN consent_status = 'rejected_all' THEN FALSE
            WHEN consent_status = 'essential_only' THEN FALSE
            ELSE TRUE
        END AS is_trackable
    FROM source
)

SELECT * FROM itp_flagged
