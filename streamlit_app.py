"""
streamlit_app.py — Text-to-SQL Engine UI
Run: streamlit run streamlit_app.py
"""

import streamlit as st
import httpx
import pandas as pd
import json

API_URL = "http://127.0.0.1:8000"

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Natural Language Business Intelligence & SQL Automation Tool",
    page_icon="🔍",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title   { font-size:2.2rem; font-weight:700; color:#1E3A5F; }
    .sub-title    { color:#555; font-size:1rem; margin-top:-10px; margin-bottom:20px; }
    .sql-box      { background:#1e1e1e; color:#d4d4d4; padding:16px; border-radius:8px;
                    font-family:monospace; font-size:0.9rem; white-space:pre-wrap; }
    .explain-box  { background:#EBF5FB; padding:14px; border-radius:8px;
                    border-left:4px solid #2E86C1; color:#1a1a1a; font-size:0.95rem; }
    .metric-card  { background:#F0F8FF; padding:12px 20px; border-radius:8px;
                    border:1px solid #BDD7EE; text-align:center; }
    .schema-box   { background:#f8f9fa; padding:14px; border-radius:8px;
                    font-family:monospace; font-size:0.8rem; color:#333;
                    max-height:300px; overflow-y:auto; }
    .history-item { background:#fafafa; border:1px solid #eee; border-radius:6px;
                    padding:8px 12px; margin-bottom:6px; cursor:pointer; font-size:0.9rem; }
    .badge        { display:inline-block; padding:2px 10px; border-radius:12px;
                    background:#1E3A5F; color:white; font-size:0.75rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Text-to-SQL Engine")
    st.caption("Powered by Groq AI (Llama 3.3) + FastAPI + SQLite")
    st.divider()

    # Schema viewer
    st.markdown("#### 📋 Database Schema")
    if st.button("Load Schema", use_container_width=True):
        try:
            r = httpx.get(f"{API_URL}/query/schema", timeout=10)
            st.session_state.schema = r.json()["schema_text"]
        except Exception as e:
            st.error(f"API not running: {e}")

    if "schema" in st.session_state:
        st.markdown(
            f'<div class="schema-box">{st.session_state.schema}</div>',
            unsafe_allow_html=True
        )

    st.divider()

    # Query history
    st.markdown("#### 🕘 Query History")
    if st.session_state.history:
        for i, h in enumerate(reversed(st.session_state.history[-8:])):
            if st.button(f"↩ {h[:45]}...", key=f"h{i}", use_container_width=True):
                st.session_state.prefill = h
    else:
        st.caption("No queries yet.")

    st.divider()

    # Sample questions
    st.markdown("#### 💡 Try These")
    samples = [
        "Show top 5 customers by total order value",
        "Which products are low in stock (under 50)?",
        "What is the total revenue per product category?",
        "List all pending or shipped orders",
        "How many orders were placed each month in 2024?",
        "Which customer has placed the most orders?",
    ]
    for q in samples:
        if st.button(q, use_container_width=True, key=q):
            st.session_state.prefill = q

# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🔍 Text-to-SQL Engine</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Ask a question in plain English → get SQL + results instantly</div>',
    unsafe_allow_html=True
)

# Input
prefill = st.session_state.get("prefill", "")
question = st.text_area(
    "Your question:",
    value=prefill,
    placeholder="e.g. Show me the top 5 customers by total spend",
    height=90,
    key="question_input",
)

col1, col2 = st.columns([1, 5])
with col1:
    run_btn = st.button("▶ Run Query", type="primary", use_container_width=True)
with col2:
    if st.button("🗑 Clear", use_container_width=False):
        st.session_state.last_result = None
        st.session_state.prefill = ""
        st.rerun()

# ── Query execution ────────────────────────────────────────────────────────────
if run_btn and question.strip():
    with st.spinner("🤖 Claude is generating SQL..."):
        try:
            resp = httpx.post(
                f"{API_URL}/query/",
                json={"question": question.strip()},
                timeout=30,
            )
            if resp.status_code == 200:
                result = resp.json()
                st.session_state.last_result = result
                # Add to history (avoid duplicates)
                if question not in st.session_state.history:
                    st.session_state.history.append(question)
                if "prefill" in st.session_state:
                    del st.session_state.prefill
            else:
                st.error(f"❌ Error {resp.status_code}: {resp.json().get('detail','Unknown error')}")
        except httpx.ConnectError:
            st.error("❌ Cannot connect to FastAPI. Make sure it's running: `uvicorn app.main:app --reload`")
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")

# ── Results ────────────────────────────────────────────────────────────────────
result = st.session_state.last_result
if result:
    st.divider()

    # Metrics row
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Rows Returned", result["row_count"])
    with m2:
        st.metric("Columns", len(result["columns"]))
    with m3:
        st.metric("Query Status", "✅ Success")

    st.divider()

    # SQL + Explanation side by side
    col_sql, col_exp = st.columns([1, 1])

    with col_sql:
        st.markdown("#### 🧠 Generated SQL")
        st.markdown(
            f'<div class="sql-box">{result["sql"]}</div>',
            unsafe_allow_html=True
        )
        st.caption("Generated by Groq (Llama 3.3) · Read-only · Safe")

    with col_exp:
        st.markdown("#### 💬 Plain-English Explanation")
        st.markdown(
            f'<div class="explain-box">{result["explanation"]}</div>',
            unsafe_allow_html=True
        )

    st.divider()

    # Results table
    st.markdown(f"#### 📊 Results  <span class='badge'>{result['row_count']} rows</span>",
                unsafe_allow_html=True)

    if result["rows"]:
        df = pd.DataFrame(result["rows"])
        st.dataframe(df, use_container_width=True, height=400)

        # Export
        col_a, col_b = st.columns([1, 5])
        with col_a:
            csv = df.to_csv(index=False).encode()
            st.download_button("⬇ Download CSV", csv, "query_results.csv", "text/csv")
        with col_b:
            st.download_button(
                "⬇ Download JSON",
                json.dumps(result["rows"], indent=2).encode(),
                "query_results.json",
                "application/json",
            )
    else:
        st.info("Query ran successfully but returned no rows.")
