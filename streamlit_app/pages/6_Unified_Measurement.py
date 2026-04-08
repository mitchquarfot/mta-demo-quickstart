import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connection import run_query

st.title("Unified Measurement: MTA vs MMM vs Incrementality")
st.markdown("### Triangulating truth across measurement methodologies")

st.subheader("MTA Channel Attribution (Linear Model)")
mta = run_query("""
    SELECT CHANNEL,
           SUM(ATTRIBUTED_REVENUE) AS MTA_REVENUE,
           COUNT(DISTINCT CONVERSION_ID) AS MTA_CONVERSIONS
    FROM MTA_DEMO.ANALYTICS.ATTRIBUTION_RESULTS
    WHERE MODEL_TYPE = 'linear'
    GROUP BY CHANNEL
    ORDER BY MTA_REVENUE DESC
""")

st.subheader("Incrementality Test Lift")
incr = run_query("SELECT * FROM MTA_DEMO.ANALYTICS.INCREMENTALITY_RESULTS")
st.dataframe(incr, use_container_width=True)

st.subheader("MMM Weekly Input (Log-Log Regression Data)")
mmm = run_query("""
    SELECT CHANNEL,
           SUM(SPEND) AS TOTAL_SPEND,
           SUM(ATTRIBUTED_REVENUE) AS TOTAL_REVENUE,
           CASE WHEN SUM(SPEND) > 0 THEN SUM(ATTRIBUTED_REVENUE) / SUM(SPEND) ELSE 0 END AS MMM_ROAS
    FROM MTA_DEMO.ANALYTICS.MMM_INPUT_WEEKLY
    GROUP BY CHANNEL
    ORDER BY TOTAL_SPEND DESC
""")

if not mta.empty and not mmm.empty:
    combined = mta.merge(mmm[["CHANNEL", "TOTAL_SPEND", "MMM_ROAS"]], on="CHANNEL", how="outer").fillna(0)
    combined["MTA_ROAS"] = combined["MTA_REVENUE"] / combined["TOTAL_SPEND"].replace(0, 1)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="MTA ROAS", x=combined["CHANNEL"], y=combined["MTA_ROAS"]))
    fig.add_trace(go.Bar(name="MMM ROAS", x=combined["CHANNEL"], y=combined["MMM_ROAS"]))
    fig.update_layout(barmode="group", title="ROAS Comparison: MTA vs MMM by Channel")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Measurement Triangulation Table")
    st.dataframe(combined.style.format({
        "MTA_REVENUE": "${:,.0f}", "TOTAL_SPEND": "${:,.0f}",
        "MTA_ROAS": "{:.2f}x", "MMM_ROAS": "{:.2f}x"
    }), use_container_width=True)

st.divider()
st.markdown("""
**Interpretation Guide:**
- **MTA** captures user-level touchpoint credit but misses cross-device/offline impact
- **MMM** captures macro channel effects but lacks user-level granularity
- **Incrementality** provides causal lift measurement but only for tested channels/geos
- When all three agree on a channel's contribution, confidence is highest
- Divergence signals measurement gaps (e.g., CTV shows high MMM impact but low MTA due to device graph gaps)
""")
