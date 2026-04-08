from fastapi import APIRouter, Query
from db import query_to_dicts
from filters import build_channel_filter, build_date_filter

router = APIRouter(prefix="/api/v1", tags=["attribution"])


@router.get("/attribution")
def get_attribution(
    advertiser_id: str | None = Query(None),
    models: str | None = Query(None),
    exclude_channels: str | None = Query(None),
    date_start: str | None = Query(None),
    date_end: str | None = Query(None),
):
    where = ["1=1"]
    if advertiser_id:
        where.append(f"ADVERTISER_ID = '{advertiser_id}'")
    if models:
        model_list = ",".join([f"'{m.strip()}'" for m in models.split(",")])
        where.append(f"MODEL_TYPE IN ({model_list})")
    ch = build_channel_filter(exclude_channels)
    if ch:
        where.append(ch)
    where.extend(build_date_filter(date_start, date_end, "CONVERSION_TIMESTAMP"))

    sql = f"""
        SELECT MODEL_TYPE, CHANNEL,
               SUM(ATTRIBUTED_REVENUE) AS REVENUE,
               SUM(ATTRIBUTION_WEIGHT) AS CONVERSIONS
        FROM MTA_DEMO.ANALYTICS.ATTRIBUTION_RESULTS
        WHERE {' AND '.join(where)}
        GROUP BY 1, 2
        ORDER BY 1, REVENUE DESC
    """
    return query_to_dicts(sql)


@router.get("/attribution/advertisers")
def get_advertisers():
    return query_to_dicts(
        "SELECT DISTINCT ADVERTISER_ID FROM MTA_DEMO.ANALYTICS.ATTRIBUTION_RESULTS ORDER BY 1"
    )
