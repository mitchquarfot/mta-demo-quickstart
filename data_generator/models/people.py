import numpy as np
import uuid
from data_generator.config import (
    NUM_PEOPLE, SEED, BROWSER_DISTRIBUTION, CONSENT_DISTRIBUTION,
    DEVICE_TYPES, POPULATION_SEGMENTS, CHANNEL_MATCH_RATES,
    OVERALL_MATCH_RATE, GEO_HOLDOUT, apply_jitter
)

def generate_people(seed=SEED):
    rng = np.random.default_rng(seed)

    browsers = list(BROWSER_DISTRIBUTION.keys())
    browser_probs = np.array([BROWSER_DISTRIBUTION[b] for b in browsers])
    browser_probs /= browser_probs.sum()

    consent_types = list(CONSENT_DISTRIBUTION.keys())
    consent_probs = np.array([CONSENT_DISTRIBUTION[c] for c in consent_types])
    consent_probs /= consent_probs.sum()

    segments = list(POPULATION_SEGMENTS.keys())
    segment_probs = np.array([POPULATION_SEGMENTS[s]["share"] for s in segments])
    segment_probs /= segment_probs.sum()

    devices = list(DEVICE_TYPES.keys())
    device_probs = np.array([DEVICE_TYPES[d] for d in devices])
    device_probs /= device_probs.sum()

    all_dmas = GEO_HOLDOUT["control_dmas"] + GEO_HOLDOUT["treatment_dmas"]

    person_ids = [str(uuid.uuid4()) for _ in range(NUM_PEOPLE)]
    browser_assignments = rng.choice(browsers, size=NUM_PEOPLE, p=browser_probs)
    consent_assignments = rng.choice(consent_types, size=NUM_PEOPLE, p=consent_probs)
    segment_assignments = rng.choice(segments, size=NUM_PEOPLE, p=segment_probs)
    primary_device = rng.choice(devices, size=NUM_PEOPLE, p=device_probs)

    has_secondary = rng.random(NUM_PEOPLE) < 0.372
    secondary_device = np.where(
        has_secondary,
        rng.choice(devices, size=NUM_PEOPLE, p=device_probs),
        None
    )

    in_device_graph = rng.random(NUM_PEOPLE) < apply_jitter(OVERALL_MATCH_RATE)
    graph_confidence = np.where(
        in_device_graph,
        np.clip(rng.beta(2.4, 1.6, size=NUM_PEOPLE), 0.3, 1.0),
        0.0
    )

    dma_indices = rng.integers(0, len(all_dmas), size=NUM_PEOPLE)
    dma_codes = [all_dmas[i]["code"] for i in dma_indices]
    dma_names = [all_dmas[i]["name"] for i in dma_indices]

    age_brackets = rng.choice(
        ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
        size=NUM_PEOPLE,
        p=[0.1243, 0.2687, 0.2318, 0.1847, 0.1213, 0.0692]
    )
    genders = rng.choice(
        ["M", "F", "NB", "U"],
        size=NUM_PEOPLE,
        p=[0.4712, 0.4823, 0.0143, 0.0322]
    )
    hhi_brackets = rng.choice(
        ["<25k", "25-50k", "50-75k", "75-100k", "100-150k", "150k+"],
        size=NUM_PEOPLE,
        p=[0.1143, 0.1687, 0.1943, 0.1812, 0.1847, 0.1568]
    )

    cookie_base_ids = [str(uuid.uuid4()) for _ in range(NUM_PEOPLE)]

    people = []
    for i in range(NUM_PEOPLE):
        people.append({
            "person_id": person_ids[i],
            "cookie_id": cookie_base_ids[i],
            "browser": browser_assignments[i],
            "consent_status": consent_assignments[i],
            "segment": segment_assignments[i],
            "primary_device": primary_device[i],
            "secondary_device": secondary_device[i] if has_secondary[i] else None,
            "in_device_graph": bool(in_device_graph[i]),
            "graph_confidence": float(graph_confidence[i]),
            "dma_code": dma_codes[i],
            "dma_name": dma_names[i],
            "age_bracket": age_brackets[i],
            "gender": genders[i],
            "hhi_bracket": hhi_brackets[i],
        })

    return people
