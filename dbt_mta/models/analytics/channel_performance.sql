WITH attribution AS (
    SELECT * FROM {{ ref('attribution_results') }}
),

impressions AS (
    SELECT
        campaign_id,
        channel,
        advertiser_id,
        COUNT(*) AS impressions,
        SUM(cpm / 1000.0) AS spend
    FROM {{ ref('stg_impressions') }}
    GROUP BY 1, 2, 3
),

clicks AS (
    SELECT
        campaign_id,
        channel,
        COUNT(*) AS clicks
    FROM {{ ref('stg_clicks') }}
    GROUP BY 1, 2
),

attr_summary AS (
    SELECT
        model_type,
        channel,
        campaign_id,
        campaign_name,
        advertiser_id,
        SUM(attribution_weight) AS attributed_conversions,
        SUM(attributed_revenue) AS attributed_revenue
    FROM attribution
    GROUP BY 1, 2, 3, 4, 5
)

SELECT
    a.model_type,
    a.channel,
    a.campaign_id,
    a.campaign_name,
    a.advertiser_id,
    COALESCE(i.impressions, 0) AS impressions,
    COALESCE(i.spend, 0) AS spend,
    COALESCE(c.clicks, 0) AS clicks,
    a.attributed_conversions,
    a.attributed_revenue,
    CASE WHEN i.impressions > 0 THEN c.clicks::FLOAT / i.impressions ELSE 0 END AS ctr,
    CASE WHEN i.impressions > 0 THEN a.attributed_conversions::FLOAT / i.impressions ELSE 0 END AS conversion_rate,
    CASE WHEN i.spend > 0 THEN a.attributed_revenue / i.spend ELSE 0 END AS roas,
    CASE WHEN a.attributed_conversions > 0 THEN i.spend / a.attributed_conversions ELSE 0 END AS cpa
FROM attr_summary a
LEFT JOIN impressions i
    ON a.campaign_id = i.campaign_id AND a.channel = i.channel AND a.advertiser_id = i.advertiser_id
LEFT JOIN clicks c
    ON a.campaign_id = c.campaign_id AND a.channel = c.channel
