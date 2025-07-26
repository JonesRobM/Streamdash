import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Page config
st.set_page_config(
    page_title="StreamDash",
    page_icon="📈",
    layout="wide"
)

# Title
st.title("📈 StreamDash - Financial Data")

# Create mock data for testing
def generate_mock_data():
    """Generate sample financial data for testing"""
    symbols = ['AAPL', 'SPY', 'MSFT']
    data = []
    
    base_time = datetime.now() - timedelta(minutes=30)
    
    for i in range(30):  # 30 data points
        timestamp = base_time + timedelta(minutes=i)
        for symbol in symbols:
            # Mock price with some variation
            base_price = {'AAPL': 150, 'SPY': 400, 'MSFT': 300}[symbol]
            price = base_price + (i * 0.5) + ((-1)**i * 2)  # Simple trend + noise
            
            data.append({
                'timestamp': timestamp,
                'symbol': symbol,
                'price': round(price, 2)
            })
    
    return pd.DataFrame(data)

# Generate and display data
df = generate_mock_data()

# Create tabs for different views
tab1, tab2 = st.tabs(["📊 Charts", "📋 Data"])

with tab1:
    # Symbol selector
    symbols = df['symbol'].unique()
    selected_symbol = st.selectbox("Select Symbol:", symbols)
    
    # Filter data for selected symbol
    symbol_data = df[df['symbol'] == selected_symbol].copy()
    
    # Create plotly chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=symbol_data['timestamp'],
        y=symbol_data['price'],
        mode='lines+markers',
        name=selected_symbol,
        line=dict(width=2)
    ))
    
    fig.update_layout(
        title=f"{selected_symbol} Price Over Time",
        xaxis_title="Time",
        yaxis_title="Price ($)",
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Current price display
    current_price = symbol_data['price'].iloc[-1]
    st.metric(
        label=f"{selected_symbol} Current Price",
        value=f"${current_price}",
        delta="Live data coming soon..."
    )

with tab2:
    st.subheader("Raw Data")
    st.dataframe(df, use_container_width=True)

# Status
st.sidebar.header("Settings")
st.sidebar.info("🔄 Auto-refresh: Coming soon")
st.sidebar.info("📧 Alerts: Coming soon")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("StreamDash MVP v0.1")