import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connection import run_query

st.title("Attribution Model Comparison")

advertisers = run_query('SELECT DISTINCT ADVERTISER_ID FROM MTA_DEMO.ANALYTICS.ATTRIBUTION_RESULTS ORDER BY 1')
selected_adv = st.sidebar.selectbox("Advertiser", advertisers["ADVERTISER_ID"].tolist(), index=0)

models = ["last_touch", "first_touch", "linear", "time_decay", "position_based"]
selected_models = st.sidebar.multiselect("Attribution Models", models, default=models)

if selected_models:
    model_filter = ",".join([f"'{m}'" for m in selected_models])
    data = run_query(f"""
        SELECT MODEL_TYPE, CHANNEL,
               SUM(ATTRIBUTED_REVENUE) AS REVENUE,
               SUM(ATTRIBUTION_WEIGHT) AS CONVERSIONS
        FROM MTA_DEMO.ANALYTICS.ATTRIBUTION_RESULTS
        WHERE ADVERTISER_ID = '{selected_adv}'
          AND MODEL_TYPE IN ({model_filter})
        GROUP BY 1, 2
        ORDER BY 1, REVENUE DESC
    """)

    if not data.empty:
        fig = px.bar(data, x="CHANNEL", y="REVENUE", color="MODEL_TYPE",
                     barmode="group", title="Attributed Revenue by Channel & Model")
        st.plotly_chart(fig, use_container_width=True)

        pivot = data.pivot_table(index="CHANNEL", columns="MODEL_TYPE", values="REVENUE", aggfunc="sum").fillna(0)
        st.subheader("Revenue Pivot Table")
        st.dataframe(pivot.style.format("${:,.0f}"), use_container_width=True)

        fig2 = px.bar(data, x="CHANNEL", y="CONVERSIONS", color="MODEL_TYPE",
                      barmode="group", title="Attributed Conversions by Channel & Model")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No data found for the selected filters.")
