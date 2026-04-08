WITH daily_imps AS (
    SELECT
        DATE_TRUNC('day', impression_timestamp) AS report_date,
        campaign_id,
        campaign_name,
        advertiser_id,
        channel,
        COUNT(*) AS impressions,
        SUM(cpm / 1000.0) AS spend
    FROM {{ ref('stg_impressions') }}
    GROUP BY 1, 2, 3, 4, 5
),

daily_clicks AS (
    SELECT
        DATE_TRUNC('day', click_timestamp) AS report_date,
        campaign_id,
        channel,
        COUNT(*) AS clicks
    FROM {{ ref('stg_clicks') }}
    GROUP BY 1, 2, 3
),

daily_conversions AS (
    SELECT
        DATE_TRUNC('day', conversion_timestamp) AS report_date,
        campaign_id,
        model_type,
        channel,
        SUM(attributed_revenue) AS attributed_revenue,
        COUNT(DISTINCT conversion_id) AS conversions
    FROM {{ ref('attribution_results') }}
    GROUP BY 1, 2, 3, 4
)

SELECT
    i.report_date,
    i.campaign_id,
    i.campaign_name,
    i.advertiser_id,
    i.channel,
    i.impressions,
    i.spend,
    COALESCE(c.clicks, 0) AS clicks,
    COALESCE(dc.conversions, 0) AS conversions,
    COALESCE(dc.attributed_revenue, 0) AS attributed_revenue,
    COALESCE(dc.model_type, 'linear') AS model_type,
    CASE WHEN i.impressions > 0 THEN COALESCE(c.clicks, 0)::FLOAT / i.impressions ELSE 0 END AS ctr,
    CASE WHEN i.spend > 0 THEN COALESCE(dc.attributed_revenue, 0) / i.spend ELSE 0 END AS roas
FROM daily_imps i
LEFT JOIN daily_clicks c
    ON i.report_date = c.report_date AND i.campaign_id = c.campaign_id AND i.channel = c.channel
LEFT JOIN daily_conversions dc
    ON i.report_date = dc.report_date AND i.campaign_id = dc.campaign_id AND i.channel = dc.channel
