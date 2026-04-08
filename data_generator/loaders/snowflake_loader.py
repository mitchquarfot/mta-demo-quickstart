import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import snowflake.connector
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output_parquet"


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_to_parquet(records_or_df, table_name):
    ensure_output_dir()
    if isinstance(records_or_df, pd.DataFrame):
        df = records_or_df
    elif records_or_df:
        df = pd.DataFrame(records_or_df)
    else:
        print(f"  [WARN] No records for {table_name}, skipping.")
        return None

    if df.empty:
        print(f"  [WARN] Empty DataFrame for {table_name}, skipping.")
        return None

    for col in df.columns:
        if df[col].dtype == "object":
            sample = df[col].dropna().head(1)
            if len(sample) > 0 and hasattr(sample.iloc[0], "isoformat"):
                df[col] = pd.to_datetime(df[col], errors="coerce")

    filepath = OUTPUT_DIR / f"{table_name}.parquet"
    df.to_parquet(filepath, engine="pyarrow", index=False)
    print(f"  Saved {len(df):,} rows to {filepath}")
    return filepath


def load_to_snowflake(table_name, parquet_path, connection_name=None):
    conn_name = connection_name or os.getenv("SNOWFLAKE_CONNECTION_NAME")
    if not conn_name:
        print(f"  [SKIP] No Snowflake connection for {table_name}")
        return

    conn = snowflake.connector.connect(connection_name=conn_name)
    cursor = conn.cursor()
    try:
        schema = "MTA_DEMO.RAW"
        stage = f"{schema}.DATA_LOAD_STAGE"

        cursor.execute(f"USE SCHEMA {schema}")
        put_cmd = f"PUT 'file://{parquet_path}' @{stage}/{table_name}/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
        cursor.execute(put_cmd)
        print(f"  PUT {table_name} → @{stage}/{table_name}/")

        cursor.execute(f"""
            CREATE OR REPLACE TABLE {schema}.{table_name}
            USING TEMPLATE (
                SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
                FROM TABLE(INFER_SCHEMA(
                    LOCATION => '@{stage}/{table_name}/',
                    FILE_FORMAT => 'MTA_DEMO.RAW.PARQUET_FORMAT'
                ))
            )
        """)
        print(f"  Created table {schema}.{table_name} from schema inference")

        cursor.execute(f"""
            COPY INTO {schema}.{table_name}
            FROM @{stage}/{table_name}/
            FILE_FORMAT = (TYPE = PARQUET)
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
        """)
        result = cursor.fetchone()
        print(f"  COPY INTO {table_name}: {result}")

    finally:
        cursor.close()
        conn.close()


def load_all_tables(connection_name=None):
    ensure_output_dir()
    parquet_files = sorted(OUTPUT_DIR.glob("*.parquet"))
    for pf in parquet_files:
        table_name = pf.stem.upper()
        print(f"\nLoading {table_name}...")
        load_to_snowflake(table_name, pf, connection_name)
