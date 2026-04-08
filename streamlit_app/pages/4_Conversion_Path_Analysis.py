import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connection import run_query

st.title("Conversion Path Analysis")

path_stats = run_query("""
    SELECT TOTAL_TOUCHPOINTS AS PATH_LENGTH,
        COUNT(DISTINCT CONVERSION_ID) AS CONVERSIONS,
        AVG(CONVERSION_VALUE) AS AVG_VALUE,
        AVG(HOURS_TO_CONVERSION) AS AVG_HOURS_TO_CONVERT
    FROM MTA_DEMO.ANALYTICS.CONVERSION_PATHS
    GROUP BY 1
    ORDER BY 1
""")

if not path_stats.empty:
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(path_stats, x="PATH_LENGTH", y="CONVERSIONS",
                     title="Conversions by Path Length")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.line(path_stats, x="PATH_LENGTH", y="AVG_HOURS_TO_CONVERT",
                       title="Avg Hours to Convert by Path Length")
        st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.subheader("Top Channel Sequences")
top_paths = run_query("""
    WITH sequenced AS (
        SELECT CONVERSION_ID,
               LISTAGG(CHANNEL, ' > ') WITHIN GROUP (ORDER BY TOUCHPOINT_POSITION) AS PATH
        FROM MTA_DEMO.ANALYTICS.CONVERSION_PATHS
        GROUP BY CONVERSION_ID
    )
    SELECT PATH, COUNT(*) AS CONVERSIONS
    FROM sequenced
    GROUP BY PATH
    ORDER BY CONVERSIONS DESC
    LIMIT 20
""")
st.dataframe(top_paths, use_container_width=True)

st.divider()
st.subheader("Frequency Distribution")
freq = run_query('SELECT * FROM MTA_DEMO.ANALYTICS.FREQUENCY_DISTRIBUTION ORDER BY CHANNEL, FREQUENCY_BUCKET')
if not freq.empty:
    fig3 = px.bar(freq, x="FREQUENCY_BUCKET", y="UNIQUE_USERS", color="CHANNEL",
                  barmode="group", title="User Frequency Distribution by Channel")
    st.plotly_chart(fig3, use_container_width=True)
