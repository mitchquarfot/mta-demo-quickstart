import random
from datetime import datetime, timedelta
import math

SEED = 42
random.seed(SEED)

DATE_START = datetime(2025, 1, 1)
DATE_END = datetime(2025, 12, 31)
NUM_DAYS = (DATE_END - DATE_START).days + 1

NUM_PEOPLE = 50_000
TARGET_IMPRESSIONS = 1_000_000
TARGET_CLICKS = 25_000
TARGET_PIXEL_FIRES = 60_000
TARGET_SESSIONS = 40_000
TARGET_RAW_CONVERSIONS = 4_200
TARGET_DEDUPED_CONVERSIONS = 3_200
TARGET_FOOT_TRAFFIC = 700

POPULATION_SEGMENTS = {
    "converter":       {"share": 0.0873, "click_propensity": 0.68, "session_propensity": 0.82},
    "store_visitor":   {"share": 0.0241, "click_propensity": 0.42, "session_propensity": 0.55},
    "engager":         {"share": 0.1786, "click_propensity": 0.31, "session_propensity": 0.44},
    "passive_exposed": {"share": 0.7100, "click_propensity": 0.006, "session_propensity": 0.012},
}

BROWSER_DISTRIBUTION = {
    "chrome":  0.6318,
    "safari":  0.1947,
    "edge":    0.0512,
    "firefox": 0.0389,
    "samsung": 0.0421,
    "other":   0.0413,
}

ITP_CONFIG = {
    "cookie_lifespan_days": 7,
    "affected_browsers": ["safari"],
    "cookies_per_year_per_user": 52,
    "tracking_prevention_rate": 0.943,
}

CONSENT_DISTRIBUTION = {
    "full_consent":    0.637,
    "essential_only":  0.214,
    "rejected_all":    0.112,
    "us_exempt":       0.037,
}

CONSENT_EFFECTS = {
    "full_consent":   {"pixel_fire": True,  "session_track": True,  "device_graph": True,  "conversion_track": True},
    "essential_only": {"pixel_fire": False, "session_track": True,  "device_graph": False, "conversion_track": True},
    "rejected_all":   {"pixel_fire": False, "session_track": False, "device_graph": False, "conversion_track": False},
    "us_exempt":      {"pixel_fire": True,  "session_track": True,  "device_graph": True,  "conversion_track": True},
}

DEVICE_TYPES = {
    "desktop":     0.3214,
    "mobile":      0.4387,
    "tablet":      0.0562,
    "ctv":         0.1243,
    "smart_speaker": 0.0198,
    "console":     0.0396,
}

OVERALL_MATCH_RATE = 0.584

CHANNEL_MATCH_RATES = {
    "display":       0.572,
    "olv":           0.613,
    "ctv":           0.52,
    "social":        0.687,
    "search":        0.724,
    "native":        0.591,
    "audio":         0.312,
    "dooh":          0.0,
}

CHANNEL_CONFIG = {
    "display": {
        "impression_share": 0.3604,
        "ctr": 0.00074,
        "view_through_rate": 0.0031,
        "cpm": 4.82,
        "avg_frequency": 18.7,
        "devices": ["desktop", "mobile", "tablet"],
    },
    "olv": {
        "impression_share": 0.1866,
        "ctr": 0.00213,
        "view_through_rate": 0.014,
        "cpm": 12.37,
        "avg_frequency": 8.4,
        "devices": ["desktop", "mobile", "tablet"],
    },
    "ctv": {
        "impression_share": 0.1256,
        "ctr": 0.0,
        "view_through_rate": 0.022,
        "cpm": 28.63,
        "avg_frequency": 6.2,
        "devices": ["ctv"],
    },
    "social": {
        "impression_share": 0.1386,
        "ctr": 0.00891,
        "view_through_rate": 0.0042,
        "cpm": 7.14,
        "avg_frequency": 12.3,
        "devices": ["mobile", "desktop"],
    },
    "search": {
        "impression_share": 0.0694,
        "ctr": 0.0342,
        "view_through_rate": 0.0,
        "cpm": 2.18,
        "avg_frequency": 4.1,
        "devices": ["desktop", "mobile"],
    },
    "native": {
        "impression_share": 0.0579,
        "ctr": 0.00312,
        "view_through_rate": 0.0019,
        "cpm": 6.43,
        "avg_frequency": 7.8,
        "devices": ["desktop", "mobile", "tablet"],
    },
    "audio": {
        "impression_share": 0.0422,
        "ctr": 0.0,
        "view_through_rate": 0.0047,
        "cpm": 15.21,
        "avg_frequency": 5.3,
        "devices": ["mobile", "smart_speaker", "desktop"],
    },
    "dooh": {
        "impression_share": 0.0193,
        "ctr": 0.0,
        "view_through_rate": 0.0012,
        "cpm": 9.87,
        "avg_frequency": 3.1,
        "devices": ["dooh"],
    },

}

ADVERTISERS = {
    "ADV001": {"name": "FreshCo Foods",       "vertical": "cpg",       "annual_budget": 8_400_000,  "conversion_value_avg": 42.17},
    "ADV002": {"name": "AutoDrive Motors",     "vertical": "auto",      "annual_budget": 14_200_000, "conversion_value_avg": 287.43},
    "ADV003": {"name": "ShopNow Retail",       "vertical": "retail",    "annual_budget": 6_800_000,  "conversion_value_avg": 67.82},
    "ADV004": {"name": "TrustBank Financial",  "vertical": "finance",   "annual_budget": 11_500_000, "conversion_value_avg": 193.67},
    "ADV005": {"name": "WanderLux Travel",     "vertical": "travel",    "annual_budget": 5_300_000,  "conversion_value_avg": 412.91},
    "ADV006": {"name": "QuickBite QSR",        "vertical": "qsr",       "annual_budget": 4_100_000,  "conversion_value_avg": 18.43},
    "ADV007": {"name": "VitalLife Wellness",   "vertical": "wellness",  "annual_budget": 3_700_000,  "conversion_value_avg": 89.26},
    "ADV008": {"name": "CloudSync B2B",        "vertical": "b2b_tech",  "annual_budget": 9_600_000,  "conversion_value_avg": 1_247.83},
    "ADV009": {"name": "PureGlow DTC",         "vertical": "dtc",       "annual_budget": 2_900_000,  "conversion_value_avg": 54.31},
    "ADV010": {"name": "PixelForge Gaming",    "vertical": "gaming",    "annual_budget": 7_200_000,  "conversion_value_avg": 34.67},
}

CAMPAIGN_ARC_TYPES = {
    "launch_spike": {
        "description": "Big launch, quick peak, gradual decline",
        "daily_modifier": lambda day_pct: 2.8 * math.exp(-3.2 * day_pct) + 0.4,
    },
    "slow_build": {
        "description": "Gradual ramp to peak at 70%, then plateau",
        "daily_modifier": lambda day_pct: 0.3 + 1.4 * (1 - math.exp(-4.0 * day_pct)),
    },
    "seasonal_burst": {
        "description": "Low baseline with holiday spike",
        "daily_modifier": lambda day_pct: 0.5 + 2.5 * math.exp(-50 * (day_pct - 0.75) ** 2),
    },
    "fatigue_decline": {
        "description": "Strong start, steady decline as creative fatigues",
        "daily_modifier": lambda day_pct: 1.8 * (1 - 0.7 * day_pct),
    },
    "steady_state": {
        "description": "Consistent always-on spend",
        "daily_modifier": lambda day_pct: 0.95 + 0.1 * math.sin(2 * math.pi * day_pct * 4),
    },
}

CAMPAIGNS = [
    {"id": "CMP001", "advertiser": "ADV001", "name": "FreshCo Spring Launch",      "channel_mix": ["display", "olv", "social", "native"],          "arc": "launch_spike",    "start_day": 0,   "end_day": 89,   "budget_share": 0.28},
    {"id": "CMP002", "advertiser": "ADV001", "name": "FreshCo Summer Always-On",   "channel_mix": ["display", "social", "search"],                  "arc": "steady_state",    "start_day": 60,  "end_day": 243,  "budget_share": 0.38},
    {"id": "CMP003", "advertiser": "ADV001", "name": "FreshCo Holiday Push",       "channel_mix": ["display", "olv", "ctv", "social", "audio"],     "arc": "seasonal_burst",  "start_day": 274, "end_day": 364,  "budget_share": 0.34},
    {"id": "CMP004", "advertiser": "ADV002", "name": "AutoDrive Model Year Launch","channel_mix": ["ctv", "olv", "display", "search"],              "arc": "launch_spike",    "start_day": 30,  "end_day": 150,  "budget_share": 0.32},
    {"id": "CMP005", "advertiser": "ADV002", "name": "AutoDrive Brand Awareness",  "channel_mix": ["ctv", "olv", "audio", "dooh"],                  "arc": "slow_build",      "start_day": 0,   "end_day": 364,  "budget_share": 0.41},
    {"id": "CMP006", "advertiser": "ADV002", "name": "AutoDrive Year-End Sales",   "channel_mix": ["display", "search", "social", "native"],        "arc": "seasonal_burst",  "start_day": 305, "end_day": 364,  "budget_share": 0.27},
    {"id": "CMP007", "advertiser": "ADV003", "name": "ShopNow Spring Sale",        "channel_mix": ["display", "social", "search", "native"],       "arc": "launch_spike",    "start_day": 59,  "end_day": 120,  "budget_share": 0.22},
    {"id": "CMP008", "advertiser": "ADV003", "name": "ShopNow Loyalty Program",    "channel_mix": ["display", "social", "native", "search"],       "arc": "slow_build",      "start_day": 0,   "end_day": 364,  "budget_share": 0.31},
    {"id": "CMP009", "advertiser": "ADV003", "name": "ShopNow Black Friday",       "channel_mix": ["display", "olv", "social", "search", "native"],"arc": "seasonal_burst",  "start_day": 297, "end_day": 334,  "budget_share": 0.47},
    {"id": "CMP010", "advertiser": "ADV004", "name": "TrustBank New Product",      "channel_mix": ["display", "olv", "search", "native"],           "arc": "launch_spike",    "start_day": 45,  "end_day": 180,  "budget_share": 0.35},
    {"id": "CMP011", "advertiser": "ADV004", "name": "TrustBank Always-On",        "channel_mix": ["display", "search", "social"],                  "arc": "steady_state",    "start_day": 0,   "end_day": 364,  "budget_share": 0.42},
    {"id": "CMP012", "advertiser": "ADV004", "name": "TrustBank Tax Season",       "channel_mix": ["search", "display", "social", "olv"],           "arc": "seasonal_burst",  "start_day": 0,   "end_day": 105,  "budget_share": 0.23},
    {"id": "CMP013", "advertiser": "ADV005", "name": "WanderLux Summer Getaway",   "channel_mix": ["olv", "ctv", "social", "display", "native"],    "arc": "seasonal_burst",  "start_day": 120, "end_day": 243,  "budget_share": 0.44},
    {"id": "CMP014", "advertiser": "ADV005", "name": "WanderLux Brand Film",       "channel_mix": ["ctv", "olv", "audio"],                          "arc": "slow_build",      "start_day": 0,   "end_day": 364,  "budget_share": 0.31},
    {"id": "CMP015", "advertiser": "ADV005", "name": "WanderLux Winter Escapes",   "channel_mix": ["display", "social", "search"],                  "arc": "fatigue_decline", "start_day": 305, "end_day": 364,  "budget_share": 0.25},
    {"id": "CMP016", "advertiser": "ADV006", "name": "QuickBite New Menu Launch",  "channel_mix": ["ctv", "olv", "social", "dooh"],                 "arc": "launch_spike",    "start_day": 90,  "end_day": 180,  "budget_share": 0.37},
    {"id": "CMP017", "advertiser": "ADV006", "name": "QuickBite Always-On Local",  "channel_mix": ["display", "social", "search"],                  "arc": "steady_state",    "start_day": 0,   "end_day": 364,  "budget_share": 0.63},
    {"id": "CMP018", "advertiser": "ADV007", "name": "VitalLife Wellness Q1",      "channel_mix": ["social", "native", "display", "olv"],           "arc": "launch_spike",    "start_day": 0,   "end_day": 89,   "budget_share": 0.34},
    {"id": "CMP019", "advertiser": "ADV007", "name": "VitalLife Summer Body",      "channel_mix": ["social", "olv", "display", "search"],           "arc": "slow_build",      "start_day": 90,  "end_day": 243,  "budget_share": 0.41},
    {"id": "CMP020", "advertiser": "ADV007", "name": "VitalLife Holiday Gifting",  "channel_mix": ["display", "social", "native", "olv"],           "arc": "seasonal_burst",  "start_day": 305, "end_day": 364,  "budget_share": 0.25},
    {"id": "CMP021", "advertiser": "ADV008", "name": "CloudSync Enterprise Launch","channel_mix": ["display", "search", "native", "social"],        "arc": "launch_spike",    "start_day": 30,  "end_day": 180,  "budget_share": 0.38},
    {"id": "CMP022", "advertiser": "ADV008", "name": "CloudSync ABM Always-On",   "channel_mix": ["display", "search", "social", "native"],         "arc": "steady_state",    "start_day": 0,   "end_day": 364,  "budget_share": 0.47},
    {"id": "CMP023", "advertiser": "ADV008", "name": "CloudSync Re:Invent Push",  "channel_mix": ["display", "olv", "social"],                     "arc": "seasonal_burst",  "start_day": 305, "end_day": 340,  "budget_share": 0.15},
    {"id": "CMP024", "advertiser": "ADV009", "name": "PureGlow TikTok-First",     "channel_mix": ["social", "olv", "display"],                     "arc": "slow_build",      "start_day": 0,   "end_day": 180,  "budget_share": 0.43},
    {"id": "CMP025", "advertiser": "ADV009", "name": "PureGlow Holiday Gift Sets","channel_mix": ["social", "display", "search", "native"],        "arc": "seasonal_burst",  "start_day": 274, "end_day": 364,  "budget_share": 0.37},
    {"id": "CMP026", "advertiser": "ADV009", "name": "PureGlow Retargeting",      "channel_mix": ["display", "social", "native"],                  "arc": "fatigue_decline", "start_day": 60,  "end_day": 270,  "budget_share": 0.20},
    {"id": "CMP027", "advertiser": "ADV010", "name": "PixelForge Game Launch",    "channel_mix": ["ctv", "olv", "social", "display"],              "arc": "launch_spike",    "start_day": 90,  "end_day": 180,  "budget_share": 0.42},
    {"id": "CMP028", "advertiser": "ADV010", "name": "PixelForge Esports Season", "channel_mix": ["olv", "social", "display", "audio"],            "arc": "slow_build",      "start_day": 0,   "end_day": 243,  "budget_share": 0.33},
    {"id": "CMP029", "advertiser": "ADV010", "name": "PixelForge Holiday Bundle", "channel_mix": ["display", "social", "search", "ctv"],           "arc": "seasonal_burst",  "start_day": 305, "end_day": 364,  "budget_share": 0.25},
    {"id": "CMP030", "advertiser": "ADV001", "name": "FreshCo Back to School",    "channel_mix": ["display", "social", "search"],                  "arc": "fatigue_decline", "start_day": 210, "end_day": 273,  "budget_share": 0.0},
]

CREATIVE_TEMPLATES = {
    "display":   ["300x250_static", "728x90_static", "300x600_static", "320x50_mobile", "300x250_rich", "160x600_static"],
    "olv":       ["15s_preroll", "30s_preroll", "6s_bumper", "15s_midroll"],
    "ctv":       ["30s_spot", "15s_spot", "60s_brand_film"],
    "social":    ["feed_image", "feed_video", "story_video", "carousel", "reel"],
    "search":    ["text_ad", "shopping_ad", "responsive_search"],
    "native":    ["in_feed_article", "recommendation_widget", "sponsored_content"],
    "audio":     ["15s_audio", "30s_audio"],
    "dooh":      ["billboard_static", "transit_digital"],
}

CONVERSION_TYPES = {
    "purchase":        {"share": 0.4217, "value_multiplier": 1.0},
    "lead_form":       {"share": 0.2143, "value_multiplier": 0.35},
    "signup":          {"share": 0.1876, "value_multiplier": 0.22},
    "add_to_cart":     {"share": 0.1018, "value_multiplier": 0.15},
    "store_locator":   {"share": 0.0746, "value_multiplier": 0.08},
}

TRIPLE_FIRE_RATE = 0.286
CONVERSION_SOURCE_PRIORITY = ["gcm_floodlight", "gtm_pixel", "ga4_goal"]

FREQUENCY_DISTRIBUTION = {
    "bucket_1_5":    {"share": 0.3217, "avg_freq": 2.8},
    "bucket_6_15":   {"share": 0.2843, "avg_freq": 9.4},
    "bucket_16_30":  {"share": 0.1962, "avg_freq": 21.7},
    "bucket_31_60":  {"share": 0.1147, "avg_freq": 42.3},
    "bucket_61_100": {"share": 0.0523, "avg_freq": 76.8},
    "bucket_101_500":{"share": 0.0240, "avg_freq": 187.4},
    "bucket_500plus":{"share": 0.0068, "avg_freq": 743.2},
}

GEO_HOLDOUT = {
    "test_type": "geo_holdout",
    "channel": "ctv",
    "holdout_duration_days": 28,
    "holdout_start_day": 180,
    "control_dmas": [
        {"code": "501", "name": "New York"},
        {"code": "803", "name": "Los Angeles"},
        {"code": "602", "name": "Chicago"},
        {"code": "504", "name": "Philadelphia"},
        {"code": "511", "name": "Washington DC"},
        {"code": "524", "name": "Atlanta"},
        {"code": "623", "name": "Dallas-Ft. Worth"},
        {"code": "618", "name": "Houston"},
        {"code": "506", "name": "Boston"},
        {"code": "753", "name": "Phoenix"},
    ],
    "treatment_dmas": [
        {"code": "807", "name": "San Francisco"},
        {"code": "819", "name": "Seattle"},
        {"code": "751", "name": "Denver"},
        {"code": "539", "name": "Tampa"},
        {"code": "527", "name": "Indianapolis"},
        {"code": "528", "name": "Miami"},
        {"code": "510", "name": "Cleveland"},
        {"code": "613", "name": "Minneapolis"},
        {"code": "617", "name": "Milwaukee"},
        {"code": "641", "name": "San Antonio"},
    ],
    "expected_lift": 0.127,
}

JITTER_PCT = 0.025

DAYOFWEEK_MODIFIERS = {
    0: 1.12,
    1: 1.08,
    2: 1.04,
    3: 1.02,
    4: 0.97,
    5: 0.84,
    6: 0.79,
}

HOUR_DISTRIBUTION = [
    0.012, 0.008, 0.006, 0.005, 0.005, 0.007,
    0.018, 0.032, 0.048, 0.062, 0.071, 0.074,
    0.072, 0.076, 0.073, 0.069, 0.064, 0.058,
    0.054, 0.051, 0.048, 0.042, 0.032, 0.019,
]

SEASONALITY_MONTHLY = [
    0.82, 0.79, 0.91, 0.94, 1.02, 1.04,
    0.97, 0.93, 1.01, 1.08, 1.23, 1.41,
]

VERTICAL_CONVERSION_RATES = {
    "cpg":      0.0118,
    "auto":     0.0034,
    "retail":   0.0267,
    "finance":  0.0083,
    "travel":   0.0091,
    "qsr":      0.0312,
    "wellness": 0.0147,
    "b2b_tech": 0.0042,
    "dtc":      0.0198,
    "gaming":   0.0223,
}


def apply_jitter(value, jitter_pct=JITTER_PCT):
    return value * (1.0 + random.uniform(-jitter_pct, jitter_pct))


def get_campaign_modifier(campaign, day_of_year):
    start = campaign["start_day"]
    end = campaign["end_day"]
    if day_of_year < start or day_of_year > end:
        return 0.0
    duration = max(end - start, 1)
    day_pct = (day_of_year - start) / duration
    arc_fn = CAMPAIGN_ARC_TYPES[campaign["arc"]]["daily_modifier"]
    base = arc_fn(day_pct)
    return apply_jitter(base)
