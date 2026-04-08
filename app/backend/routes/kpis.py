from fastapi import APIRouter, Query
from db import query_to_dicts

router = APIRouter(prefix="/api/v1", tags=["kpis"])


@router.get("/kpis")
def get_kpis():
    total_imps = query_to_dicts("SELECT COUNT(*) AS cnt FROM MTA_DEMO.STAGING.STG_IMPRESSIONS")
    match_rate = query_to_dicts("""
        SELECT ROUND(AVG(CASE WHEN RESOLUTION_METHOD = 'device_graph' THEN 1.0 ELSE 0.0 END), 4) AS rate
        FROM MTA_DEMO.STAGING.STG_IDENTITY_RESOLVED
    """)
    itp_rate = query_to_dicts("""
        SELECT ROUND(AVG(CASE WHEN COOKIE_RELIABILITY = 'itp_rotated' THEN 1.0 ELSE 0.0 END), 4) AS rate
        FROM MTA_DEMO.STAGING.STG_IMPRESSIONS
    """)
    consent_block = query_to_dicts("""
        SELECT ROUND(AVG(CASE WHEN IS_TRACKABLE = FALSE THEN 1.0 ELSE 0.0 END), 4) AS rate
        FROM MTA_DEMO.STAGING.STG_IMPRESSIONS
    """)
    total_clicks = query_to_dicts("SELECT COUNT(*) AS cnt FROM MTA_DEMO.STAGING.STG_CLICKS")
    total_conversions = query_to_dicts("SELECT COUNT(*) AS cnt FROM MTA_DEMO.STAGING.STG_CONVERSIONS_DEDUPED")
    total_spend = query_to_dicts("SELECT ROUND(SUM(CPM / 1000.0), 2) AS spend FROM MTA_DEMO.STAGING.STG_IMPRESSIONS")
    total_revenue = query_to_dicts("""
        SELECT ROUND(SUM(ATTRIBUTED_REVENUE), 2) AS revenue
        FROM MTA_DEMO.ANALYTICS.ATTRIBUTION_RESULTS
        WHERE MODEL_TYPE = 'linear'
    """)

    return {
        "total_impressions": total_imps[0]["CNT"],
        "total_clicks": total_clicks[0]["CNT"],
        "total_conversions": total_conversions[0]["CNT"],
        "total_spend": float(total_spend[0]["SPEND"] or 0),
        "total_revenue": float(total_revenue[0]["REVENUE"] or 0),
        "identity_match_rate": float(match_rate[0]["RATE"] or 0),
        "itp_affected_rate": float(itp_rate[0]["RATE"] or 0),
        "consent_blocked_rate": float(consent_block[0]["RATE"] or 0),
    }


@router.get("/population")
def get_population():
    rows = query_to_dicts("""
        SELECT "segment" AS SEGMENT, COUNT(*) AS PEOPLE,
               ROUND(COUNT(*)::FLOAT / SUM(COUNT(*)) OVER (), 4) AS SHARE
        FROM MTA_DEMO.RAW.PEOPLE
        GROUP BY "segment" ORDER BY PEOPLE DESC
    """)
    return rows


@router.get("/dedup-report")
def get_dedup_report():
    return query_to_dicts("SELECT * FROM MTA_DEMO.ANALYTICS.CONVERSION_DEDUP_REPORT")
