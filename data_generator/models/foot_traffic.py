import numpy as np
from datetime import timedelta
from data_generator.config import (
    SEED, TARGET_FOOT_TRAFFIC, GEO_HOLDOUT, ADVERTISERS,
    apply_jitter, DATE_START
)


def generate_foot_traffic(people, impressions_flat, seed=SEED):
    rng = np.random.default_rng(seed + 60)

    store_visitors = [p for p in people if p["segment"] == "store_visitor"]
    if not store_visitors:
        return []

    control_dma_codes = set(d["code"] for d in GEO_HOLDOUT["control_dmas"])
    treatment_dma_codes = set(d["code"] for d in GEO_HOLDOUT["treatment_dmas"])
    holdout_start = GEO_HOLDOUT["holdout_start_day"]
    holdout_end = holdout_start + GEO_HOLDOUT["holdout_duration_days"]

    exposed_visitors = {}
    for imp in impressions_flat:
        pid = imp["person_id"]
        if pid not in exposed_visitors:
            exposed_visitors[pid] = []
        exposed_visitors[pid].append(imp)

    records = []
    visit_counter = 0
    target_per_visitor = TARGET_FOOT_TRAFFIC / max(len(store_visitors), 1)

    for person in store_visitors:
        n_visits = max(1, int(rng.poisson(apply_jitter(target_per_visitor))))
        person_imps = exposed_visitors.get(person["person_id"], [])

        for _ in range(n_visits):
            visit_counter += 1

            if person_imps and rng.random() < 0.67:
                ref_imp = rng.choice(person_imps)
                delay_hours = max(1, float(rng.lognormal(3.5, 1.2)))
                visit_ts = ref_imp["timestamp"] + timedelta(hours=delay_hours)
                triggered_campaign = ref_imp["campaign_id"]
                triggered_advertiser = ref_imp["advertiser_id"]
            else:
                day_offset = int(rng.integers(0, 365))
                visit_ts = DATE_START + timedelta(days=day_offset, hours=int(rng.integers(8, 21)), minutes=int(rng.integers(0, 60)))
                triggered_campaign = None
                triggered_advertiser = rng.choice(list(ADVERTISERS.keys()))

            is_in_holdout = (
                person["dma_code"] in control_dma_codes
                and holdout_start <= (visit_ts - DATE_START).days < holdout_end
            )
            is_in_treatment = (
                person["dma_code"] in treatment_dma_codes
                and holdout_start <= (visit_ts - DATE_START).days < holdout_end
            )

            if is_in_holdout:
                lift_reduction = apply_jitter(GEO_HOLDOUT["expected_lift"])
                if rng.random() < lift_reduction:
                    continue

            dwell_minutes = max(1, int(rng.lognormal(2.3, 0.8)))

            records.append({
                "visit_id": f"VISIT_{visit_counter:08d}",
                "person_id": person["person_id"],
                "visit_timestamp": visit_ts,
                "dma_code": person["dma_code"],
                "dma_name": person["dma_name"],
                "dwell_time_minutes": dwell_minutes,
                "campaign_id": triggered_campaign,
                "advertiser_id": triggered_advertiser,
                "is_holdout_geo": is_in_holdout,
                "is_treatment_geo": is_in_treatment,
                "visit_source": rng.choice(["observed_wifi", "gps_signal", "beacon"], p=[0.437, 0.389, 0.174]),
            })

    return records
