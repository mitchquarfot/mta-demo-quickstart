import os
import streamlit as st
import snowflake.connector
import pandas as pd

@st.cache_resource
def get_connection():
    conn_name = os.getenv("SNOWFLAKE_CONNECTION_NAME", "my_connection")
    return snowflake.connector.connect(
        connection_name=conn_name,
        database="MTA_DEMO",
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "MTA_WH"),
    )

def run_query(sql, ttl=300):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    columns = [desc[0] for desc in cur.description]
    data = cur.fetchall()
    return pd.DataFrame(data, columns=columns)
