import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connection import run_query

st.title("Foot Traffic & Incrementality")

st.subheader("Geo-Holdout Incrementality Test Results")
incr = run_query("SELECT * FROM MTA_DEMO.ANALYTICS.INCREMENTALITY_RESULTS")

if not incr.empty:
    col1, col2, col3 = st.columns(3)
    treatment = incr[incr["TEST_GROUP"] == "treatment"]
    control = incr[incr["TEST_GROUP"] == "control"]

    if not treatment.empty and not control.empty:
        with col1:
            st.metric("Treatment Visits", f"{treatment['TOTAL_VISITS'].iloc[0]:,.0f}")
        with col2:
            st.metric("Control Visits", f"{control['TOTAL_VISITS'].iloc[0]:,.0f}")
        with col3:
            lift = treatment["INCREMENTAL_LIFT"].iloc[0]
            st.metric("Incremental Lift", f"{lift*100:.1f}%" if lift else "N/A")

    fig = px.bar(incr, x="TEST_GROUP", y="TOTAL_VISITS", color="TEST_GROUP",
                 title="Total Store Visits: Treatment vs Control")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Foot Traffic by DMA")
ft_dma = run_query("""
    SELECT DMA_CODE, DMA_NAME,
           COUNT(*) AS VISITS,
           COUNT(DISTINCT PERSON_ID) AS UNIQUE_VISITORS,
           AVG(DWELL_TIME_MINUTES) AS AVG_DWELL
    FROM MTA_DEMO.STAGING.STG_FOOT_TRAFFIC
    GROUP BY 1, 2
    ORDER BY VISITS DESC
""")
st.dataframe(ft_dma, use_container_width=True)
