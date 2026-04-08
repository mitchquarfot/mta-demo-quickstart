#!/usr/bin/env python3
import sys
import time
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_generator.config import CAMPAIGNS, SEED
from data_generator.models.people import generate_people
from data_generator.models.device_graph import generate_device_graph
from data_generator.models.impressions import generate_impressions
from data_generator.models.clicks import generate_clicks, generate_pixel_fires, generate_sessions, generate_conversions, generate_view_through_conversions, generate_foot_traffic
from data_generator.loaders.snowflake_loader import save_to_parquet, load_all_tables, OUTPUT_DIR


def main():
    t0 = time.time()
    print("=" * 60)
    print("MTA Demo Data Generator")
    print("=" * 60)

    print("\n[1/9] Generating people...")
    people = generate_people()
    save_to_parquet(people, "people")
    people_lookup = {p["person_id"]: p for p in people}
    print(f"  Generated {len(people):,} people in {time.time()-t0:.1f}s")

    t1 = time.time()
    print("\n[2/9] Generating device graph...")
    device_graph = generate_device_graph(people)
    save_to_parquet(device_graph, "device_graph")
    print(f"  Generated {len(device_graph):,} graph edges in {time.time()-t1:.1f}s")

    t2 = time.time()
    print("\n[3/9] Generating impressions...")
    imp_df = generate_impressions(people, CAMPAIGNS)
    save_to_parquet(imp_df, "impressions")
    n_impressions = len(imp_df)
    print(f"  Generated {n_impressions:,} impressions in {time.time()-t2:.1f}s")

    t3 = time.time()
    print("\n[4/9] Generating clicks...")
    clicks = generate_clicks(imp_df, people_lookup)
    del imp_df
    save_to_parquet(clicks, "clicks")
    print(f"  Generated {len(clicks):,} clicks in {time.time()-t3:.1f}s")

    t4 = time.time()
    print("\n[5/9] Generating pixel fires...")
    pixel_fires = generate_pixel_fires(clicks, people_lookup)
    save_to_parquet(pixel_fires, "pixel_fires")
    print(f"  Generated {len(pixel_fires):,} pixel fires in {time.time()-t4:.1f}s")

    t5 = time.time()
    print("\n[6/9] Generating sessions...")
    sessions = generate_sessions(clicks, people_lookup)
    save_to_parquet(sessions, "sessions")
    print(f"  Generated {len(sessions):,} sessions in {time.time()-t5:.1f}s")

    t6 = time.time()
    print("\n[7/9] Generating click-based conversions (with triple-fire duplication)...")
    click_conversions = generate_conversions(clicks, sessions, people_lookup)
    print(f"  Generated {len(click_conversions):,} click-based conversions in {time.time()-t6:.1f}s")

    t6b = time.time()
    print("\n[8/9] Generating view-through conversions...")
    existing_converter_keys = set()
    for c in click_conversions:
        existing_converter_keys.add((c["person_id"], c["advertiser_id"]))
    imp_df_for_vt = pd.read_parquet(OUTPUT_DIR / "impressions.parquet")
    vt_conversions = generate_view_through_conversions(imp_df_for_vt, people_lookup, existing_converter_keys)
    del imp_df_for_vt
    print(f"  Generated {len(vt_conversions):,} view-through conversions in {time.time()-t6b:.1f}s")

    conversions = click_conversions + vt_conversions
    save_to_parquet(conversions, "conversions")
    print(f"  Total raw conversions: {len(conversions):,}")

    t7 = time.time()
    print("\n[9/9] Generating foot traffic...")
    foot_traffic = generate_foot_traffic(people, clicks)
    save_to_parquet(foot_traffic, "foot_traffic")
    print(f"  Generated {len(foot_traffic):,} store visits in {time.time()-t7:.1f}s")

    total_time = time.time() - t0
    print("\n" + "=" * 60)
    print(f"Data generation complete in {total_time:.1f}s")
    print(f"  People:       {len(people):>12,}")
    print(f"  Device Graph: {len(device_graph):>12,}")
    print(f"  Impressions:  {n_impressions:>12,}")
    print(f"  Clicks:       {len(clicks):>12,}")
    print(f"  Pixel Fires:  {len(pixel_fires):>12,}")
    print(f"  Sessions:     {len(sessions):>12,}")
    print(f"  Conversions:  {len(conversions):>12,}")
    print(f"  Foot Traffic: {len(foot_traffic):>12,}")
    print("=" * 60)

    if "--load" in sys.argv:
        print("\nLoading data into Snowflake...")
        load_all_tables()
        print("Loading complete!")


if __name__ == "__main__":
    main()
