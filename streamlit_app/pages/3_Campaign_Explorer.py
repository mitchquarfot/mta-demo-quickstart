import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connection import run_query

st.title("Campaign Explorer")

campaigns = run_query("""
    SELECT DISTINCT CAMPAIGN_ID, CAMPAIGN_NAME, ADVERTISER_ID
    FROM MTA_DEMO.ANALYTICS.CAMPAIGN_DAILY_METRICS
    ORDER BY CAMPAIGN_ID
""")

selected_campaign = st.sidebar.selectbox(
    "Campaign",
    campaigns["CAMPAIGN_ID"].tolist(),
    format_func=lambda x: campaigns[campaigns["CAMPAIGN_ID"] == x]["CAMPAIGN_NAME"].iloc[0]
)

daily = run_query(f"""
    SELECT REPORT_DATE, CHANNEL, IMPRESSIONS, SPEND, CLICKS, CONVERSIONS, ATTRIBUTED_REVENUE, CTR, ROAS
    FROM MTA_DEMO.ANALYTICS.CAMPAIGN_DAILY_METRICS
    WHERE CAMPAIGN_ID = '{selected_campaign}'
      AND MODEL_TYPE = 'linear'
    ORDER BY REPORT_DATE
""")

if not daily.empty:
    fig = px.area(daily, x="REPORT_DATE", y="IMPRESSIONS", color="CHANNEL",
                  title="Daily Impressions by Channel")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.line(daily.groupby("REPORT_DATE").agg({"SPEND": "sum", "ATTRIBUTED_REVENUE": "sum"}).reset_index(),
                       x="REPORT_DATE", y=["SPEND", "ATTRIBUTED_REVENUE"],
                       title="Daily Spend vs Revenue")
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        daily_agg = daily.groupby("REPORT_DATE").agg({"SPEND": "sum", "ATTRIBUTED_REVENUE": "sum"}).reset_index()
        daily_agg["ROAS"] = daily_agg["ATTRIBUTED_REVENUE"] / daily_agg["SPEND"].replace(0, 1)
        fig3 = px.line(daily_agg, x="REPORT_DATE", y="ROAS", title="Daily ROAS Trend")
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Raw Daily Data")
    st.dataframe(daily, use_container_width=True)
