from fastapi import APIRouter, Query
from db import query_to_dicts
from filters import build_channel_filter, build_date_filter

router = APIRouter(prefix="/api/v1", tags=["campaigns"])


@router.get("/campaigns")
def list_campaigns():
    return query_to_dicts("""
        SELECT DISTINCT CAMPAIGN_ID, CAMPAIGN_NAME, ADVERTISER_ID
        FROM MTA_DEMO.ANALYTICS.CAMPAIGN_DAILY_METRICS
        ORDER BY CAMPAIGN_ID
    """)


@router.get("/campaigns/{campaign_id}/daily")
def get_campaign_daily(
    campaign_id: str,
    model_type: str = Query("linear"),
    exclude_channels: str | None = Query(None),
    date_start: str | None = Query(None),
    date_end: str | None = Query(None),
):
    where = [f"CAMPAIGN_ID = '{campaign_id}'", f"MODEL_TYPE = '{model_type}'"]
    ch = build_channel_filter(exclude_channels)
    if ch:
        where.append(ch)
    where.extend(build_date_filter(date_start, date_end, "REPORT_DATE"))
    sql = f"""
        SELECT REPORT_DATE, CHANNEL, IMPRESSIONS, SPEND, CLICKS,
               CONVERSIONS, ATTRIBUTED_REVENUE, CTR, ROAS
        FROM MTA_DEMO.ANALYTICS.CAMPAIGN_DAILY_METRICS
        WHERE {' AND '.join(where)}
        ORDER BY REPORT_DATE
    """
    return query_to_dicts(sql)
