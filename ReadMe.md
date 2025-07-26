# 📈 StreamDash - Real-Time Financial Dashboard

A lightweight, real-time financial data visualization dashboard built with Streamlit and yfinance. Monitor stock prices, ETFs, and market data with interactive charts and live updates.

## ✨ Features

- **📊 Real-time price tracking** - Live updates every 1-30 seconds
- **📈 Historical data visualization** - Configurable periods (1d to max) with multiple intervals
- **🎛️ Interactive charts** - Zoom, pan, hover for detailed price information
- **⚡ Auto-refresh capability** - Hands-free monitoring with configurable intervals
- **🔄 Multi-symbol support** - Track multiple stocks/ETFs simultaneously
- **🎨 Clean, modern UI** - Dark theme with intuitive controls
- **📱 Responsive design** - Works on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/streamdash.git
   cd streamdash
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

5. **Open your browser** to `http://localhost:8501`

## 📦 Dependencies

```txt
streamlit==1.29.0
yfinance==0.2.18
pandas==2.1.4
plotly==5.17.0
```

## 🎮 Usage

### Basic Operation

1. **Launch the app** and wait for initial data loading
2. **Select symbols** in the sidebar (comma-separated, e.g., `AAPL,SPY,MSFT`)
3. **Configure historical period** (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max)
4. **Set refresh interval** (1-30 seconds) using the slider
5. **Enable auto-refresh** for continuous updates
6. **Switch between symbols** using the dropdown in the main view

### Advanced Features

#### Historical Data Configuration
- **Period**: Choose timeframe for historical data
- **Interval**: Select data granularity (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
- **Smart suggestions**: App automatically suggests appropriate intervals based on selected period

#### Real-time Monitoring
- **Live data overlay**: Red markers show real-time updates over historical data
- **Automatic refresh**: Configurable intervals from 1-30 seconds
- **Status indicators**: Track data points, refresh timing, and symbol status

#### Interactive Charts
- **Zoom and pan**: Click and drag to explore data
- **Hover details**: Mouse over points for exact values and timestamps
- **Legend control**: Toggle historical vs live data visibility

## ⚙️ Configuration

### Symbol Configuration
Add any valid Yahoo Finance ticker symbols:
- **Stocks**: `AAPL`, `GOOGL`, `MSFT`, `TSLA`
- **ETFs**: `SPY`, `QQQ`, `VTI`, `ARKK`
- **Indices**: `^GSPC`, `^IXIC`, `^DJI`
- **Commodities**: `GC=F` (Gold), `CL=F` (Oil)
- **Crypto**: `BTC-USD`, `ETH-USD`

### Performance Tuning
- **Refresh interval**: Balance between data freshness and API limits
- **Historical period**: Longer periods require more memory
- **Symbol count**: More symbols = longer refresh times

## 🌐 Deployment

### Streamlit Community Cloud (Recommended)

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Initial StreamDash deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select `main.py` as the main file
   - Deploy and share your app

### Local Network Access

Run with network access for other devices:
```bash
streamlit run main.py --server.address 0.0.0.0
```

## 📊 Data Sources

- **Primary**: Yahoo Finance via `yfinance` library
- **Update frequency**: Real-time quotes (15-30 second delay)
- **Historical range**: Up to maximum available history per symbol
- **Market coverage**: Global markets supported by Yahoo Finance

## ⚠️ Limitations

- **Data delay**: Real-time quotes have 15-30 second delay
- **API limits**: Yahoo Finance may rate-limit excessive requests
- **Market hours**: Live updates only during market hours
- **Historical limits**: Some interval/period combinations have restricted data

## 🛠️ Technical Architecture

```
StreamDash/
├── main.py              # Main Streamlit application
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── NEXT_STEPS.md       # Development roadmap
```

### Key Components
- **Data fetching**: `yfinance` for market data
- **Storage**: In-memory with `collections.deque` (thread-safe)
- **Visualization**: `plotly` for interactive charts
- **UI**: `streamlit` for web interface
- **Threading**: Safe concurrent data updates

## 🐛 Troubleshooting

### Common Issues

**"No data available"**
- Check symbol spelling (use Yahoo Finance format)
- Verify market hours for live data
- Try refreshing manually

**Slow loading**
- Reduce number of symbols
- Increase refresh interval
- Choose shorter historical periods

**Connection errors**
- Check internet connection
- Yahoo Finance may be temporarily unavailable
- Reduce request frequency

### Debug Mode
Run with verbose logging:
```bash
streamlit run main.py --logger.level debug
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests (when available)
python -m pytest

# Format code
black main.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **yfinance** - Yahoo Finance data access
- **Streamlit** - Web application framework
- **Plotly** - Interactive charting library
- **Yahoo Finance** - Market data provider

## 📈 Performance Notes

- **Memory usage**: ~50-100MB for typical usage
- **CPU usage**: Low during idle, spikes during refresh
- **Network**: ~1-5KB per symbol per update
- **Scalability**: Tested with up to 10 symbols simultaneously

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/streamdash/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/streamdash/discussions)
- **Documentation**: This README and inline code comments

---

**⭐ Star this repo if StreamDash helps with your financial monitoring!**