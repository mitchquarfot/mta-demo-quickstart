WITH impressions AS (
    SELECT
        person_id,
        channel,
        campaign_id,
        COUNT(*) AS impression_count
    FROM {{ ref('stg_impressions') }}
    GROUP BY 1, 2, 3
),

bucketed AS (
    SELECT
        person_id,
        channel,
        campaign_id,
        impression_count,
        CASE
            WHEN impression_count BETWEEN 1 AND 5 THEN '01-05'
            WHEN impression_count BETWEEN 6 AND 15 THEN '06-15'
            WHEN impression_count BETWEEN 16 AND 30 THEN '16-30'
            WHEN impression_count BETWEEN 31 AND 60 THEN '31-60'
            WHEN impression_count BETWEEN 61 AND 100 THEN '61-100'
            WHEN impression_count BETWEEN 101 AND 500 THEN '101-500'
            WHEN impression_count > 500 THEN '500+'
        END AS frequency_bucket
    FROM impressions
)

SELECT
    channel,
    frequency_bucket,
    COUNT(DISTINCT person_id) AS unique_users,
    SUM(impression_count) AS total_impressions,
    AVG(impression_count) AS avg_frequency
FROM bucketed
GROUP BY 1, 2
ORDER BY channel, frequency_bucket
