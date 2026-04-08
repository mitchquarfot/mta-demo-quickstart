#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_generator.loaders.snowflake_loader import load_all_tables

if __name__ == "__main__":
    load_all_tables()
