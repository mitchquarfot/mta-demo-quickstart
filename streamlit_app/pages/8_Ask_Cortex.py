import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connection import run_query

st.title("Ask Cortex - Natural Language Analytics")
st.markdown("Ask questions about your attribution data in plain English.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sql" in msg:
            with st.expander("View SQL"):
                st.code(msg["sql"], language="sql")
        if "data" in msg:
            st.dataframe(msg["data"])

prompt = st.chat_input("Ask about your attribution data...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                safe_prompt = prompt.replace("'", "''")
                result = run_query(f"""
                    SELECT SNOWFLAKE.CORTEX.COMPLETE(
                        'mistral-large2',
                        'You are an ad-tech analytics expert. Given this question about multi-touch attribution data, '
                        || 'write a SQL query against these tables: '
                        || 'MTA_DEMO.ANALYTICS.ATTRIBUTION_RESULTS (columns: CONVERSION_ID, TOUCHPOINT_ID, CHANNEL, CAMPAIGN_ID, CAMPAIGN_NAME, ADVERTISER_ID, CONVERSION_TYPE, CONVERSION_TIMESTAMP, MODEL_TYPE, ATTRIBUTION_WEIGHT, ATTRIBUTED_REVENUE), '
                        || 'MTA_DEMO.ANALYTICS.CHANNEL_PERFORMANCE (columns: MODEL_TYPE, CHANNEL, CAMPAIGN_ID, IMPRESSIONS, SPEND, CLICKS, ATTRIBUTED_CONVERSIONS, ATTRIBUTED_REVENUE, CTR, ROAS, CPA), '
                        || 'MTA_DEMO.ANALYTICS.CAMPAIGN_DAILY_METRICS (columns: REPORT_DATE, CAMPAIGN_ID, CHANNEL, IMPRESSIONS, SPEND, CLICKS, CONVERSIONS, ATTRIBUTED_REVENUE, MODEL_TYPE). '
                        || 'All column names are UPPERCASE and do not need quoting. '
                        || 'Question: ' || '{safe_prompt}'
                        || ' Return ONLY the SQL query, no explanation.'
                    ) AS response
                """)
                sql = result["RESPONSE"].iloc[0].strip()
                if sql.startswith("```"):
                    sql = sql.split("\n", 1)[1].rsplit("```", 1)[0].strip()

                st.code(sql, language="sql")

                try:
                    data = run_query(sql)
                    st.dataframe(data, use_container_width=True)
                    st.session_state.messages.append({
                        "role": "assistant", "content": "Here are the results:",
                        "sql": sql, "data": data
                    })
                except Exception as e:
                    st.error(f"SQL execution error: {e}")
                    st.session_state.messages.append({
                        "role": "assistant", "content": f"Generated SQL but got error: {e}",
                        "sql": sql
                    })
            except Exception as e:
                st.error(f"Error: {e}")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})
