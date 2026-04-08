from fastapi import APIRouter, Query
from db import query_to_dicts
from filters import build_channel_filter

router = APIRouter(prefix="/api/v1", tags=["frequency"])


@router.get("/frequency")
def get_frequency(exclude_channels: str | None = Query(None)):
    where = ["1=1"]
    ch = build_channel_filter(exclude_channels)
    if ch:
        where.append(ch)
    return query_to_dicts(f"""
        SELECT CHANNEL, FREQUENCY_BUCKET, UNIQUE_USERS, TOTAL_IMPRESSIONS,
               ROUND(AVG_FREQUENCY, 1) AS AVG_FREQUENCY
        FROM MTA_DEMO.ANALYTICS.FREQUENCY_DISTRIBUTION
        WHERE {' AND '.join(where)}
        ORDER BY CHANNEL, FREQUENCY_BUCKET
    """)
