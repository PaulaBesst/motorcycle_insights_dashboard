import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import base64
import io
from PIL import Image

import os

port = int(os.environ.get("PORT", 8050))

# Create dummy data (replace with actual data loading)
def create_dummy_data():
    np.random.seed(42)  # For reproducible data
    dates = pd.date_range(start='2024-01-01 07:00:00', periods=168, freq='1H')  # 1 week of hourly data
    
    data = []
    for i, date in enumerate(dates):
        # Create realistic patterns
        hour = date.hour
        base_compliance = 0.6 + 0.3 * np.sin((hour - 6) * np.pi / 12)  # Higher compliance during peak hours
        noise = np.random.normal(0, 0.15)
        compliance_rate = max(0.1, min(0.95, base_compliance + noise))
        
        total_detections = np.random.poisson(12) + 5  # 5-25 detections per period
        helmet_compliance = int(total_detections * compliance_rate)
        child_passengers = np.random.poisson(1.5) if np.random.random() < 0.4 else 0
        
        # Mirror status: no mirror, left mirror, right mirror
        mirror_probs = np.random.dirichlet([2, 3, 4])  # More likely to have mirrors
        mirror_counts = np.random.multinomial(total_detections, mirror_probs)
        no_mirror = mirror_counts[0]
        left_mirror = mirror_counts[1]
        right_mirror = mirror_counts[2]
        both_mirrors = mirror_counts[1] + mirror_counts[2]  # Count of riders with at least one mirror


        data.append({
            'timestamp': date,
            'helmet_compliance': helmet_compliance,
            'total_detections': total_detections,
            'child_passengers': child_passengers,
            'no_mirror': no_mirror,
            'left_mirror': left_mirror,
            'right_mirror': right_mirror,
            'both_mirrors': both_mirrors,
            'time_window': f"{date.strftime('%H:%M')}-{(date + timedelta(hours=1)).strftime('%H:%M')}",
            'hour': hour,
            'day_of_week': date.strftime('%A')
        })
    
    return pd.DataFrame(data)

# Load data
df = create_dummy_data()

# Calculate metrics
df['helmet_compliance_rate'] = (df['helmet_compliance'] / df['total_detections'] * 100).round(1)
df['child_passenger_ratio'] = (df['child_passengers'] / df['total_detections'] * 100).round(1)
df['mirror_coverage_rate'] = ((df['left_mirror'] + df['right_mirror'] + df['both_mirrors']) / df['total_detections'] * 100).round(1)
df['safety_score'] = (df['helmet_compliance_rate'] * 0.6 + df['mirror_coverage_rate'] * 0.4).round(1)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define custom CSS styles
custom_styles = {
    'card': {
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'padding': '25px',
        'borderRadius': '20px',
        'margin': '10px',
        'boxShadow': '0 10px 30px rgba(0,0,0,0.3)',
        'border': '1px solid rgba(255,255,255,0.1)',
        'backdropFilter': 'blur(10px)'
    },
    'metric_card': {
        'background': 'linear-gradient(135deg, #2d3748 0%, #4a5568 100%)',
        'padding': '30px',
        'borderRadius': '20px',
        'margin': '10px',
        'boxShadow': '0 15px 35px rgba(0,0,0,0.4)',
        'border': '2px solid rgba(255,255,255,0.1)',
        'backdropFilter': 'blur(15px)',
        'position': 'relative',
        'overflow': 'hidden',
        'flex': '1',
        'minWidth': '200px'
    },
    'chart_card': {
        'background': 'linear-gradient(135deg, #1a202c 0%, #2d3748 100%)',
        'padding': '25px',
        'borderRadius': '20px',
        'margin': '10px',
        'boxShadow': '0 20px 40px rgba(0,0,0,0.5)',
        'border': '1px solid rgba(255,255,255,0.1)',
        'backdropFilter': 'blur(10px)'
    },
    'image_frame': {
        'background': 'linear-gradient(135deg, #1a202c 0%, #2d3748 100%)',
        'padding': '20px',
        'borderRadius': '20px',
        'margin': '10px',
        'boxShadow': '0 20px 40px rgba(0,0,0,0.5)',
        'border': '2px solid rgba(255,255,255,0.1)',
        'position': 'relative'
    }
}

# Define the layout
app.layout = html.Div([
    # Header with gradient background
    html.Div([
        html.Div([
            html.H1("🏍️ MOTORCYCLE SAFETY INSIGHTS", 
                    style={'textAlign': 'center', 'color': '#ffffff', 'fontWeight': 'bold', 
                           'fontSize': '32px', 'margin': '0', 'textShadow': '0 2px 10px rgba(0,0,0,0.5)'}),
            html.P("Real-time traffic monitoring and safety analytics", 
                   style={'textAlign': 'center', 'color': '#e2e8f0', 'fontSize': '16px', 'margin': '10px 0 0 0'})
        ], style={'padding': '30px'})
    ], style={'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
              'boxShadow': '0 5px 20px rgba(0,0,0,0.3)'}),
    
    # Main container
    html.Div([
        # Top row - Enhanced key metrics with icons (evenly distributed)
        html.Div([
            # Helmet compliance rate
            html.Div([
                html.Div([
                    html.Div(" ", style={'fontSize': '40px', 'marginBottom': '10px'}),
                    html.H3("HELMET COMPLIANCE", style={'color': '#ffffff', 'fontSize': '14px', 'textAlign': 'center', 'marginBottom': '5px', 'fontWeight': '600'}),
                    html.Div(id='helmet-compliance-metric', style={'color': '#00ff88', 'fontSize': '42px', 'fontWeight': 'bold', 'textAlign': 'center', 'textShadow': '0 0 20px rgba(0,255,136,0.5)'}),
                    html.Div(id='helmet-trend', style={'color': '#a0aec0', 'fontSize': '12px', 'textAlign': 'center', 'marginTop': '5px'})
                ], style={'textAlign': 'center'})
            ], style=custom_styles['metric_card']),
            
            # Total detections
            html.Div([
                html.Div([
                    html.Div(" ", style={'fontSize': '40px', 'marginBottom': '10px'}),
                    html.H3("TOTAL DETECTIONS", style={'color': '#ffffff', 'fontSize': '14px', 'textAlign': 'center', 'marginBottom': '5px', 'fontWeight': '600'}),
                    html.Div(id='total-detections-metric', style={'color': '#00b4ff', 'fontSize': '42px', 'fontWeight': 'bold', 'textAlign': 'center', 'textShadow': '0 0 20px rgba(0,180,255,0.5)'}),
                    html.Div(id='detection-trend', style={'color': '#a0aec0', 'fontSize': '12px', 'textAlign': 'center', 'marginTop': '5px'})
                ], style={'textAlign': 'center'})
            ], style=custom_styles['metric_card']),
            
            # Child passenger ratio
            html.Div([
                html.Div([
                    html.Div(" ", style={'fontSize': '40px', 'marginBottom': '10px'}),
                    html.H3("CHILD PASSENGER RATIO", style={'color': '#ffffff', 'fontSize': '14px', 'textAlign': 'center', 'marginBottom': '5px', 'fontWeight': '600'}),
                    html.Div(id='child-ratio-metric', style={'color': '#ffb800', 'fontSize': '42px', 'fontWeight': 'bold', 'textAlign': 'center', 'textShadow': '0 0 20px rgba(255,184,0,0.5)'}),
                    html.Div(id='child-trend', style={'color': '#a0aec0', 'fontSize': '12px', 'textAlign': 'center', 'marginTop': '5px'})
                ], style={'textAlign': 'center'})
            ], style=custom_styles['metric_card']),
            
            # Safety score
            html.Div([
                html.Div([
                    html.Div(" ", style={'fontSize': '40px', 'marginBottom': '10px'}),
                    html.H3("SAFETY SCORE", style={'color': '#ffffff', 'fontSize': '14px', 'textAlign': 'center', 'marginBottom': '5px', 'fontWeight': '600'}),
                    html.Div(id='safety-score-metric', style={'color': '#ff6b6b', 'fontSize': '42px', 'fontWeight': 'bold', 'textAlign': 'center', 'textShadow': '0 0 20px rgba(255,107,107,0.5)'}),
                    html.Div(id='safety-trend', style={'color': '#a0aec0', 'fontSize': '12px', 'textAlign': 'center', 'marginTop': '5px'})
                ], style={'textAlign': 'center'})
            ], style=custom_styles['metric_card']),
        ], style={'display': 'flex', 'gap': '10px', 'marginBottom': '20px'}),
        
        # Control panel
        html.Div([
            html.Div([
                html.H3("📅 TIME RANGE SELECTOR", style={'color': '#ffffff', 'fontSize': '16px', 'marginBottom': '15px', 'fontWeight': '600'}),
                html.Div([
                    html.Button("Last 24 Hours", id='btn-24h', className='time-btn', 
                               style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#4299e1', 'color': 'white', 'border': 'none', 'borderRadius': '10px', 'cursor': 'pointer'}),
                    html.Button("Last Week", id='btn-week', className='time-btn',
                               style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#4299e1', 'color': 'white', 'border': 'none', 'borderRadius': '10px', 'cursor': 'pointer'}),
                    html.Button("All Time", id='btn-all', className='time-btn',
                               style={'margin': '5px', 'padding': '10px 20px', 'backgroundColor': '#4299e1', 'color': 'white', 'border': 'none', 'borderRadius': '10px', 'cursor': 'pointer'})
                ], style={'marginTop': '15px'})
            ], style=custom_styles['chart_card'])
        ], style={'marginBottom': '20px'}),
        
        # Middle row - Image and status
        html.Div([
            # Latest detected frame with your image
            html.Div([
                html.H3("LATEST DETECTED FRAME", style={'color': '#ffffff', 'fontSize': '18px', 'marginBottom': '15px', 'fontWeight': '600'}),
                html.Div([
                    html.Img(
                        id='latest-frame',
                        src='data:image/png;base64,',  # Will be updated with actual image
                        style={
                            'width': '100%',
                            'height': 'auto',
                            'maxHeight': '400px',
                            'objectFit': 'contain',
                            'borderRadius': '15px',
                            'border': '2px solid rgba(255,255,255,0.1)'
                        }
                    )
                ], style={'textAlign': 'center'})
            ], style={**custom_styles['image_frame'], 'flex': '2'}),
            
            # Quick stats and alerts
            html.Div([
                # Mirror status
                html.Div([
                    html.H3("MIRROR STATUS", style={'color': '#ffffff', 'fontSize': '16px', 'marginBottom': '15px', 'fontWeight': '600'}),
                    dcc.Graph(id='mirror-status-chart', style={'height': '280px'})
                ], style={**custom_styles['chart_card'], 'marginBottom': '15px'}),
                
                # Live alerts
                html.Div([
                    html.H3("LIVE ALERTS", style={'color': '#ffffff', 'fontSize': '16px', 'marginBottom': '15px', 'fontWeight': '600'}),
                    html.Div(id='live-alerts', style={'color': '#e2e8f0', 'fontSize': '14px'})
                ], style=custom_styles['chart_card'])
            ], style={'flex': '1', 'margin': '10px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': '20px'}),
        
        # Bottom row - Enhanced charts
        html.Div([
            # Helmet compliance heatmap by hour and day with dropdown
            html.Div([
                html.Div([
                    html.H3("HELMET COMPLIANCE vs. NON-COMPLIANCE", style={'color': '#ffffff', 'fontSize': '18px', 'marginBottom': '15px', 'fontWeight': '600', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Dropdown(
                            id='heatmap-axis-dropdown',
                            options=[
                                {'label': 'Hours', 'value': 'hours'},
                                {'label': 'Days of Week', 'value': 'days'}
                            ],
                            value='hours',
                            style={'width': '120px', 'color': '#000', 'fontSize': '14px'}
                        )
                    ], style={'float': 'right', 'marginTop': '10px'})
                ], style={'clearfix': 'both', 'marginBottom': '15px'}),
                dcc.Graph(id='compliance-heatmap')
            ], style={**custom_styles['chart_card'], 'flex': '1'}),
            
            # Helmet compliance trends with dropdown
            html.Div([
                html.Div([
                    html.H3("HELMET COMPLIANCE TRENDS", style={'color': '#ffffff', 'fontSize': '18px', 'marginBottom': '15px', 'fontWeight': '600', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Dropdown(
                            id='trend-axis-dropdown',
                            options=[
                                {'label': 'Hours', 'value': 'hours'},
                                {'label': 'Days of Week', 'value': 'days'}
                            ],
                            value='hours',
                            style={'width': '120px', 'color': '#000', 'fontSize': '14px'}
                        )
                    ], style={'float': 'right', 'marginTop': '10px'})
                ], style={'clearfix': 'both', 'marginBottom': '15px'}),
                dcc.Graph(id='helmet-compliance-trends')
            ], style={**custom_styles['chart_card'], 'flex': '1'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': '20px'}),
        
        # Additional insights row
        html.Div([
            # Detection patterns over time
            html.Div([
                html.H3("DETECTION PATTERNS OVER TIME", style={'color': '#ffffff', 'fontSize': '18px', 'marginBottom': '15px', 'fontWeight': '600'}),
                dcc.Graph(id='detection-patterns')
            ], style={**custom_styles['chart_card'], 'flex': '2'}),
            
            # Top insights
            html.Div([
                html.H3("💡 KEY INSIGHTS", style={'color': '#ffffff', 'fontSize': '16px', 'marginBottom': '15px', 'fontWeight': '600'}),
                html.Div(id='key-insights', style={'color': '#e2e8f0', 'fontSize': '14px', 'lineHeight': '1.6'})
            ], style={**custom_styles['chart_card'], 'flex': '1'})
        ], style={'display': 'flex', 'flexWrap': 'wrap'})
        
    ], style={'background': 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)', 'minHeight': '100vh', 'padding': '20px'}),
    
    # Store components for time range selection
    dcc.Store(id='selected-time-range', data='all')
    
], style={'margin': '0', 'padding': '0', 'fontFamily': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'})

# Function to encode image for display
def encode_image_for_display():
    # Create a placeholder image with road scene
    # In real implementation, you'd load your actual image here
    try:
        # You can replace this with your actual image loading code
        img = Image.open("latest_frame.jpg")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except:
        return "data:image/png;base64,"

# Callback for time range buttons
@callback(
    Output('selected-time-range', 'data'),
    [Input('btn-24h', 'n_clicks'),
     Input('btn-week', 'n_clicks'),
     Input('btn-all', 'n_clicks')],
    prevent_initial_call=True
)
def update_time_range(btn_24h, btn_week, btn_all):
    ctx = dash.callback_context
    if not ctx.triggered:
        return 'all'
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'btn-24h':
        return '24h'
    elif button_id == 'btn-week':
        return 'week'
    else:
        return 'all'

# Function to filter data based on time range
def filter_data_by_time_range(time_range):
    if time_range == '24h':
        cutoff_date = df['timestamp'].max() - timedelta(hours=24)
        return df[df['timestamp'] >= cutoff_date]
    elif time_range == 'week':
        cutoff_date = df['timestamp'].max() - timedelta(days=7)
        return df[df['timestamp'] >= cutoff_date]
    else:
        return df

# Callbacks for updating charts and metrics
@callback(
    [Output('helmet-compliance-metric', 'children'),
     Output('total-detections-metric', 'children'),
     Output('child-ratio-metric', 'children'),
     Output('safety-score-metric', 'children'),
     Output('helmet-trend', 'children'),
     Output('detection-trend', 'children'),
     Output('child-trend', 'children'),
     Output('safety-trend', 'children'),
     Output('mirror-status-chart', 'figure'),
     Output('compliance-heatmap', 'figure'),
     Output('helmet-compliance-trends', 'figure'),
     Output('detection-patterns', 'figure'),
     Output('live-alerts', 'children'),
     Output('key-insights', 'children'),
     Output('latest-frame', 'src')],
    [Input('selected-time-range', 'data'),
     Input('heatmap-axis-dropdown', 'value'),
     Input('trend-axis-dropdown', 'value')]
)
def update_dashboard(time_range, heatmap_axis, trend_axis):
    # Filter data based on time range
    filtered_df = filter_data_by_time_range(time_range)
    
    # Calculate metrics
    avg_helmet_compliance = filtered_df['helmet_compliance_rate'].mean()
    total_detections = filtered_df['total_detections'].sum()
    avg_child_ratio = filtered_df['child_passenger_ratio'].mean()
    avg_safety_score = filtered_df['safety_score'].mean()
    
    # Calculate trends (simple comparison with previous period)
    helmet_trend = "📈 +2.3% vs last period"
    detection_trend = "📈 +15% vs last period"
    child_trend = "📉 -0.8% vs last period"
    safety_trend = "📈 +1.5% vs last period"
    
    # Mirror status pie chart with enhanced styling and fixed legend
    mirror_data = {
        'No Mirror': filtered_df['no_mirror'].sum(),
        'Left Mirror': filtered_df['left_mirror'].sum(),
        'Right Mirror': filtered_df['right_mirror'].sum(),
        'Both Mirrors': filtered_df['both_mirrors'].sum()
    }
    
    mirror_fig = go.Figure(data=[go.Pie(
        labels=list(mirror_data.keys()),
        values=list(mirror_data.values()),
        hole=0.4,
        marker_colors=['#ff6b6b', '#ffb800', '#00ff88', '4299e1'],
        textinfo='label+percent',
        textfont=dict(size=12, color='white'),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    mirror_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=11),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1,
            bgcolor="rgba(0,0,0,0)"
        ),
        margin=dict(l=0, r=80, t=0, b=0),
        height=250
    )
    
    # Helmet compliance vs. non-compliance stacked bar chart
    if heatmap_axis == 'hours':
        compliance_data = filtered_df.groupby('hour').agg({
            'helmet_compliance': 'sum',
            'total_detections': 'sum'
        }).reset_index()
        compliance_data['non_compliant'] = compliance_data['total_detections'] - compliance_data['helmet_compliance']
        x_values = compliance_data['hour']
        x_title = 'Hour of Day'
    else:
        compliance_data = filtered_df.groupby('day_of_week').agg({
            'helmet_compliance': 'sum',
            'total_detections': 'sum'
        }).reset_index()
        compliance_data['non_compliant'] = compliance_data['total_detections'] - compliance_data['helmet_compliance']
        x_values = compliance_data['day_of_week']
        x_title = 'Day of Week'

    # Stacked bar chart figure
    heatmap_fig = go.Figure()
    heatmap_fig.add_trace(go.Bar(
        x=x_values,
        y=compliance_data['helmet_compliance'],
        name='Helmet Compliant',
        marker_color='#ffb800'  # yellow-gold from your pie chart
    ))
    heatmap_fig.add_trace(go.Bar(
        x=x_values,
        y=compliance_data['non_compliant'],
        name='Non-compliant',
        marker_color='#ff6b6b'  # red from your pie chart
    ))

    # Layout for the stacked bar
    heatmap_fig.update_layout(
        barmode='stack',
        #title='Helmet Compliance vs. Non-compliance',
        xaxis=dict(title=x_title, gridcolor='#4a5568'),
        yaxis=dict(title='Number of Riders', gridcolor='#4a5568'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)"
        )
    )
    
    # Helmet compliance trends (line chart only)
    if trend_axis == 'hours':
        trend_data = filtered_df.groupby('hour')['helmet_compliance_rate'].mean().reset_index()
        trend_fig = go.Figure()
        trend_fig.add_trace(go.Scatter(
            x=trend_data['hour'],
            y=trend_data['helmet_compliance_rate'],
            mode='lines+markers',
            name='Compliance Rate',
            line=dict(color='#00ff88', width=4),
            marker=dict(size=8, color='#00ff88')
        ))
        trend_fig.update_layout(
            xaxis=dict(title='Hour of Day', gridcolor='#4a5568')
        )
    else:
        trend_data = filtered_df.groupby('day_of_week')['helmet_compliance_rate'].mean().reset_index()
        trend_fig = go.Figure()
        trend_fig.add_trace(go.Scatter(
            x=trend_data['day_of_week'],
            y=trend_data['helmet_compliance_rate'],
            mode='lines+markers',
            name='Compliance Rate',
            line=dict(color='#00ff88', width=4),
            marker=dict(size=8, color='#00ff88')
        ))
        trend_fig.update_layout(
            xaxis=dict(title='Day of Week', gridcolor='#4a5568')
        )
    
    trend_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        yaxis=dict(title='Compliance Rate (%)', gridcolor='#4a5568'),
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    # Detection patterns over time 
    detection_fig = go.Figure()
    detection_fig.add_trace(go.Scatter(
        x=filtered_df['timestamp'],
        y=filtered_df['total_detections'],
        mode='lines',
        name='Total Detections',
        line=dict(color='#00b4ff', width=2)
    ))
    detection_fig.add_trace(go.Scatter(
        x=filtered_df['timestamp'],
        y=filtered_df['helmet_compliance'],
        mode='lines',
        name='Helmet Compliance Count',
        line=dict(color='#00ff88', width=2)
    ))
    detection_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(title='Time', gridcolor='#4a5568'),
        yaxis=dict(title='Count', gridcolor='#4a5568'),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    # Live alerts
    alerts = []
    if avg_helmet_compliance < 50:
        alerts.append("🚨 Low helmet compliance detected!")
    if avg_child_ratio > 15:
        alerts.append("👶 High child passenger ratio observed")
    if avg_safety_score < 60:
        alerts.append("⚠️ Safety score below threshold")
    
    alert_display = html.Div([
        html.Div(alert, style={'marginBottom': '8px', 'padding': '8px', 'backgroundColor': 'rgba(255,107,107,0.1)', 'borderRadius': '5px'}) 
        for alert in alerts
    ]) if alerts else html.Div("✅ All systems normal", style={'color': '#00ff88'})
    
    # Key insights
    if trend_axis == 'hours':
        trend_data = filtered_df.groupby('hour')['helmet_compliance_rate'].mean()
        peak_hour = trend_data.idxmax()
        peak_detection_hour = filtered_df.groupby('hour')['total_detections'].sum().idxmax()
    else:
        trend_data = filtered_df.groupby('day_of_week')['helmet_compliance_rate'].mean()
        peak_hour = trend_data.idxmax()
        peak_detection_hour = filtered_df.groupby('day_of_week')['total_detections'].sum().idxmax()
    
    insights = [
        f"Average compliance rate: {avg_helmet_compliance:.1f}%",
        f"Peak detection {'hour' if trend_axis == 'hours' else 'day'}: {peak_detection_hour}",
        f"Best compliance {'hour' if trend_axis == 'hours' else 'day'}: {peak_hour}",
        f"Safety trend: {'Improving' if avg_safety_score > 60 else 'Needs attention'}"
    ]
    
    insight_display = html.Div([
        html.Div(insight, style={'marginBottom': '10px', 'padding': '5px 0'}) 
        for insight in insights
    ])
    
    # Image for latest frame
    image_src = encode_image_for_display()
    
    return (
        f"{avg_helmet_compliance:.1f}%",
        f"{total_detections:,}",
        f"{avg_child_ratio:.1f}%",
        f"{avg_safety_score:.1f}",
        helmet_trend,
        detection_trend,
        child_trend,
        safety_trend,
        mirror_fig,
        heatmap_fig,
        trend_fig,
        detection_fig,
        alert_display,
        insight_display,
        image_src
    )

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=port, debug=True, dev_tools_ui=False)

app = dash.Dash(__name__)
server = app.server  # This is important for deployment

