WITH identity_health AS (
    SELECT
        channel,
        COUNT(*) AS total_events,
        SUM(CASE WHEN resolution_method = 'device_graph' THEN 1 ELSE 0 END) AS graph_matched,
        SUM(CASE WHEN cookie_reliability = 'itp_rotated' THEN 1 ELSE 0 END) AS itp_affected,
        SUM(CASE WHEN is_trackable = FALSE THEN 1 ELSE 0 END) AS consent_blocked,
        ROUND(graph_matched / NULLIF(total_events, 0), 4) AS match_rate,
        ROUND(itp_affected / NULLIF(total_events, 0), 4) AS itp_rate,
        ROUND(consent_blocked / NULLIF(total_events, 0), 4) AS consent_block_rate
    FROM {{ ref('stg_identity_resolved') }}
    GROUP BY channel
)

SELECT * FROM identity_health
