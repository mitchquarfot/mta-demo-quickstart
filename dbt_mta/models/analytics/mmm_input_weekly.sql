WITH weekly_channel AS (
    SELECT
        DATE_TRUNC('week', impression_timestamp) AS week_start,
        channel,
        advertiser_id,
        COUNT(*) AS impressions,
        SUM(cpm / 1000.0) AS spend
    FROM {{ ref('stg_impressions') }}
    GROUP BY 1, 2, 3
),

weekly_conversions AS (
    SELECT
        DATE_TRUNC('week', conversion_timestamp) AS week_start,
        channel,
        advertiser_id,
        SUM(attributed_revenue) AS attributed_revenue,
        COUNT(DISTINCT conversion_id) AS conversions
    FROM {{ ref('attribution_results') }}
    WHERE model_type = 'linear'
    GROUP BY 1, 2, 3
)

SELECT
    wc.week_start,
    wc.channel,
    wc.advertiser_id,
    wc.impressions,
    wc.spend,
    COALESCE(wcv.conversions, 0) AS conversions,
    COALESCE(wcv.attributed_revenue, 0) AS attributed_revenue,
    LN(GREATEST(wc.spend, 0.01)) AS ln_spend,
    LN(GREATEST(COALESCE(wcv.attributed_revenue, 0.01), 0.01)) AS ln_revenue
FROM weekly_channel wc
LEFT JOIN weekly_conversions wcv
    ON wc.week_start = wcv.week_start
    AND wc.channel = wcv.channel
    AND wc.advertiser_id = wcv.advertiser_id
ORDER BY wc.week_start, wc.channel
