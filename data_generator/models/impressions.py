import numpy as np
import pandas as pd
import uuid
from datetime import timedelta
from data_generator.config import (
    SEED, TARGET_IMPRESSIONS, DATE_START, NUM_DAYS,
    CHANNEL_CONFIG, CAMPAIGNS, CREATIVE_TEMPLATES, ADVERTISERS,
    HOUR_DISTRIBUTION, DAYOFWEEK_MODIFIERS, SEASONALITY_MONTHLY,
    ITP_CONFIG, GEO_HOLDOUT, POPULATION_SEGMENTS,
    CAMPAIGN_ARC_TYPES, JITTER_PCT
)
import math

def generate_impressions(people_list, campaigns, seed=SEED):
    rng = np.random.default_rng(seed + 10)
    print("    Building fully vectorized impressions...")

    people = pd.DataFrame(people_list)
    n_people = len(people)

    control_dma_codes = set(d["code"] for d in GEO_HOLDOUT["control_dmas"])
    holdout_start = GEO_HOLDOUT["holdout_start_day"]
    holdout_end = holdout_start + GEO_HOLDOUT["holdout_duration_days"]
    itp_browsers = set(ITP_CONFIG["affected_browsers"])

    hour_probs = np.array(HOUR_DISTRIBUTION, dtype=np.float64)
    hour_probs /= hour_probs.sum()

    seg_idx = {s: people.index[people["segment"] == s].values for s in POPULATION_SEGMENTS}

    all_dfs = []

    for cmp in campaigns:
        adv = ADVERTISERS[cmp["advertiser"]]
        channels = cmp["channel_mix"]
        budget_share = cmp.get("budget_share", 0.1)
        n_target = max(int(TARGET_IMPRESSIONS * budget_share * 0.8), 500)

        pool = np.concatenate([
            rng.choice(seg_idx.get("converter", np.array([])), size=min(int(len(seg_idx.get("converter", [])) * 0.15), len(seg_idx.get("converter", []))), replace=False) if len(seg_idx.get("converter", [])) > 0 else np.array([], dtype=int),
            rng.choice(seg_idx.get("store_visitor", np.array([])), size=min(int(len(seg_idx.get("store_visitor", [])) * 0.12), len(seg_idx.get("store_visitor", []))), replace=False) if len(seg_idx.get("store_visitor", [])) > 0 else np.array([], dtype=int),
            rng.choice(seg_idx.get("engager", np.array([])), size=min(int(len(seg_idx.get("engager", [])) * 0.08), len(seg_idx.get("engager", []))), replace=False) if len(seg_idx.get("engager", [])) > 0 else np.array([], dtype=int),
            rng.choice(seg_idx.get("passive_exposed", np.array([])), size=min(int(len(seg_idx.get("passive_exposed", [])) * 0.03), len(seg_idx.get("passive_exposed", []))), replace=False) if len(seg_idx.get("passive_exposed", [])) > 0 else np.array([], dtype=int),
        ]).astype(int)

        if len(pool) == 0:
            continue

        pidx = rng.choice(pool, size=n_target, replace=True)
        days = rng.integers(cmp["start_day"], cmp["end_day"] + 1, size=n_target)
        channel_arr = rng.choice(channels, size=n_target)

        arc_fn = CAMPAIGN_ARC_TYPES[cmp["arc"]]["daily_modifier"]
        duration = max(cmp["end_day"] - cmp["start_day"], 1)
        day_pcts = (days - cmp["start_day"]) / duration

        base_dates = np.array([(DATE_START + timedelta(days=int(d))) for d in days])
        months = np.array([dt.month - 1 for dt in base_dates])
        dows = np.array([dt.weekday() for dt in base_dates])

        campaign_mods = np.array([arc_fn(float(p)) for p in day_pcts]) * rng.uniform(1 - JITTER_PCT, 1 + JITTER_PCT, size=n_target)
        seasonal = np.array([SEASONALITY_MONTHLY[m] for m in months])
        dow_mod = np.array([DAYOFWEEK_MODIFIERS.get(int(d), 1.0) for d in dows])

        combined = campaign_mods * seasonal * dow_mod
        keep_prob = np.minimum(combined / 2.0, 1.0)
        keep = rng.random(n_target) < keep_prob

        dma_vals = people["dma_code"].values[pidx]
        holdout_channel = GEO_HOLDOUT["channel"]
        holdout = (
            (np.array([ch == holdout_channel for ch in channel_arr]))
            & np.isin(dma_vals, list(control_dma_codes))
            & (days >= holdout_start) & (days < holdout_end)
        )
        keep = keep & ~holdout

        idx_kept = np.where(keep)[0]
        n = len(idx_kept)
        if n == 0:
            continue

        p_idx = pidx[idx_kept]
        d_kept = days[idx_kept]
        ch_kept = channel_arr[idx_kept]

        hours = rng.choice(24, size=n, p=hour_probs)
        mins = rng.integers(0, 60, size=n)
        secs = rng.integers(0, 60, size=n)

        timestamps = pd.to_datetime([
            base_dates[idx_kept[i]].replace(hour=int(hours[i]), minute=int(mins[i]), second=int(secs[i]))
            for i in range(n)
        ])

        browser_vals = people["browser"].values[p_idx]
        is_itp = np.isin(browser_vals, list(itp_browsers))
        cookie_vals = people["cookie_id"].values[p_idx].copy()

        creative_ids = []
        creative_formats = []
        device_types = []
        cpms = []
        for i in range(n):
            ch = ch_kept[i]
            cfg = CHANNEL_CONFIG[ch]
            cr_list = CREATIVE_TEMPLATES.get(ch, ["default"])
            cr = rng.choice(cr_list)
            creative_formats.append(cr)
            creative_ids.append(f"CR_{cmp['id']}_{cr}")
            device_types.append(rng.choice(cfg["devices"]))
            cpms.append(round(cfg["cpm"] * rng.uniform(0.85, 1.15), 2))

        df = pd.DataFrame({
            "impression_id": [f"IMP_{i:012d}" for i in range(1, n + 1)],
            "timestamp": timestamps,
            "person_id": people["person_id"].values[p_idx],
            "cookie_id": cookie_vals,
            "device_type": device_types,
            "browser": browser_vals,
            "channel": ch_kept,
            "campaign_id": cmp["id"],
            "campaign_name": cmp["name"],
            "advertiser_id": cmp["advertiser"],
            "advertiser_name": adv["name"],
            "creative_id": creative_ids,
            "creative_format": creative_formats,
            "dma_code": people["dma_code"].values[p_idx],
            "dma_name": people["dma_name"].values[p_idx],
            "consent_status": people["consent_status"].values[p_idx],
            "is_itp_affected": is_itp,
            "in_holdout_geo": False,
            "cpm": cpms,
        })
        all_dfs.append(df)
        print(f"    Campaign {cmp['id']}: {sum(len(d) for d in all_dfs):,} cumulative ({n:,} kept)")

    if not all_dfs:
        return []

    result = pd.concat(all_dfs, ignore_index=True)
    result["impression_id"] = [f"IMP_{i:012d}" for i in range(1, len(result) + 1)]
    print(f"    Total impressions: {len(result):,}")
    return result
