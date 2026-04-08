WITH exposed_visits AS (
    SELECT
        ft.visit_id,
        ft.person_id,
        ft.visit_timestamp,
        ft.dma_code,
        ft.dma_name,
        ft.dwell_time_minutes,
        ft.campaign_id,
        ft.advertiser_id,
        ft.is_holdout_geo,
        ft.is_treatment_geo,
        ft.visit_source,
        CASE
            WHEN ft.is_holdout_geo THEN 'control'
            WHEN ft.is_treatment_geo THEN 'treatment'
            ELSE 'non_test'
        END AS test_group
    FROM {{ ref('stg_foot_traffic') }} ft
),

group_stats AS (
    SELECT
        test_group,
        COUNT(*) AS total_visits,
        COUNT(DISTINCT person_id) AS unique_visitors,
        AVG(dwell_time_minutes) AS avg_dwell_minutes
    FROM exposed_visits
    WHERE test_group IN ('control', 'treatment')
    GROUP BY test_group
),

lift_calc AS (
    SELECT
        t.total_visits AS treatment_visits,
        t.unique_visitors AS treatment_visitors,
        c.total_visits AS control_visits,
        c.unique_visitors AS control_visitors,
        CASE
            WHEN c.total_visits > 0
            THEN (t.total_visits::FLOAT / NULLIF(t.unique_visitors, 0))
                 / (c.total_visits::FLOAT / NULLIF(c.unique_visitors, 0)) - 1.0
            ELSE NULL
        END AS incremental_lift
    FROM group_stats t
    CROSS JOIN group_stats c
    WHERE t.test_group = 'treatment' AND c.test_group = 'control'
)

SELECT
    gs.test_group,
    gs.total_visits,
    gs.unique_visitors,
    gs.avg_dwell_minutes,
    lc.incremental_lift
FROM group_stats gs
CROSS JOIN lift_calc lc
