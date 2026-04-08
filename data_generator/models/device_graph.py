import numpy as np
import uuid
from data_generator.config import (
    SEED, CHANNEL_MATCH_RATES, OVERALL_MATCH_RATE, ITP_CONFIG, apply_jitter
)

def generate_device_graph(people, seed=SEED):
    rng = np.random.default_rng(seed + 1)

    graph_people = [p for p in people if p["in_device_graph"]]

    records = []
    for p in graph_people:
        ramp_id = "RAMP_" + str(uuid.uuid4())[:12]

        records.append({
            "ramp_id": ramp_id,
            "identifier_type": "cookie",
            "identifier_value": p["cookie_id"],
            "device_type": p["primary_device"],
            "confidence_score": round(p["graph_confidence"], 4),
            "match_source": rng.choice(["deterministic", "probabilistic"], p=[0.623, 0.377]),
            "first_seen": None,
            "last_seen": None,
            "person_id": p["person_id"],
        })

        if p["secondary_device"]:
            secondary_match_prob = apply_jitter(0.481)
            if rng.random() < secondary_match_prob:
                secondary_id = str(uuid.uuid4())
                records.append({
                    "ramp_id": ramp_id,
                    "identifier_type": "device_id",
                    "identifier_value": secondary_id,
                    "device_type": p["secondary_device"],
                    "confidence_score": round(float(np.clip(rng.beta(2.0, 2.0), 0.25, 0.95)), 4),
                    "match_source": rng.choice(["deterministic", "probabilistic"], p=[0.412, 0.588]),
                    "first_seen": None,
                    "last_seen": None,
                    "person_id": p["person_id"],
                })

        if p["primary_device"] == "mobile" and rng.random() < apply_jitter(0.347):
            maid = "MAID_" + str(uuid.uuid4())[:16]
            records.append({
                "ramp_id": ramp_id,
                "identifier_type": "maid",
                "identifier_value": maid,
                "device_type": "mobile",
                "confidence_score": round(float(np.clip(rng.beta(3.0, 1.5), 0.5, 1.0)), 4),
                "match_source": "deterministic",
                "first_seen": None,
                "last_seen": None,
                "person_id": p["person_id"],
            })

        if p["primary_device"] == "ctv" and rng.random() < apply_jitter(0.213):
            ip_id = f"IP_{rng.integers(10,255)}.{rng.integers(0,255)}.{rng.integers(0,255)}.{rng.integers(1,254)}"
            records.append({
                "ramp_id": ramp_id,
                "identifier_type": "ip_address",
                "identifier_value": ip_id,
                "device_type": "ctv",
                "confidence_score": round(float(np.clip(rng.beta(1.5, 2.5), 0.15, 0.75)), 4),
                "match_source": "probabilistic",
                "first_seen": None,
                "last_seen": None,
                "person_id": p["person_id"],
            })

    return records
