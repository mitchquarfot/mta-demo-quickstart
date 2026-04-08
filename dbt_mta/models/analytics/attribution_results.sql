WITH paths AS (
    SELECT * FROM {{ ref('conversion_paths') }}
),

last_touch AS (
    SELECT
        conversion_id,
        touchpoint_id,
        channel,
        campaign_id,
        campaign_name,
        advertiser_id,
        conversion_value,
        conversion_type,
        conversion_timestamp,
        CASE WHEN touchpoint_position = total_touchpoints THEN 1.0 ELSE 0.0 END AS attribution_weight,
        'last_touch' AS model_type
    FROM paths
),

first_touch AS (
    SELECT
        conversion_id,
        touchpoint_id,
        channel,
        campaign_id,
        campaign_name,
        advertiser_id,
        conversion_value,
        conversion_type,
        conversion_timestamp,
        CASE WHEN touchpoint_position = 1 THEN 1.0 ELSE 0.0 END AS attribution_weight,
        'first_touch' AS model_type
    FROM paths
),

linear AS (
    SELECT
        conversion_id,
        touchpoint_id,
        channel,
        campaign_id,
        campaign_name,
        advertiser_id,
        conversion_value,
        conversion_type,
        conversion_timestamp,
        1.0 / NULLIF(total_touchpoints, 0) AS attribution_weight,
        'linear' AS model_type
    FROM paths
),

time_decay AS (
    SELECT
        conversion_id,
        touchpoint_id,
        channel,
        campaign_id,
        campaign_name,
        advertiser_id,
        conversion_value,
        conversion_type,
        conversion_timestamp,
        hours_to_conversion,
        total_touchpoints,
        POW(0.5, hours_to_conversion / 168.0) AS raw_weight,
        'time_decay' AS model_type
    FROM paths
),

time_decay_normalized AS (
    SELECT
        conversion_id,
        touchpoint_id,
        channel,
        campaign_id,
        campaign_name,
        advertiser_id,
        conversion_value,
        conversion_type,
        conversion_timestamp,
        raw_weight / NULLIF(SUM(raw_weight) OVER (PARTITION BY conversion_id), 0) AS attribution_weight,
        'time_decay' AS model_type
    FROM time_decay
),

position_based AS (
    SELECT
        conversion_id,
        touchpoint_id,
        channel,
        campaign_id,
        campaign_name,
        advertiser_id,
        conversion_value,
        conversion_type,
        conversion_timestamp,
        touchpoint_position,
        total_touchpoints,
        CASE
            WHEN total_touchpoints = 1 THEN 1.0
            WHEN touchpoint_position = 1 THEN 0.4
            WHEN touchpoint_position = total_touchpoints THEN 0.4
            ELSE 0.2 / NULLIF(total_touchpoints - 2, 0)
        END AS attribution_weight,
        'position_based' AS model_type
    FROM paths
),

all_models AS (
    SELECT conversion_id, touchpoint_id, channel, campaign_id, campaign_name, advertiser_id, conversion_value, conversion_type, conversion_timestamp, attribution_weight, model_type FROM last_touch
    UNION ALL
    SELECT conversion_id, touchpoint_id, channel, campaign_id, campaign_name, advertiser_id, conversion_value, conversion_type, conversion_timestamp, attribution_weight, model_type FROM first_touch
    UNION ALL
    SELECT conversion_id, touchpoint_id, channel, campaign_id, campaign_name, advertiser_id, conversion_value, conversion_type, conversion_timestamp, attribution_weight, model_type FROM linear
    UNION ALL
    SELECT conversion_id, touchpoint_id, channel, campaign_id, campaign_name, advertiser_id, conversion_value, conversion_type, conversion_timestamp, attribution_weight, model_type FROM time_decay_normalized
    UNION ALL
    SELECT conversion_id, touchpoint_id, channel, campaign_id, campaign_name, advertiser_id, conversion_value, conversion_type, conversion_timestamp, attribution_weight, model_type FROM position_based
)

SELECT
    conversion_id,
    touchpoint_id,
    channel,
    campaign_id,
    campaign_name,
    advertiser_id,
    conversion_type,
    conversion_timestamp,
    model_type,
    attribution_weight,
    conversion_value * attribution_weight AS attributed_revenue
FROM all_models
