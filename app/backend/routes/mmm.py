from fastapi import APIRouter, Query
from db import query_to_dicts
from filters import build_channel_filter, build_date_filter

router = APIRouter(prefix="/api/v1", tags=["mmm"])


@router.get("/mmm-weekly")
def get_mmm_weekly(
    exclude_channels: str | None = Query(None),
    date_start: str | None = Query(None),
    date_end: str | None = Query(None),
):
    where = ["1=1"]
    ch = build_channel_filter(exclude_channels)
    if ch:
        where.append(ch)
    where.extend(build_date_filter(date_start, date_end, "WEEK_START"))
    sql = f"""
        SELECT WEEK_START, CHANNEL, ADVERTISER_ID, IMPRESSIONS, SPEND,
               CONVERSIONS, ATTRIBUTED_REVENUE, LN_SPEND, LN_REVENUE
        FROM MTA_DEMO.ANALYTICS.MMM_INPUT_WEEKLY
        WHERE {' AND '.join(where)}
        ORDER BY WEEK_START, CHANNEL
    """
    return query_to_dicts(sql)


@router.get("/mmm-summary")
def get_mmm_summary(
    exclude_channels: str | None = Query(None),
    date_start: str | None = Query(None),
    date_end: str | None = Query(None),
):
    where = ["1=1"]
    ch = build_channel_filter(exclude_channels)
    if ch:
        where.append(ch)
    where.extend(build_date_filter(date_start, date_end, "WEEK_START"))
    sql = f"""
        SELECT CHANNEL,
               SUM(SPEND) AS TOTAL_SPEND,
               SUM(ATTRIBUTED_REVENUE) AS TOTAL_REVENUE,
               CASE WHEN SUM(SPEND) > 0 THEN ROUND(SUM(ATTRIBUTED_REVENUE) / SUM(SPEND), 2) ELSE 0 END AS MMM_ROAS
        FROM MTA_DEMO.ANALYTICS.MMM_INPUT_WEEKLY
        WHERE {' AND '.join(where)}
        GROUP BY CHANNEL
        ORDER BY TOTAL_SPEND DESC
    """
    return query_to_dicts(sql)


@router.get("/unified-measurement")
def get_unified_measurement(
    exclude_channels: str | None = Query(None),
    date_start: str | None = Query(None),
    date_end: str | None = Query(None),
):
    mta_where = ["MODEL_TYPE = 'linear'"]
    ch = build_channel_filter(exclude_channels)
    if ch:
        mta_where.append(ch)
    mta_where.extend(build_date_filter(date_start, date_end, "CONVERSION_TIMESTAMP"))

    mmm_where = ["1=1"]
    if ch:
        mmm_where.append(ch)
    mmm_where.extend(build_date_filter(date_start, date_end, "WEEK_START"))

    mta = query_to_dicts(f"""
        SELECT CHANNEL,
               SUM(ATTRIBUTED_REVENUE) AS MTA_REVENUE,
               COUNT(DISTINCT CONVERSION_ID) AS MTA_CONVERSIONS
        FROM MTA_DEMO.ANALYTICS.ATTRIBUTION_RESULTS
        WHERE {' AND '.join(mta_where)}
        GROUP BY CHANNEL
    """)
    mmm = query_to_dicts(f"""
        SELECT CHANNEL,
               SUM(SPEND) AS TOTAL_SPEND,
               SUM(ATTRIBUTED_REVENUE) AS TOTAL_REVENUE,
               CASE WHEN SUM(SPEND) > 0 THEN SUM(ATTRIBUTED_REVENUE) / SUM(SPEND) ELSE 0 END AS MMM_ROAS
        FROM MTA_DEMO.ANALYTICS.MMM_INPUT_WEEKLY
        WHERE {' AND '.join(mmm_where)}
        GROUP BY CHANNEL
    """)
    incr = query_to_dicts("SELECT * FROM MTA_DEMO.ANALYTICS.INCREMENTALITY_RESULTS")
    return {"mta": mta, "mmm": mmm, "incrementality": incr}


@router.get("/mmm-coefficients")
def get_mmm_coefficients(exclude_channels: str | None = Query(None)):
    where = ["1=1"]
    ch = build_channel_filter(exclude_channels)
    if ch:
        where.append(ch)
    return query_to_dicts(f"""
        SELECT * FROM MTA_DEMO.ANALYTICS.MMM_COEFFICIENTS
        WHERE {' AND '.join(where)}
        ORDER BY R_SQUARED DESC
    """)


@router.get("/mmm-response-curves")
def get_response_curves(exclude_channels: str | None = Query(None)):
    where = ["1=1"]
    ch = build_channel_filter(exclude_channels)
    if ch:
        where.append(ch)
    return query_to_dicts(f"""
        SELECT * FROM MTA_DEMO.ANALYTICS.MMM_RESPONSE_CURVES
        WHERE {' AND '.join(where)}
        ORDER BY CHANNEL, SPEND
    """)
