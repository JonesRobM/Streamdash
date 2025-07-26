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

def fetch_historical_data(symbols, period='5d', interval='15m'):
    """Fetch historical data for given symbols"""
    try:
        tickers = yf.Tickers(' '.join(symbols))
        historical_data = {}
        
        for symbol in symbols:
            try:
                ticker = tickers.tickers[symbol]
                hist = ticker.history(period=period, interval=interval)
                
                if not hist.empty:
                    data_points = []
                    for timestamp, row in hist.iterrows():
                        # Convert timezone-aware timestamp to naive
                        if timestamp.tz is not None:
                            timestamp = timestamp.tz_localize(None)
                        
                        data_points.append({
                            'timestamp': timestamp.to_pydatetime(),
                            'price': round(float(row['Close']), 2),
                            'symbol': symbol,
                            'volume': int(row['Volume']) if not pd.isna(row['Volume']) else 0,
                            'is_historical': True
                        })
                    historical_data[symbol] = data_points
                    
            except Exception as e:
                st.sidebar.error(f"Error fetching historical data for {symbol}: {str(e)}")
                continue
        
        return historical_data
    
    except Exception as e:
        st.sidebar.error(f"Historical data fetch error: {str(e)}")
        return {}

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
                        'symbol': symbol,
                        'volume': info.get('volume', 0),
                        'is_historical': False
                    }
                else:
                    # Fallback: get from history
                    hist = ticker.history(period='1d', interval='1m')
                    if not hist.empty:
                        prices[symbol] = {
                            'timestamp': current_time,
                            'price': round(float(hist['Close'].iloc[-1]), 2),
                            'symbol': symbol,
                            'volume': int(hist['Volume'].iloc[-1]) if not pd.isna(hist['Volume'].iloc[-1]) else 0,
                            'is_historical': False
                        }
            except Exception as e:
                st.sidebar.error(f"Error fetching {symbol}: {str(e)}")
                continue
        
        return prices
    
    except Exception as e:
        st.sidebar.error(f"Data fetch error: {str(e)}")
        return {}

def initialize_symbol_data(symbol, max_points=200):
    """Initialize a symbol with historical data"""
    global price_data
    
    if symbol not in price_data:
        # Fetch historical data
        historical_data = fetch_historical_data([symbol])
        
        with data_lock:
            price_data[symbol] = deque(maxlen=max_points)
            
            if symbol in historical_data:
                # Add historical data points
                for data_point in historical_data[symbol]:
                    price_data[symbol].append(data_point)

def update_price_data(symbols, max_points=200):
    """Update global price data storage"""
    global price_data
    
    # Initialize any new symbols with historical data
    for symbol in symbols:
        if symbol not in price_data:
            initialize_symbol_data(symbol, max_points)
    
    # Fetch live data
    new_prices = fetch_live_data(symbols)
    
    with data_lock:
        for symbol, data in new_prices.items():
            if symbol in price_data:
                price_data[symbol].append(data)

def get_estimated_points(period, interval):
    """Estimate number of data points for period/interval combination"""
    period_days = {
        '1d': 1, '5d': 5, '1mo': 30, '3mo': 90, 
        '6mo': 180, '1y': 365, '2y': 730, '5y': 1825, 
        '10y': 3650, 'max': 7300  # Rough estimate for max
    }
    
    interval_per_day = {
        '1m': 390, '5m': 78, '15m': 26, '30m': 13, 
        '1h': 6.5, '1d': 1, '1wk': 0.14, '1mo': 0.03
    }
    
    days = period_days.get(period, 365)
    points_per_day = interval_per_day.get(interval, 1)
    
    estimated = int(days * points_per_day)
    
    if estimated > 1000:
        return f"~{estimated//1000}k"
    else:
        return f"~{estimated}"

def get_dataframe():
    """Convert stored data to DataFrame"""
    with data_lock:
        if not price_data:
            return pd.DataFrame()
        
        all_data = []
        for symbol, data_points in price_data.items():
            for data_point in list(data_points):
                # Ensure timestamp is timezone-naive
                timestamp = data_point['timestamp']
                if hasattr(timestamp, 'tz') and timestamp.tz is not None:
                    timestamp = timestamp.replace(tzinfo=None)
                
                data_copy = data_point.copy()
                data_copy['timestamp'] = timestamp
                all_data.append(data_copy)
        
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
    st.session_state.refresh_interval = 5  # Increased frequency to 5 seconds
    st.session_state.auto_refresh = True  # Enable auto-refresh by default
    st.session_state.historical_period = '5d'  # Back to 5 days for high frequency
    st.session_state.historical_interval = '1m'  # 1-minute intervals for maximum detail
    st.session_state.initialized_symbols = set()
    st.session_state.last_historical_period = '5d'
    st.session_state.last_historical_interval = '1m'

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
new_symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]

# Check if symbols changed
if new_symbols != st.session_state.symbols:
    st.session_state.symbols = new_symbols
    # Reset initialized symbols to force re-fetch of historical data
    st.session_state.initialized_symbols = set()
    if new_symbols:  # Only show message if symbols exist
        st.sidebar.info("📥 New symbols detected. Click 'Refresh Now' to load historical data.")

# Historical data settings
st.sidebar.subheader("Historical Data")
historical_period = st.sidebar.selectbox(
    "Historical period:",
    options=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max'],
    index=['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max'].index(st.session_state.historical_period)
)
st.session_state.historical_period = historical_period

# Smart interval suggestions based on period
if historical_period in ['1d', '5d']:
    interval_options = ['1m', '5m', '15m', '30m', '1h']
    default_interval = '15m'
elif historical_period in ['1mo', '3mo']:
    interval_options = ['15m', '30m', '1h', '1d']
    default_interval = '1h'
else:  # 6mo and longer
    interval_options = ['1h', '1d', '1wk', '1mo']
    default_interval = '1d'

# Ensure current interval is valid for the period
if st.session_state.historical_interval not in interval_options:
    st.session_state.historical_interval = default_interval

historical_interval = st.sidebar.selectbox(
    "Historical interval:",
    options=interval_options,
    index=interval_options.index(st.session_state.historical_interval)
)
st.session_state.historical_interval = historical_interval

# Show data estimate
st.sidebar.caption(f"Estimated data points: {get_estimated_points(historical_period, historical_interval)}")

# Add note about refreshing for new settings
if historical_period != st.session_state.get('last_historical_period') or historical_interval != st.session_state.get('last_historical_interval'):
    st.sidebar.info("⚙️ Historical settings changed. Refresh to apply to new symbols.")
    st.session_state.last_historical_period = historical_period
    st.session_state.last_historical_interval = historical_interval

# Refresh controls
st.sidebar.subheader("Data Refresh")
refresh_interval = st.sidebar.slider("Refresh interval (seconds):", 1, 30, st.session_state.refresh_interval)
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
        symbol_data = symbol_data.sort_values('timestamp')
        
        # Separate historical and live data
        historical_data = symbol_data[symbol_data['is_historical'] == True]
        live_data = symbol_data[symbol_data['is_historical'] == False]
        
        # Create plotly chart
        fig = go.Figure()
        
        # Add historical data
        if not historical_data.empty:
            fig.add_trace(go.Scatter(
                x=historical_data['timestamp'],
                y=historical_data['price'],
                mode='lines',
                name=f'{selected_symbol} Historical',
                line=dict(width=2, color='lightblue'),
                opacity=0.7
            ))
        
        # Add live data
        if not live_data.empty:
            fig.add_trace(go.Scatter(
                x=live_data['timestamp'],
                y=live_data['price'],
                mode='lines+markers',
                name=f'{selected_symbol} Live',
                line=dict(width=3, color='red'),
                marker=dict(size=6, color='red')
            ))
        
        fig.update_layout(
            title=f"{selected_symbol} Price Over Time (Historical + Live)",
            xaxis_title="Time",
            yaxis_title="Price ($)",
            height=500,
            showlegend=True,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Current price and statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            current_price = symbol_data['price'].iloc[-1]
            st.metric(
                label=f"{selected_symbol} Current Price",
                value=f"${current_price}",
                delta=f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}"
            )
        
        with col2:
            if len(symbol_data) > 1:
                price_change = symbol_data['price'].iloc[-1] - symbol_data['price'].iloc[-2]
                price_change_pct = (price_change / symbol_data['price'].iloc[-2]) * 100
                st.metric(
                    label="Change",
                    value=f"${price_change:.2f}",
                    delta=f"{price_change_pct:.2f}%"
                )
        
        with col3:
            daily_high = symbol_data['price'].max()
            daily_low = symbol_data['price'].min()
            st.metric(
                label="Range",
                value=f"${daily_low:.2f} - ${daily_high:.2f}",
                delta=f"Spread: ${daily_high - daily_low:.2f}"
            )
        
        # Data summary
        st.subheader("Data Summary")
        hist_count = len(historical_data) if not historical_data.empty else 0
        live_count = len(live_data) if not live_data.empty else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"📊 Historical points: {hist_count}")
        with col2:
            st.success(f"🔴 Live points: {live_count}")
        with col3:
            st.info(f"📈 Total points: {len(symbol_data)}")
            
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
    next_refresh = refresh_interval - (datetime.now() - st.session_state.last_update).total_seconds()
    st.sidebar.success(f"🔄 Auto-refresh: ON ({refresh_interval}s)")
    if next_refresh > 0:
        st.sidebar.caption(f"Next refresh in: {next_refresh:.1f}s")
else:
    st.sidebar.info("🔄 Auto-refresh: OFF")

if not df.empty:
    total_points = len(df)
    historical_points = len(df[df['is_historical'] == True])
    live_points = len(df[df['is_historical'] == False])
    
    st.sidebar.info(f"📊 Total data points: {total_points}")
    st.sidebar.info(f"📈 Historical: {historical_points}")
    st.sidebar.success(f"🔴 Live: {live_points}")
    st.sidebar.info(f"🕐 Last update: {st.session_state.last_update.strftime('%H:%M:%S')}")
    
    # Show refresh rate
    if live_points > 1:
        st.sidebar.caption(f"⚡ Effective refresh: {refresh_interval}s")
    
    # Show symbols status
    st.sidebar.subheader("Symbols Status")
    for symbol in st.session_state.symbols:
        symbol_df = df[df['symbol'] == symbol]
        if not symbol_df.empty:
            symbol_hist = len(symbol_df[symbol_df['is_historical'] == True])
            symbol_live = len(symbol_df[symbol_df['is_historical'] == False])
            st.sidebar.caption(f"{symbol}: {symbol_hist}📈 + {symbol_live}🔴")
        else:
            st.sidebar.caption(f"{symbol}: No data")

st.sidebar.markdown("---")
st.sidebar.caption("StreamDash MVP v0.1")

# Auto-refresh placeholder (triggers rerun)
if st.session_state.auto_refresh:
    time.sleep(0.5)  # Reduced delay for more responsive updates
    placeholder = st.empty()
    placeholder.empty()