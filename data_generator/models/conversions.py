import numpy as np
from datetime import timedelta
from data_generator.config import (
    SEED, CONVERSION_TYPES, TRIPLE_FIRE_RATE, CONVERSION_SOURCE_PRIORITY,
    ADVERTISERS, VERTICAL_CONVERSION_RATES, CONSENT_EFFECTS,
    POPULATION_SEGMENTS, apply_jitter
)


def generate_conversions(clicks, sessions, people_lookup, seed=SEED):
    rng = np.random.default_rng(seed + 50)

    conv_types = list(CONVERSION_TYPES.keys())
    conv_probs = np.array([CONVERSION_TYPES[c]["share"] for c in conv_types])
    conv_probs /= conv_probs.sum()

    raw_conversions = []
    conv_counter = 0

    converter_clicks = [
        c for c in clicks
        if people_lookup.get(c["person_id"], {}).get("segment") == "converter"
    ]

    for click in converter_clicks:
        person = people_lookup.get(click["person_id"])
        if not person:
            continue

        consent = person["consent_status"]
        if not CONSENT_EFFECTS[consent]["conversion_track"]:
            continue

        adv = ADVERTISERS.get(click["advertiser_id"], {})
        vertical = adv.get("vertical", "retail")
        base_conv_rate = VERTICAL_CONVERSION_RATES.get(vertical, 0.01)
        adj_rate = apply_jitter(base_conv_rate * 3.8)

        if rng.random() >= adj_rate:
            continue

        conv_type = rng.choice(conv_types, p=conv_probs)
        value_mult = CONVERSION_TYPES[conv_type]["value_multiplier"]
        base_value = adv.get("conversion_value_avg", 50.0)
        conv_value = round(apply_jitter(base_value * value_mult, 0.20), 2)

        delay_hours = max(0.1, float(rng.lognormal(2.5, 1.4)))
        conv_ts = click["timestamp"] + timedelta(hours=delay_hours)

        conv_counter += 1
        base_conv = {
            "person_id": click["person_id"],
            "cookie_id": click["cookie_id"],
            "device_type": click["device_type"],
            "campaign_id": click["campaign_id"],
            "advertiser_id": click["advertiser_id"],
            "conversion_type": conv_type,
            "conversion_value": conv_value,
            "conversion_timestamp": conv_ts,
            "triggering_click_id": click["click_id"],
        }

        is_triple_fire = rng.random() < TRIPLE_FIRE_RATE
        if is_triple_fire:
            for i, source in enumerate(CONVERSION_SOURCE_PRIORITY):
                conv_counter += 1
                jitter_ms = int(rng.integers(-2000, 2000))
                source_ts = conv_ts + timedelta(milliseconds=jitter_ms * (i + 1))
                raw_conversions.append({
                    **base_conv,
                    "conversion_id": f"CONV_{conv_counter:010d}",
                    "conversion_timestamp": source_ts,
                    "conversion_source": source,
                    "is_duplicate": i > 0,
                })
        else:
            source = rng.choice(CONVERSION_SOURCE_PRIORITY, p=[0.487, 0.318, 0.195])
            conv_counter += 1
            raw_conversions.append({
                **base_conv,
                "conversion_id": f"CONV_{conv_counter:010d}",
                "conversion_source": source,
                "is_duplicate": False,
            })

    store_visitor_sessions = [
        s for s in sessions
        if people_lookup.get(s["person_id"], {}).get("segment") == "store_visitor"
        and s["duration_seconds"] > 30
    ]
    for sess in store_visitor_sessions:
        if rng.random() < apply_jitter(0.12):
            person = people_lookup.get(sess["person_id"])
            if not person or not CONSENT_EFFECTS[person["consent_status"]]["conversion_track"]:
                continue

            adv = ADVERTISERS.get(sess["advertiser_id"], {})
            conv_counter += 1
            raw_conversions.append({
                "conversion_id": f"CONV_{conv_counter:010d}",
                "person_id": sess["person_id"],
                "cookie_id": sess["cookie_id"],
                "device_type": sess["device_type"],
                "campaign_id": sess["campaign_id"],
                "advertiser_id": sess["advertiser_id"],
                "conversion_type": "store_locator",
                "conversion_value": round(apply_jitter(adv.get("conversion_value_avg", 50.0) * 0.08, 0.20), 2),
                "conversion_timestamp": sess["timestamp"] + timedelta(hours=float(rng.lognormal(3.0, 1.0))),
                "triggering_click_id": sess.get("click_id"),
                "conversion_source": rng.choice(CONVERSION_SOURCE_PRIORITY, p=[0.487, 0.318, 0.195]),
                "is_duplicate": False,
            })

    return raw_conversions
