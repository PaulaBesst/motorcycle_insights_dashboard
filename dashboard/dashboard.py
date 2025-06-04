import streamlit as st
import pandas as pd
import plotly.express as px

# Page setup
st.set_page_config(layout="wide", page_title="Motorcycle Safety Insights Dashboard")

# Title
st.markdown("""
    <h1 style='text-align: center;'>🏍️ MOTORCYCLE SAFETY INSIGHTS DASHBOARD</h1>
""", unsafe_allow_html=True)

# ---- METRICS ----
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
        <div style='font-size: 1.8em; font-weight: bold;'>HELMET COMPLIANCE RATE (%)</div>
        <div style='font-size: 3.0em; color: #1f77b4;'>78%</div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div style='font-size: 1.8em; font-weight: bold;'>TOTAL MOTORCYCLE DETECTIONS</div>
        <div style='font-size: 3.0em; color: #ff7f0e;'>1,242</div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
        <div style='font-size: 1.8em; font-weight: bold;'>CHILD PASSENGERS DETECTED</div>
        <div style='font-size: 3.0em; color: #2ca02c;'>67</div>
    """, unsafe_allow_html=True)

# ---- FRAME + CHARTS SECTION ----
left_col, right_col = st.columns([2 ,1.5])

# Latest Detected Frame
with left_col:
    st.subheader("LATEST DETECTED FRAME")
    st.image("latest_frame.jpg", width=1330)  # Reduced image size

# Right column: Pie + Line Chart
with right_col:
    # Pie Chart - Mirror Status
    st.subheader("PIE CHART OF MIRROR STATUS")
    pie_data = pd.DataFrame({
        'Mirror Status': ['Both', 'Left Only', 'Right Only', 'None'],
        'Count': [520, 110, 90, 150]
    })
    fig_pie = px.pie(pie_data, names='Mirror Status', values='Count', hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

    # Line Chart - Helmet Usage Over Time
    st.subheader("LINE CHART OF HELMET USAGE")
    line_data = pd.DataFrame({
        'Date': pd.date_range(start="2025-05-28", periods=7),
        'Helmet Usage Rate (%)': [55, 60, 63, 70, 74, 76, 78]
    })
    fig_line = px.line(line_data, x='Date', y='Helmet Usage Rate (%)', markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

