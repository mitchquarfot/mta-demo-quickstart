WITH impressions AS (
    SELECT
        impression_id AS event_id,
        impression_timestamp AS event_timestamp,
        'impression' AS event_type,
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
        cookie_reliability,
        is_trackable
    FROM {{ ref('stg_impressions') }}
),

clicks AS (
    SELECT
        click_id AS event_id,
        click_timestamp AS event_timestamp,
        'click' AS event_type,
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
        CASE
            WHEN browser IN ('safari') THEN 'itp_rotated'
            ELSE 'stable'
        END AS cookie_reliability,
        TRUE AS is_trackable
    FROM {{ ref('stg_clicks') }}
),

unioned AS (
    SELECT * FROM impressions
    UNION ALL
    SELECT * FROM clicks
),

resolved AS (
    SELECT
        u.*,
        dg.ramp_id,
        dg.confidence_score AS graph_confidence,
        dg.match_source AS graph_match_source,
        COALESCE(dg.ramp_id, u.cookie_id) AS resolved_id,
        CASE
            WHEN dg.ramp_id IS NOT NULL THEN 'device_graph'
            ELSE 'cookie_only'
        END AS resolution_method,
        ROW_NUMBER() OVER (
            PARTITION BY u.event_id
            ORDER BY dg.confidence_score DESC NULLS LAST
        ) AS match_rank
    FROM unioned u
    LEFT JOIN {{ ref('stg_device_graph') }} dg
        ON u.cookie_id = dg.identifier_value
        AND dg.identifier_type = 'cookie'
)

SELECT
    event_id,
    event_timestamp,
    event_type,
    person_id,
    cookie_id,
    resolved_id,
    resolution_method,
    ramp_id,
    graph_confidence,
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
    cookie_reliability,
    is_trackable
FROM resolved
WHERE match_rank = 1
