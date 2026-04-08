from fastapi import APIRouter, Query
from db import query_to_dicts
from filters import build_channel_filter

router = APIRouter(prefix="/api/v1", tags=["channels"])


@router.get("/channel-performance")
def get_channel_performance(
    model_type: str = Query("linear"),
    exclude_channels: str | None = Query(None),
):
    where = [f"MODEL_TYPE = '{model_type}'"]
    ch = build_channel_filter(exclude_channels)
    if ch:
        where.append(ch)
    sql = f"""
        SELECT CHANNEL, CAMPAIGN_ID, CAMPAIGN_NAME, ADVERTISER_ID,
               IMPRESSIONS, SPEND, CLICKS, ATTRIBUTED_CONVERSIONS, ATTRIBUTED_REVENUE,
               CTR, CONVERSION_RATE, ROAS, CPA
        FROM MTA_DEMO.ANALYTICS.CHANNEL_PERFORMANCE
        WHERE {' AND '.join(where)}
        ORDER BY ATTRIBUTED_REVENUE DESC
    """
    return query_to_dicts(sql)


@router.get("/channel-summary")
def get_channel_summary(
    model_type: str = Query("linear"),
    exclude_channels: str | None = Query(None),
):
    where = [f"MODEL_TYPE = '{model_type}'"]
    ch = build_channel_filter(exclude_channels)
    if ch:
        where.append(ch)
    sql = f"""
        SELECT CHANNEL,
               SUM(IMPRESSIONS) AS IMPRESSIONS,
               SUM(SPEND) AS SPEND,
               SUM(CLICKS) AS CLICKS,
               SUM(ATTRIBUTED_CONVERSIONS) AS ATTRIBUTED_CONVERSIONS,
               SUM(ATTRIBUTED_REVENUE) AS ATTRIBUTED_REVENUE,
               CASE WHEN SUM(SPEND) > 0 THEN SUM(ATTRIBUTED_REVENUE) / SUM(SPEND) ELSE 0 END AS ROAS,
               CASE WHEN SUM(ATTRIBUTED_CONVERSIONS) > 0 THEN SUM(SPEND) / SUM(ATTRIBUTED_CONVERSIONS) ELSE 0 END AS CPA
        FROM MTA_DEMO.ANALYTICS.CHANNEL_PERFORMANCE
        WHERE {' AND '.join(where)}
        GROUP BY CHANNEL
        ORDER BY SPEND DESC
    """
    return query_to_dicts(sql)
