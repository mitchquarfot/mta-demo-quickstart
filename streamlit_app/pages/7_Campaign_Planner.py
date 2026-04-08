import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connection import run_query

st.title("Campaign Planner & What-If Simulator")

st.subheader("Budget Allocation Simulator")
st.markdown("Adjust channel budgets to see projected ROAS and conversions.")

current = run_query("""
    SELECT CHANNEL,
           SUM(SPEND) AS CURRENT_SPEND,
           SUM(ATTRIBUTED_REVENUE) AS CURRENT_REVENUE,
           SUM(ATTRIBUTED_CONVERSIONS) AS CURRENT_CONVERSIONS,
           CASE WHEN SUM(SPEND) > 0 THEN SUM(ATTRIBUTED_REVENUE) / SUM(SPEND) ELSE 0 END AS CURRENT_ROAS
    FROM MTA_DEMO.ANALYTICS.CHANNEL_PERFORMANCE
    WHERE MODEL_TYPE = 'linear'
    GROUP BY CHANNEL
    ORDER BY CURRENT_SPEND DESC
""")

if not current.empty:
    current_total = max(int(current["CURRENT_SPEND"].sum()), 10000)
    total_budget = st.sidebar.number_input(
        "Total Annual Budget ($)",
        min_value=10000,
        max_value=100000000,
        value=current_total,
        step=10000
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Channel Budget Allocation (%)**")

    allocations = {}
    channels = current["CHANNEL"].tolist()
    current_pcts = (current["CURRENT_SPEND"] / current["CURRENT_SPEND"].sum() * 100).tolist()

    for i, ch in enumerate(channels):
        allocations[ch] = st.sidebar.slider(
            ch.upper(),
            min_value=0, max_value=100,
            value=int(current_pcts[i]),
            step=1
        )

    total_alloc = sum(allocations.values())
    if total_alloc > 0:
        projected = []
        for _, row in current.iterrows():
            ch = row["CHANNEL"]
            alloc_pct = allocations.get(ch, 0) / total_alloc
            new_spend = total_budget * alloc_pct
            roas = row["CURRENT_ROAS"] if row["CURRENT_ROAS"] > 0 else 1.0
            diminishing_factor = min(1.0, (new_spend / max(row["CURRENT_SPEND"], 1)) ** 0.7)
            proj_rev = new_spend * roas * diminishing_factor
            proj_conv = row["CURRENT_CONVERSIONS"] * (new_spend / max(row["CURRENT_SPEND"], 1)) * diminishing_factor

            projected.append({
                "Channel": ch,
                "Current Spend": row["CURRENT_SPEND"],
                "New Spend": new_spend,
                "Current ROAS": roas,
                "Projected Revenue": proj_rev,
                "Projected Conversions": int(proj_conv),
                "Projected ROAS": proj_rev / max(new_spend, 1),
            })

        proj_df = pd.DataFrame(projected)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Projected Revenue", f"${proj_df['Projected Revenue'].sum():,.0f}")
        with col2:
            st.metric("Total Projected Conversions", f"{proj_df['Projected Conversions'].sum():,}")
        with col3:
            overall_roas = proj_df["Projected Revenue"].sum() / max(total_budget, 1)
            st.metric("Blended ROAS", f"{overall_roas:.2f}x")

        fig = px.bar(proj_df, x="Channel", y=["Current Spend", "New Spend"],
                     barmode="group", title="Budget Allocation: Current vs Projected")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Projected Performance Table")
        st.dataframe(proj_df.style.format({
            "Current Spend": "${:,.0f}", "New Spend": "${:,.0f}",
            "Current ROAS": "{:.2f}x", "Projected Revenue": "${:,.0f}",
            "Projected ROAS": "{:.2f}x"
        }), use_container_width=True)
