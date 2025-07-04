import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    layout="wide",
    page_title="Motorcycle Safety Insights Dashboard"
)

# Title
st.markdown("<h1 style='text-align: center;'>🏍️ MOTORCYCLE SAFETY INSIGHTS DASHBOARD</h1>", unsafe_allow_html=True)
st.markdown("---")

# ---- METRICS SECTION ----
st.markdown("### Key Safety Indicators")
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric(label="Helmet Compliance Rate (%)", value="78%")
with kpi2:
    st.metric(label="Total Motorcycle Detections", value="1,242")
with kpi3:
    st.metric(label="Child Passengers Detected", value="67")

st.markdown("---")

# ---- TWO-COLUMN LAYOUT ----
left_col, right_col = st.columns([2, 1], gap="large")

# LEFT: Latest Frame
with left_col:
    st.subheader("📸 Latest Detected Frame")
    st.image("latest_frame.jpg", caption="Most recent detection", use_column_width=True)

# RIGHT: Charts Stacked Vertically
st.subheader("🚨 Violation Types")
bar_data = pd.DataFrame({
    'Violation': ['No Helmet', 'Overloaded', 'Wrong Lane', 'No Mirrors'],
    'Count': [130, 55, 22, 150]
})
fig_bar = px.bar(bar_data, x='Violation', y='Count', text='Count', color='Violation')
fig_bar.update_traces(textposition='outside')
fig_bar.update_layout(showlegend=False)
st.plotly_chart(fig_bar, use_container_width=True)
with right_col:
    # Pie Chart
    st.subheader("🪞 Mirror Status Breakdown")
    pie_data = pd.DataFrame({
        'Mirror Status': ['Both', 'Left Only', 'Right Only', 'None'],
        'Count': [520, 110, 90, 150]
    })
    fig_pie = px.pie(pie_data, names='Mirror Status', values='Count', hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

    # Line Chart
    st.subheader("⏱️ Helmet Usage Over Time")
    line_data = pd.DataFrame({
        'Date': pd.date_range(start="2025-05-28", periods=7),
        'Helmet Usage Rate (%)': [55, 60, 63, 70, 74, 76, 78]
    })
    fig_line = px.line(line_data, x='Date', y='Helmet Usage Rate (%)', markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

    # Bar Chart
    
