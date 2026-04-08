WITH daily_channel AS (
    SELECT
        DATE_TRUNC('day', impression_timestamp)::DATE AS report_date,
        channel AS series_key,
        COUNT(*) AS impressions,
        SUM(cpm / 1000.0) AS daily_spend
    FROM {{ ref('stg_impressions') }}
    GROUP BY 1, 2
),

daily_revenue AS (
    SELECT
        DATE_TRUNC('day', conversion_timestamp)::DATE AS report_date,
        channel AS series_key,
        SUM(attributed_revenue) AS daily_attributed_revenue
    FROM {{ ref('attribution_results') }}
    WHERE model_type = 'linear'
    GROUP BY 1, 2
)

SELECT
    dc.report_date,
    dc.series_key,
    dc.impressions,
    dc.daily_spend,
    COALESCE(dr.daily_attributed_revenue, 0) AS daily_attributed_revenue
FROM daily_channel dc
LEFT JOIN daily_revenue dr
    ON dc.report_date = dr.report_date AND dc.series_key = dr.series_key
ORDER BY dc.report_date, dc.series_key
