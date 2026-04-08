import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connection import run_query

st.title("Channel Performance")

model_type = st.sidebar.selectbox("Attribution Model", ["linear", "last_touch", "first_touch", "time_decay", "position_based"])

perf = run_query(f"""
    SELECT CHANNEL, CAMPAIGN_ID, CAMPAIGN_NAME, ADVERTISER_ID,
           IMPRESSIONS, SPEND, CLICKS, ATTRIBUTED_CONVERSIONS, ATTRIBUTED_REVENUE,
           CTR, CONVERSION_RATE, ROAS, CPA
    FROM MTA_DEMO.ANALYTICS.CHANNEL_PERFORMANCE
    WHERE MODEL_TYPE = '{model_type}'
    ORDER BY ATTRIBUTED_REVENUE DESC
""")

if not perf.empty:
    col1, col2 = st.columns(2)
    with col1:
        channel_summary = perf.groupby("CHANNEL").agg({"SPEND": "sum", "ATTRIBUTED_REVENUE": "sum"}).reset_index()
        channel_summary["ROAS"] = channel_summary["ATTRIBUTED_REVENUE"] / channel_summary["SPEND"].replace(0, 1)
        fig = px.bar(channel_summary, x="CHANNEL", y="ROAS", title="ROAS by Channel", color="ROAS",
                     color_continuous_scale="RdYlGn")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.treemap(perf, path=["CHANNEL", "CAMPAIGN_NAME"], values="ATTRIBUTED_REVENUE",
                          title="Revenue Treemap", color="ROAS", color_continuous_scale="RdYlGn")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Detailed Performance Table")
    st.dataframe(perf.style.format({
        "SPEND": "${:,.0f}", "ATTRIBUTED_REVENUE": "${:,.0f}",
        "CTR": "{:.4%}", "CONVERSION_RATE": "{:.6f}", "ROAS": "{:.2f}x", "CPA": "${:,.2f}"
    }), use_container_width=True)
