WITH touchpoints AS (
    SELECT
        ir.resolved_id,
        ir.event_id,
        ir.event_timestamp,
        ir.event_type,
        ir.channel,
        ir.campaign_id,
        ir.campaign_name,
        ir.advertiser_id,
        ir.advertiser_name,
        ir.creative_id,
        ir.device_type,
        ir.dma_code,
        ir.resolution_method
    FROM {{ ref('stg_identity_resolved') }} ir
    WHERE ir.is_trackable = TRUE
),

conversions AS (
    SELECT
        c.conversion_id,
        c.person_id,
        c.conversion_timestamp,
        c.conversion_type,
        c.conversion_value,
        c.campaign_id AS conversion_campaign_id,
        c.advertiser_id AS conversion_advertiser_id,
        dg.ramp_id AS resolved_id
    FROM {{ ref('stg_conversions_deduped') }} c
    LEFT JOIN {{ ref('stg_device_graph') }} dg
        ON c.cookie_id = dg.identifier_value
        AND dg.identifier_type = 'cookie'
),

conversion_paths AS (
    SELECT
        c.conversion_id,
        c.resolved_id AS conversion_resolved_id,
        c.conversion_timestamp,
        c.conversion_type,
        c.conversion_value,
        c.conversion_advertiser_id,
        t.event_id AS touchpoint_id,
        t.event_timestamp AS touchpoint_timestamp,
        t.event_type AS touchpoint_type,
        t.channel,
        t.campaign_id,
        t.campaign_name,
        t.advertiser_id,
        t.creative_id,
        t.device_type,
        t.dma_code,
        t.resolution_method,
        DATEDIFF('hour', t.event_timestamp, c.conversion_timestamp) AS hours_to_conversion,
        ROW_NUMBER() OVER (
            PARTITION BY c.conversion_id
            ORDER BY t.event_timestamp ASC
        ) AS touchpoint_position,
        COUNT(*) OVER (
            PARTITION BY c.conversion_id
        ) AS total_touchpoints
    FROM conversions c
    INNER JOIN touchpoints t
        ON COALESCE(c.resolved_id, c.conversion_resolved_id) = t.resolved_id
        AND t.event_timestamp <= c.conversion_timestamp
        AND t.event_timestamp >= DATEADD('day', -30, c.conversion_timestamp)
        AND t.advertiser_id = c.conversion_advertiser_id
)

SELECT * FROM conversion_paths
WHERE hours_to_conversion >= 0
