WITH source AS (
    SELECT * FROM {{ source('raw', 'device_graph') }}
)

SELECT
    ramp_id,
    identifier_type,
    identifier_value,
    device_type,
    confidence_score,
    match_source,
    person_id
FROM source
