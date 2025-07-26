import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import yfinance as yf
import threading
from collections import deque

# Global data storage (in-memory)
price_data = {}
data_lock = threading.Lock()

def fetch_live_data(symbols):
    """Fetch current prices for given symbols"""
    try:
        # Create yfinance tickers object
        tickers = yf.Tickers(' '.join(symbols))
        
        current_time = datetime.now()
        prices = {}
        
        for symbol in symbols:
            try:
                ticker = tickers.tickers[symbol]
                # Get current price from info
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                
                if current_price:
                    prices[symbol] = {
                        'timestamp': current_time,
                        'price': round(float(current_price), 2),
                        'symbol': symbol
                    }
                else:
                    # Fallback: get from history
                    hist = ticker.history(period='1d', interval='1m')
                    if not hist.empty:
                        prices[symbol] = {
                            'timestamp': current_time,
                            'price': round(float(hist['Close'].iloc[-1]), 2),
                            'symbol': symbol
                        }
            except Exception as e:
                st.sidebar.error(f"Error fetching {symbol}: {str(e)}")
                continue
        
        return prices
    
    except Exception as e:
        st.sidebar.error(f"Data fetch error: {str(e)}")
        return {}

def update_price_data(symbols, max_points=50):
    """Update global price data storage"""
    global price_data
    
    new_prices = fetch_live_data(symbols)
    
    with data_lock:
        for symbol, data in new_prices.items():
            if symbol not in price_data:
                price_data[symbol] = deque(maxlen=max_points)
            
            price_data[symbol].append(data)

def get_dataframe():
    """Convert stored data to DataFrame"""
    with data_lock:
        if not price_data:
            return pd.DataFrame()
        
        all_data = []
        for symbol, data_points in price_data.items():
            all_data.extend(list(data_points))
        
        return pd.DataFrame(all_data)

# Page config
st.set_page_config(
    page_title="StreamDash",
    page_icon="📈",
    layout="wide"
)

# Initialize session state
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
    st.session_state.symbols = ['AAPL', 'SPY', 'MSFT', 'TSLA']
    st.session_state.refresh_interval = 10  # seconds
    st.session_state.auto_refresh = False

# Title
st.title("📈 StreamDash - Financial Data")

# Sidebar controls
st.sidebar.header("Settings")

# Symbol management
st.sidebar.subheader("Symbols")
symbols_input = st.sidebar.text_input(
    "Symbols (comma-separated):", 
    value=','.join(st.session_state.symbols)
)
st.session_state.symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]

# Refresh controls
st.sidebar.subheader("Data Refresh")
refresh_interval = st.sidebar.slider("Refresh interval (seconds):", 5, 60, st.session_state.refresh_interval)
st.session_state.refresh_interval = refresh_interval

auto_refresh = st.sidebar.checkbox("Auto-refresh", value=st.session_state.auto_refresh)
st.session_state.auto_refresh = auto_refresh

# Manual refresh button
if st.sidebar.button("🔄 Refresh Now"):
    with st.spinner("Fetching live data..."):
        update_price_data(st.session_state.symbols)
    st.session_state.last_update = datetime.now()
    st.rerun()

# Auto-refresh logic
if auto_refresh:
    time_since_update = (datetime.now() - st.session_state.last_update).total_seconds()
    if time_since_update >= refresh_interval:
        with st.spinner("Updating..."):
            update_price_data(st.session_state.symbols)
        st.session_state.last_update = datetime.now()
        st.rerun()

# Get current data
df = get_dataframe()

# If no data, fetch initial data
if df.empty:
    st.info("Fetching initial data...")
    with st.spinner("Loading..."):
        update_price_data(st.session_state.symbols)
    df = get_dataframe()
    st.session_state.last_update = datetime.now()

# Create tabs for different views
tab1, tab2 = st.tabs(["📊 Charts", "📋 Data"])

with tab1:
    if not df.empty:
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
            delta=f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}"
        )
    else:
        st.warning("No data available. Check symbols and try refreshing.")

with tab2:
    st.subheader("Raw Data")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data to display")

# Status
st.sidebar.markdown("---")
if auto_refresh:
    st.sidebar.success(f"🔄 Auto-refresh: ON ({refresh_interval}s)")
else:
    st.sidebar.info("🔄 Auto-refresh: OFF")

if not df.empty:
    st.sidebar.info(f"📊 Data points: {len(df)}")
    st.sidebar.info(f"🕐 Last update: {st.session_state.last_update.strftime('%H:%M:%S')}")

st.sidebar.markdown("---")
st.sidebar.caption("StreamDash MVP v0.1")

# Auto-refresh placeholder (triggers rerun)
if st.session_state.auto_refresh:
    time.sleep(1)  # Small delay to prevent excessive CPU usage
    placeholder = st.empty()
    placeholder.empty()