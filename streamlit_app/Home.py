import streamlit as st
from connection import run_query

st.set_page_config(
    page_title="MTA Demo - Multi-Touch Attribution",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Multi-Touch Attribution Dashboard")
st.markdown("### Identity Health & Signal Loss Monitor")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_imps = run_query("SELECT COUNT(*) AS cnt FROM MTA_DEMO.STAGING.STG_IMPRESSIONS")
    st.metric("Total Impressions", f"{total_imps['CNT'].iloc[0]:,.0f}")

with col2:
    match_rate = run_query("""
        SELECT ROUND(AVG(CASE WHEN RESOLUTION_METHOD = 'device_graph' THEN 1.0 ELSE 0.0 END), 4) AS rate
        FROM MTA_DEMO.STAGING.STG_IDENTITY_RESOLVED
    """)
    st.metric("Identity Match Rate", f"{match_rate['RATE'].iloc[0]*100:.1f}%")

with col3:
    itp_rate = run_query("""
        SELECT ROUND(AVG(CASE WHEN COOKIE_RELIABILITY = 'itp_rotated' THEN 1.0 ELSE 0.0 END), 4) AS rate
        FROM MTA_DEMO.STAGING.STG_IMPRESSIONS
    """)
    st.metric("ITP-Affected Events", f"{itp_rate['RATE'].iloc[0]*100:.1f}%")

with col4:
    consent_block = run_query("""
        SELECT ROUND(AVG(CASE WHEN IS_TRACKABLE = FALSE THEN 1.0 ELSE 0.0 END), 4) AS rate
        FROM MTA_DEMO.STAGING.STG_IMPRESSIONS
    """)
    st.metric("Consent-Blocked", f"{consent_block['RATE'].iloc[0]*100:.1f}%")

st.divider()

st.subheader("Signal Health by Channel")
signal_health = run_query("""
    SELECT * FROM MTA_DEMO.ANALYTICS.CHANNEL_PERFORMANCE
    WHERE MODEL_TYPE = 'linear'
    ORDER BY SPEND DESC
""")
st.dataframe(signal_health, use_container_width=True)

st.divider()

st.subheader("Conversion Deduplication Summary")
dedup = run_query("SELECT * FROM MTA_DEMO.ANALYTICS.CONVERSION_DEDUP_REPORT")
st.dataframe(dedup, use_container_width=True)

st.divider()
st.subheader("Population Breakdown")
pop = run_query("""
    SELECT "segment", COUNT(*) AS PEOPLE,
           ROUND(COUNT(*)::FLOAT / SUM(COUNT(*)) OVER (), 4) AS SHARE
    FROM MTA_DEMO.RAW.PEOPLE
    GROUP BY "segment" ORDER BY PEOPLE DESC
""")
st.dataframe(pop, use_container_width=True)
