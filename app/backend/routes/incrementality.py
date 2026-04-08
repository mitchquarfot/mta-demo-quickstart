from fastapi import APIRouter
from db import query_to_dicts

router = APIRouter(prefix="/api/v1", tags=["incrementality"])


@router.get("/incrementality")
def get_incrementality():
    return query_to_dicts("SELECT * FROM MTA_DEMO.ANALYTICS.INCREMENTALITY_RESULTS")


@router.get("/foot-traffic")
def get_foot_traffic_by_dma():
    return query_to_dicts("""
        SELECT DMA_CODE, DMA_NAME,
               COUNT(*) AS VISITS,
               COUNT(DISTINCT PERSON_ID) AS UNIQUE_VISITORS,
               ROUND(AVG(DWELL_TIME_MINUTES), 1) AS AVG_DWELL
        FROM MTA_DEMO.STAGING.STG_FOOT_TRAFFIC
        GROUP BY 1, 2
        ORDER BY VISITS DESC
    """)
