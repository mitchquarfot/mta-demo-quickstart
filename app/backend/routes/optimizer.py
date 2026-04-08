from fastapi import APIRouter, Query
from db import query_to_dicts
from filters import build_channel_filter
import math

router = APIRouter(prefix="/api/v1", tags=["optimizer"])


def _response_fn(spend: float, alpha: float, beta: float) -> float:
    if spend <= 0:
        return 0.0
    return math.exp(alpha + beta * math.log(spend + 1)) - 1


def _marginal_response(spend: float, alpha: float, beta: float) -> float:
    if spend <= 0:
        return beta * math.exp(alpha)
    return beta * math.exp(alpha + beta * math.log(spend + 1)) / (spend + 1)


@router.post("/optimize-budget")
def optimize_budget(payload: dict):
    total_budget = float(payload.get("total_budget", 0))
    exclude = payload.get("exclude_channels", "")
    where = ["1=1"]
    ch = build_channel_filter(exclude)
    if ch:
        where.append(ch)
    coefficients = query_to_dicts(
        f"SELECT CHANNEL, ALPHA, BETA, AVG_WEEKLY_SPEND FROM MTA_DEMO.ANALYTICS.MMM_COEFFICIENTS WHERE {' AND '.join(where)}"
    )
    if not coefficients or total_budget <= 0:
        return {"error": "No coefficients or invalid budget"}

    channels = [c["CHANNEL"] for c in coefficients]
    alphas = {c["CHANNEL"]: float(c["ALPHA"]) for c in coefficients}
    betas = {c["CHANNEL"]: float(c["BETA"]) for c in coefficients}
    n = len(channels)

    allocation = {ch: total_budget / n for ch in channels}

    for _ in range(200):
        marginals = {ch: _marginal_response(allocation[ch], alphas[ch], betas[ch]) for ch in channels}
        best = max(marginals, key=marginals.get)
        worst = min(marginals, key=marginals.get)
        if marginals[best] - marginals[worst] < 0.001:
            break
        step = total_budget * 0.01
        if allocation[worst] >= step:
            allocation[worst] -= step
            allocation[best] += step

    results = []
    for ch in channels:
        spend = round(allocation[ch], 2)
        rev = round(_response_fn(spend, alphas[ch], betas[ch]), 2)
        results.append({
            "channel": ch,
            "optimized_spend": spend,
            "predicted_revenue": rev,
            "roas": round(rev / spend, 4) if spend > 0 else 0,
        })

    total_rev = sum(r["predicted_revenue"] for r in results)
    return {
        "total_budget": total_budget,
        "total_predicted_revenue": round(total_rev, 2),
        "overall_roas": round(total_rev / total_budget, 4) if total_budget > 0 else 0,
        "allocations": sorted(results, key=lambda x: x["optimized_spend"], reverse=True),
    }


@router.get("/current-allocation")
def get_current_allocation(exclude_channels: str | None = Query(None)):
    where = ["1=1"]
    ch = build_channel_filter(exclude_channels)
    if ch:
        where.append(ch)
    return query_to_dicts(f"""
        SELECT CHANNEL, TOTAL_SPEND, TOTAL_REVENUE, AVG_WEEKLY_SPEND, AVG_WEEKLY_REVENUE, ROAS
        FROM MTA_DEMO.ANALYTICS.MMM_COEFFICIENTS
        WHERE {' AND '.join(where)}
        ORDER BY TOTAL_SPEND DESC
    """)
