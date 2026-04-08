from fastapi import APIRouter, Query
from db import query_to_dicts
from filters import build_channel_filter

router = APIRouter(prefix="/api/v1", tags=["paths"])


@router.get("/conversion-paths/stats")
def get_path_stats(exclude_channels: str | None = Query(None)):
    where = ["1=1"]
    ch = build_channel_filter(exclude_channels)
    if ch:
        where.append(ch)
    return query_to_dicts(f"""
        SELECT TOTAL_TOUCHPOINTS AS PATH_LENGTH,
            COUNT(DISTINCT CONVERSION_ID) AS CONVERSIONS,
            ROUND(AVG(CONVERSION_VALUE), 2) AS AVG_VALUE,
            ROUND(AVG(HOURS_TO_CONVERSION), 1) AS AVG_HOURS_TO_CONVERT
        FROM MTA_DEMO.ANALYTICS.CONVERSION_PATHS
        WHERE {' AND '.join(where)}
        GROUP BY 1
        ORDER BY 1
    """)


@router.get("/conversion-paths/top-sequences")
def get_top_sequences(limit: int = Query(20), exclude_channels: str | None = Query(None)):
    where = ["1=1"]
    ch = build_channel_filter(exclude_channels)
    if ch:
        where.append(ch)
    return query_to_dicts(f"""
        WITH sequenced AS (
            SELECT CONVERSION_ID,
                   LISTAGG(CHANNEL, ' > ') WITHIN GROUP (ORDER BY TOUCHPOINT_POSITION) AS PATH
            FROM MTA_DEMO.ANALYTICS.CONVERSION_PATHS
            WHERE {' AND '.join(where)}
            GROUP BY CONVERSION_ID
        )
        SELECT PATH, COUNT(*) AS CONVERSIONS
        FROM sequenced
        GROUP BY PATH
        ORDER BY CONVERSIONS DESC
        LIMIT {limit}
    """)


@router.get("/conversion-paths/channel-position")
def get_channel_position(exclude_channels: str | None = Query(None)):
    where = ["1=1"]
    ch = build_channel_filter(exclude_channels)
    if ch:
        where.append(ch)
    return query_to_dicts(f"""
        SELECT CHANNEL,
               ROUND(AVG(TOUCHPOINT_POSITION), 1) AS AVG_POSITION,
               ROUND(AVG(TOTAL_TOUCHPOINTS), 1) AS AVG_PATH_LENGTH,
               ROUND(AVG(TOUCHPOINT_POSITION::FLOAT / TOTAL_TOUCHPOINTS), 3) AS AVG_RELATIVE_POSITION,
               COUNT(CASE WHEN TOUCHPOINT_POSITION = 1 THEN 1 END) AS FIRST_TOUCH_COUNT,
               COUNT(CASE WHEN TOUCHPOINT_POSITION = TOTAL_TOUCHPOINTS THEN 1 END) AS LAST_TOUCH_COUNT,
               COUNT(*) AS TOTAL_TOUCHPOINTS_IN_PATHS
        FROM MTA_DEMO.ANALYTICS.CONVERSION_PATHS
        WHERE {' AND '.join(where)}
        GROUP BY CHANNEL
        ORDER BY AVG_RELATIVE_POSITION ASC
    """)
