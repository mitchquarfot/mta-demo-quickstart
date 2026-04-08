WITH dedup_stats AS (
    SELECT
        conversion_source,
        COUNT(*) AS total_fires,
        SUM(CASE WHEN is_primary_conversion THEN 1 ELSE 0 END) AS primary_fires,
        SUM(CASE WHEN NOT is_primary_conversion THEN 1 ELSE 0 END) AS duplicate_fires
    FROM {{ ref('stg_conversions_raw') }}
    GROUP BY conversion_source
),

overall AS (
    SELECT
        COUNT(*) AS total_raw_conversions,
        SUM(CASE WHEN is_primary_conversion THEN 1 ELSE 0 END) AS deduped_conversions,
        SUM(CASE WHEN NOT is_primary_conversion THEN 1 ELSE 0 END) AS duplicates_removed,
        ROUND(duplicates_removed::FLOAT / NULLIF(total_raw_conversions, 0), 4) AS dedup_rate
    FROM {{ ref('stg_conversions_raw') }}
)

SELECT
    'by_source' AS report_type,
    d.conversion_source,
    d.total_fires,
    d.primary_fires,
    d.duplicate_fires,
    NULL AS dedup_rate
FROM dedup_stats d
UNION ALL
SELECT
    'overall' AS report_type,
    'ALL' AS conversion_source,
    o.total_raw_conversions AS total_fires,
    o.deduped_conversions AS primary_fires,
    o.duplicates_removed AS duplicate_fires,
    o.dedup_rate
FROM overall o
