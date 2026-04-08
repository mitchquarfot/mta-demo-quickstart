from fastapi import APIRouter, Query
from db import query_to_dicts
from filters import build_channel_filter

router = APIRouter(prefix="/api/v1", tags=["forecast"])


@router.get("/forecast")
def get_forecast(exclude_channels: str | None = Query(None)):
    where_h = ["1=1"]
    where_f = ["1=1"]
    ch = build_channel_filter(exclude_channels)
    if ch:
        where_h.append(ch)
        where_f.append(ch)
    historical = query_to_dicts(f"""
        SELECT CHANNEL, WEEK_START, REVENUE AS VALUE, 'actual' AS TYPE
        FROM MTA_DEMO.ANALYTICS.V_CHANNEL_WEEKLY
        WHERE {' AND '.join(where_h)}
        ORDER BY CHANNEL, WEEK_START
    """)
    predicted = query_to_dicts(f"""
        SELECT CHANNEL, WEEK_START, FORECAST AS VALUE, LOWER_BOUND, UPPER_BOUND, 'forecast' AS TYPE
        FROM MTA_DEMO.ANALYTICS.CHANNEL_FORECAST
        WHERE {' AND '.join(where_f)}
        ORDER BY CHANNEL, WEEK_START
    """)
    return {"historical": historical, "forecast": predicted}


@router.get("/forecast/metrics")
def get_forecast_metrics():
    return query_to_dicts("""
        SELECT * FROM MTA_DEMO.ANALYTICS.FORECAST_METRICS
        ORDER BY SERIES, ERROR_METRIC
    """)
