WITH source AS (
    SELECT * FROM {{ source('raw', 'people') }}
)

SELECT
    person_id,
    cookie_id,
    browser,
    consent_status,
    segment,
    primary_device,
    secondary_device,
    in_device_graph,
    graph_confidence,
    dma_code,
    dma_name,
    age_bracket,
    gender,
    hhi_bracket
FROM source
