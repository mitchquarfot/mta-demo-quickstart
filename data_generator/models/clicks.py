import numpy as np
import pandas as pd
from datetime import timedelta
from data_generator.config import (
    SEED, CHANNEL_CONFIG, CONSENT_EFFECTS, POPULATION_SEGMENTS,
    TRIPLE_FIRE_RATE, CONVERSION_SOURCE_PRIORITY,
    ADVERTISERS, VERTICAL_CONVERSION_RATES, CONVERSION_TYPES,
    TARGET_FOOT_TRAFFIC, GEO_HOLDOUT, DATE_START, apply_jitter,
    CHANNEL_MATCH_RATES
)


def generate_clicks(impressions, people_lookup, seed=SEED):
    rng = np.random.default_rng(seed + 20)
    df = impressions if isinstance(impressions, pd.DataFrame) else pd.DataFrame(impressions)

    df["ctr"] = df["channel"].map(lambda ch: CHANNEL_CONFIG[ch]["ctr"])
    df = df[df["ctr"] > 0].copy()

    df["seg"] = df["person_id"].map(lambda pid: people_lookup.get(pid, {}).get("segment", "passive_exposed"))
    df["seg_prop"] = df["seg"].map(lambda s: POPULATION_SEGMENTS.get(s, {}).get("click_propensity", 0.006))
    df["adj_ctr"] = df["ctr"] * (df["seg_prop"] / 0.3) * rng.uniform(0.975, 1.025, size=len(df))

    rolls = rng.random(len(df))
    clicked = df[rolls < df["adj_ctr"]].copy()

    delays = rng.exponential(2.4, size=len(clicked)).astype(int)
    clicked["click_timestamp"] = clicked["timestamp"] + pd.to_timedelta(delays, unit="s")

    clicked = clicked.reset_index(drop=True)
    clicked["click_id"] = [f"CLK_{i+1:010d}" for i in range(len(clicked))]
    clicked["landing_page"] = clicked.apply(
        lambda r: f"https://www.{r['advertiser_name'].lower().replace(' ', '')}.com/lp/{r['campaign_id'].lower()}", axis=1
    )

    result = clicked[["click_id", "impression_id", "click_timestamp", "person_id",
                       "cookie_id", "device_type", "browser", "channel", "campaign_id",
                       "campaign_name", "advertiser_id", "advertiser_name",
                       "creative_id", "dma_code", "consent_status", "landing_page"]].copy()
    result = result.rename(columns={"click_timestamp": "timestamp"})

    return result.to_dict("records")


def generate_pixel_fires(clicks, people_lookup, seed=SEED):
    rng = np.random.default_rng(seed + 30)
    df = pd.DataFrame(clicks)
    if df.empty:
        return []

    df["consent"] = df["person_id"].map(lambda pid: people_lookup.get(pid, {}).get("consent_status", "rejected_all"))
    df["can_fire"] = df["consent"].map(lambda c: CONSENT_EFFECTS.get(c, {}).get("pixel_fire", False))
    df = df[df["can_fire"]].copy()

    fire_roll = rng.random(len(df))
    fired = df[fire_roll < 0.72].copy()

    delays = rng.exponential(1.8, size=len(fired)).astype(int)
    fired["fire_ts"] = pd.to_datetime(fired["timestamp"]) + pd.to_timedelta(delays, unit="s")

    event_types = rng.choice(
        ["pageview", "button_click", "form_start", "scroll_depth"],
        size=len(fired), p=[0.52, 0.23, 0.14, 0.11]
    )

    records = []
    counter = 0
    for _, row in fired.iterrows():
        counter += 1
        records.append({
            "pixel_fire_id": f"PXL_{counter:010d}",
            "click_id": row["click_id"],
            "impression_id": row.get("impression_id"),
            "timestamp": row["fire_ts"],
            "person_id": row["person_id"],
            "cookie_id": row["cookie_id"],
            "device_type": row["device_type"],
            "campaign_id": row["campaign_id"],
            "advertiser_id": row["advertiser_id"],
            "consent_status": row.get("consent", row.get("consent_status")),
            "pixel_source": "gtm",
            "page_url": row["landing_page"],
            "event_type": event_types[counter - 1] if counter - 1 < len(event_types) else "pageview",
        })

    return records


def generate_sessions(clicks, people_lookup, seed=SEED):
    rng = np.random.default_rng(seed + 40)
    df = pd.DataFrame(clicks)
    if df.empty:
        return []

    df["consent"] = df["person_id"].map(lambda pid: people_lookup.get(pid, {}).get("consent_status", "rejected_all"))
    df["can_track"] = df["consent"].map(lambda c: CONSENT_EFFECTS.get(c, {}).get("session_track", False))
    df = df[df["can_track"]].copy()

    session_roll = rng.random(len(df))
    sessioned = df[session_roll < 0.83].copy()

    durations = np.maximum(1, rng.lognormal(4.2, 1.3, size=len(sessioned)).astype(int))
    pages = np.maximum(1, rng.lognormal(0.8, 0.7, size=len(sessioned)).astype(int))

    records = []
    counter = 0
    for idx, (_, row) in enumerate(sessioned.iterrows()):
        counter += 1
        d = int(durations[idx])
        p = int(pages[idx])
        records.append({
            "session_id": f"SESS_{counter:010d}",
            "click_id": row["click_id"],
            "timestamp": row["timestamp"],
            "person_id": row["person_id"],
            "cookie_id": row["cookie_id"],
            "device_type": row["device_type"],
            "browser": row.get("browser", "unknown"),
            "campaign_id": row["campaign_id"],
            "advertiser_id": row["advertiser_id"],
            "consent_status": row.get("consent", row.get("consent_status")),
            "session_source": "ga4",
            "landing_page": row["landing_page"],
            "duration_seconds": d,
            "pages_viewed": p,
            "is_bounce": p == 1 and d < 10,
        })

    return records


def generate_conversions(clicks, sessions, people_lookup, seed=SEED):
    rng = np.random.default_rng(seed + 50)

    conv_types = list(CONVERSION_TYPES.keys())
    conv_probs = np.array([CONVERSION_TYPES[c]["share"] for c in conv_types])
    conv_probs /= conv_probs.sum()

    df = pd.DataFrame(clicks)
    if df.empty:
        return []

    df["seg"] = df["person_id"].map(lambda pid: people_lookup.get(pid, {}).get("segment", "passive_exposed"))
    df["consent"] = df["person_id"].map(lambda pid: people_lookup.get(pid, {}).get("consent_status", "rejected_all"))
    df["can_convert"] = df["consent"].map(lambda c: CONSENT_EFFECTS.get(c, {}).get("conversion_track", False))

    converter_clicks = df[(df["seg"] == "converter") & (df["can_convert"])].copy()

    def get_vert(aid):
        return ADVERTISERS.get(aid, {}).get("vertical", "retail")

    converter_clicks["vertical"] = converter_clicks["advertiser_id"].map(get_vert)
    converter_clicks["base_rate"] = converter_clicks["vertical"].map(
        lambda v: VERTICAL_CONVERSION_RATES.get(v, 0.01) * 3.8
    )
    converter_clicks["adj_rate"] = converter_clicks["base_rate"] * rng.uniform(0.975, 1.025, size=len(converter_clicks))

    rolls = rng.random(len(converter_clicks))
    converting = converter_clicks[rolls < converter_clicks["adj_rate"]].copy()

    records = []
    counter = 0

    for _, row in converting.iterrows():
        ct = rng.choice(conv_types, p=conv_probs)
        val_mult = CONVERSION_TYPES[ct]["value_multiplier"]
        base_val = ADVERTISERS.get(row["advertiser_id"], {}).get("conversion_value_avg", 50.0)
        conv_val = round(base_val * val_mult * rng.uniform(0.8, 1.2), 2)

        delay_h = max(0.1, float(rng.lognormal(2.5, 1.4)))
        conv_ts = pd.Timestamp(row["timestamp"]) + pd.Timedelta(hours=delay_h)

        is_triple = rng.random() < TRIPLE_FIRE_RATE
        if is_triple:
            for j, src in enumerate(CONVERSION_SOURCE_PRIORITY):
                counter += 1
                jitter_ms = int(rng.integers(-2000, 2000))
                src_ts = conv_ts + pd.Timedelta(milliseconds=jitter_ms * (j + 1))
                records.append({
                    "conversion_id": f"CONV_{counter:010d}",
                    "person_id": row["person_id"],
                    "cookie_id": row["cookie_id"],
                    "device_type": row["device_type"],
                    "campaign_id": row["campaign_id"],
                    "advertiser_id": row["advertiser_id"],
                    "conversion_type": ct,
                    "conversion_value": conv_val,
                    "conversion_timestamp": src_ts,
                    "triggering_click_id": row["click_id"],
                    "conversion_source": src,
                    "is_duplicate": j > 0,
                    "consent_status": row.get("consent", row.get("consent_status")),
                })
        else:
            src = rng.choice(CONVERSION_SOURCE_PRIORITY, p=[0.487, 0.318, 0.195])
            counter += 1
            records.append({
                "conversion_id": f"CONV_{counter:010d}",
                "person_id": row["person_id"],
                "cookie_id": row["cookie_id"],
                "device_type": row["device_type"],
                "campaign_id": row["campaign_id"],
                "advertiser_id": row["advertiser_id"],
                "conversion_type": ct,
                "conversion_value": conv_val,
                "conversion_timestamp": conv_ts,
                "triggering_click_id": row["click_id"],
                "conversion_source": src,
                "is_duplicate": False,
                "consent_status": row.get("consent", row.get("consent_status")),
            })

    return records


def generate_view_through_conversions(impressions, people_lookup, existing_converters, seed=SEED):
    rng = np.random.default_rng(seed + 55)

    conv_types = list(CONVERSION_TYPES.keys())
    conv_probs = np.array([CONVERSION_TYPES[c]["share"] for c in conv_types])
    conv_probs /= conv_probs.sum()

    df = impressions if isinstance(impressions, pd.DataFrame) else pd.DataFrame(impressions)
    if df.empty:
        return []

    vt_channels = {ch: cfg["view_through_rate"] for ch, cfg in CHANNEL_CONFIG.items() if cfg.get("view_through_rate", 0) > 0}
    df = df[df["channel"].isin(vt_channels)].copy()
    if df.empty:
        return []

    df["vt_rate"] = df["channel"].map(vt_channels)
    df["seg"] = df["person_id"].map(lambda pid: people_lookup.get(pid, {}).get("segment", "passive_exposed"))
    df["consent"] = df["person_id"].map(lambda pid: people_lookup.get(pid, {}).get("consent_status", "rejected_all"))
    df["can_convert"] = df["consent"].map(lambda c: CONSENT_EFFECTS.get(c, {}).get("conversion_track", False))
    df["match_rate"] = df["channel"].map(lambda ch: CHANNEL_MATCH_RATES.get(ch, 0))

    eligible = df[
        (df["seg"].isin(["converter", "engager"]))
        & (df["can_convert"])
    ].copy()

    if eligible.empty:
        return []

    seg_multiplier = eligible["seg"].map({"converter": 1.0, "engager": 0.15}).values
    def get_vert(aid):
        return ADVERTISERS.get(aid, {}).get("vertical", "retail")
    eligible["vertical"] = eligible["advertiser_id"].map(get_vert)
    eligible["vert_rate"] = eligible["vertical"].map(
        lambda v: VERTICAL_CONVERSION_RATES.get(v, 0.01)
    )

    awareness_boost = eligible["channel"].map({"ctv": 2.5, "olv": 1.8, "audio": 1.3}).fillna(1.0).values
    eligible["conv_prob"] = eligible["vt_rate"] * eligible["vert_rate"] * seg_multiplier * eligible["match_rate"] * 8.0 * awareness_boost

    rolls = rng.random(len(eligible))
    converting = eligible[rolls < eligible["conv_prob"]].copy()

    already_converted_people = set(existing_converters)
    vt_converted = set()

    records = []
    counter = 0

    for _, row in converting.iterrows():
        pid = row["person_id"]
        adv = row["advertiser_id"]
        key = (pid, adv)
        if key in already_converted_people or key in vt_converted:
            continue
        vt_converted.add(key)

        ct = rng.choice(conv_types, p=conv_probs)
        val_mult = CONVERSION_TYPES[ct]["value_multiplier"]
        base_val = ADVERTISERS.get(adv, {}).get("conversion_value_avg", 50.0)
        conv_val = round(base_val * val_mult * rng.uniform(0.8, 1.2), 2)

        delay_h = max(2.0, float(rng.lognormal(3.5, 1.0)))
        conv_ts = pd.Timestamp(row["timestamp"]) + pd.Timedelta(hours=delay_h)

        is_triple = rng.random() < TRIPLE_FIRE_RATE
        if is_triple:
            for j, src in enumerate(CONVERSION_SOURCE_PRIORITY):
                counter += 1
                jitter_ms = int(rng.integers(-2000, 2000))
                src_ts = conv_ts + pd.Timedelta(milliseconds=jitter_ms * (j + 1))
                records.append({
                    "conversion_id": f"VTC_{counter:010d}",
                    "person_id": pid,
                    "cookie_id": row["cookie_id"],
                    "device_type": row["device_type"],
                    "campaign_id": row["campaign_id"],
                    "advertiser_id": adv,
                    "conversion_type": ct,
                    "conversion_value": conv_val,
                    "conversion_timestamp": src_ts,
                    "triggering_click_id": None,
                    "triggering_impression_id": row["impression_id"],
                    "conversion_source": src,
                    "is_duplicate": j > 0,
                    "consent_status": row.get("consent", row.get("consent_status")),
                    "is_view_through": True,
                    "view_through_channel": row["channel"],
                })
        else:
            src = rng.choice(CONVERSION_SOURCE_PRIORITY, p=[0.487, 0.318, 0.195])
            counter += 1
            records.append({
                "conversion_id": f"VTC_{counter:010d}",
                "person_id": pid,
                "cookie_id": row["cookie_id"],
                "device_type": row["device_type"],
                "campaign_id": row["campaign_id"],
                "advertiser_id": adv,
                "conversion_type": ct,
                "conversion_value": conv_val,
                "conversion_timestamp": conv_ts,
                "triggering_click_id": None,
                "triggering_impression_id": row["impression_id"],
                "conversion_source": src,
                "is_duplicate": False,
                "consent_status": row.get("consent", row.get("consent_status")),
                "is_view_through": True,
                "view_through_channel": row["channel"],
            })

    return records


def generate_foot_traffic(people, exposure_data, seed=SEED):
    rng = np.random.default_rng(seed + 60)

    store_visitors = [p for p in people if p["segment"] == "store_visitor"]
    if not store_visitors:
        return []

    control_dma_codes = set(d["code"] for d in GEO_HOLDOUT["control_dmas"])
    treatment_dma_codes = set(d["code"] for d in GEO_HOLDOUT["treatment_dmas"])
    holdout_start = GEO_HOLDOUT["holdout_start_day"]
    holdout_end = holdout_start + GEO_HOLDOUT["holdout_duration_days"]

    exposed_by_person = {}
    source_data = exposure_data if isinstance(exposure_data, list) else exposure_data.to_dict("records") if hasattr(exposure_data, "to_dict") else exposure_data
    for rec in source_data:
        pid = rec["person_id"]
        if pid not in exposed_by_person:
            exposed_by_person[pid] = []
        if len(exposed_by_person[pid]) < 5:
            exposed_by_person[pid].append(rec)

    records = []
    counter = 0
    target_per = TARGET_FOOT_TRAFFIC / max(len(store_visitors), 1)

    for person in store_visitors:
        n_visits = max(1, int(rng.poisson(target_per)))
        p_imps = exposed_by_person.get(person["person_id"], [])

        for _ in range(n_visits):
            counter += 1
            if p_imps and rng.random() < 0.67:
                ref = rng.choice(p_imps)
                delay_h = max(1, float(rng.lognormal(3.5, 1.2)))
                visit_ts = pd.Timestamp(ref["timestamp"]) + pd.Timedelta(hours=delay_h)
                cmp = ref["campaign_id"]
                adv = ref["advertiser_id"]
            else:
                day_off = int(rng.integers(0, 365))
                visit_ts = DATE_START + timedelta(days=day_off, hours=int(rng.integers(8, 21)))
                cmp = None
                adv = rng.choice(list(ADVERTISERS.keys()))

            day_of_year = (visit_ts - pd.Timestamp(DATE_START)).days if isinstance(visit_ts, pd.Timestamp) else (visit_ts - DATE_START).days
            is_holdout = person["dma_code"] in control_dma_codes and holdout_start <= day_of_year < holdout_end
            is_treatment = person["dma_code"] in treatment_dma_codes and holdout_start <= day_of_year < holdout_end

            if is_holdout and rng.random() < GEO_HOLDOUT["expected_lift"]:
                continue

            records.append({
                "visit_id": f"VISIT_{counter:08d}",
                "person_id": person["person_id"],
                "visit_timestamp": visit_ts,
                "dma_code": person["dma_code"],
                "dma_name": person["dma_name"],
                "dwell_time_minutes": max(1, int(rng.lognormal(2.3, 0.8))),
                "campaign_id": cmp,
                "advertiser_id": adv,
                "is_holdout_geo": is_holdout,
                "is_treatment_geo": is_treatment,
                "visit_source": rng.choice(["observed_wifi", "gps_signal", "beacon"], p=[0.437, 0.389, 0.174]),
            })

    return records
