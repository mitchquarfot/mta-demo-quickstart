from fastapi import APIRouter
from db import query_to_dicts

router = APIRouter(prefix="/api/v1", tags=["identity"])


@router.get("/identity/stats")
def get_identity_stats():
    resolution = query_to_dicts("""
        SELECT RESOLUTION_METHOD, COUNT(*) AS EVENT_COUNT,
               ROUND(COUNT(*)::FLOAT / SUM(COUNT(*)) OVER (), 4) AS SHARE
        FROM MTA_DEMO.STAGING.STG_IDENTITY_RESOLVED
        GROUP BY 1
    """)
    by_channel = query_to_dicts("""
        SELECT CHANNEL, RESOLUTION_METHOD, COUNT(*) AS EVENT_COUNT
        FROM MTA_DEMO.STAGING.STG_IDENTITY_RESOLVED
        GROUP BY 1, 2
        ORDER BY 1, 2
    """)
    return {"resolution_methods": resolution, "by_channel": by_channel}
