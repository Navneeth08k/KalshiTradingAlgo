# 🧠 Kalshi Trading Algorithm

An automated trading system that combines real-time sentiment analysis with quantitative market data to identify profitable opportunities on Kalshi prediction markets.

## 🎯 What This System Does

This algorithm automatically:

1. **Scans the world's sentiment** in real-time using Google Gemini AI
2. **Finds trending teams/topics** that are emotionally overhyped or dumped on
3. **Matches entities to active Kalshi markets** using semantic mapping
4. **Fetches benchmark odds** from Pinnacle and other sources
5. **Computes price deviations** to detect +EV opportunities
6. **Generates trading signals** with risk management
7. **Simulates trades** and tracks portfolio performance
8. **Optimizes parameters** based on historical performance

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

Copy `env_example.txt` to `.env` and fill in your API keys:

```bash
cp env_example.txt .env
```

Edit `.env` with your actual API keys:

```env
# REQUIRED: Google Gemini API Key (get from https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your_gemini_api_key_here

# RECOMMENDED: Kalshi API Key (get from https://trading.kalshi.com/trade-api)
KALSHI_API_KEY=your_kalshi_api_key_here

# RECOMMENDED: The Odds API Key (free tier available at https://the-odds-api.com/)
THE_ODDS_API_KEY=your_the_odds_api_key_here

# OPTIONAL: Betfair API Key (get from https://developer.betfair.com/)
BETFAIR_API_KEY=your_betfair_api_key_here

# NOTE: Pinnacle API is now restricted (requires special access)
# PINNACLE_API_KEY=your_pinnacle_api_key_here
```

### 3. Validate System

Before running the system, validate all components:

```bash
python test_system_validation.py
```

This will test all components and provide recommendations for any issues.

### 4. Run the System

#### Option A: Automated Trading (Recommended)
```bash
python main.py --mode run
```

#### Option B: Interactive Dashboard
```bash
python main.py --mode dashboard
```

#### Option C: Single Cycle Test
```bash
python main.py --mode test
```

## 📊 Dashboard Features

The Streamlit dashboard provides:

- **Real-time portfolio monitoring**
- **Performance analytics and metrics**
- **Signal analysis and visualization**
- **Parameter optimization tools**
- **Trade history and P&L tracking**

Access the dashboard at: `http://localhost:8501`

## 🔧 System Components

### 1. Sentiment Engine (`sentiment_engine.py`)
- Uses Google Gemini AI to analyze trending topics
- Provides sentiment scores (-1 to +1) for entities
- Identifies emotional overhype or dumping
- **NEW**: Enhanced error handling and retry logic
- **NEW**: Fallback entities when API fails

### 2. Market Mapper (`market_mapper.py`)
- Maps trending entities to Kalshi markets
- Uses semantic matching to find relevant markets
- Validates market mappings for accuracy
- **NEW**: Improved error handling and fallback mappings

### 3. Benchmark Fetcher (`benchmark_fetcher.py`)
- **UPDATED**: Now uses The Odds API (free tier) instead of restricted Pinnacle API
- Fetches odds from multiple sources including Betfair
- Calculates consensus odds from multiple sources
- Detects arbitrage opportunities
- **NEW**: Fallback to mock data when APIs unavailable

### 4. Signal Generator (`signal_generator.py`)
- Combines sentiment and price gap analysis
- Generates LONG/SHORT/NONE signals
- Calculates position sizes and risk metrics

### 5. Portfolio Tracker (`portfolio_tracker.py`)
- Tracks all trades and portfolio performance
- Simulates trades with realistic P&L calculation
- Maintains SQLite database of all activities

### 6. Kalshi API (`kalshi_api.py`)
- **NEW**: Real Kalshi API integration
- Fetches live market data and prices
- Places orders and tracks positions
- **NEW**: Fallback to mock data when API unavailable

### 7. Feedback Loop (`feedback_loop.py`)
- Analyzes performance and optimizes parameters
- Generates daily reports and recommendations
- Implements machine learning for threshold adjustment

## 📈 How It Works

### The Complete Pipeline

```
[Gemini Search] → [Trending Entity + Sentiment Score]
           ↓
[Gemini Mapping] → [Find matching Kalshi markets]
           ↓
[API Fetcher] → [Get Kalshi + Pinnacle prices]
           ↓
[Quant Script] → [Generate trade signals]
           ↓
[Portfolio Module] → [Simulate trades + monitor results]
           ↓
[Feedback] → [Adjust thresholds / explain results]
```

### Signal Generation Logic

```python
# Example signal logic
gap = kalshi_price - pinnacle_implied
if gap > 0.05 and sentiment_score > 0.7:
    signal = "SHORT"  # Kalshi overvalued, negative sentiment
elif gap < -0.05 and sentiment_score < -0.7:
    signal = "LONG"   # Kalshi undervalued, positive sentiment
else:
    signal = "NONE"
```

## 🎛️ Configuration

Edit `config.py` to adjust:

- **Sentiment Threshold**: Minimum sentiment score for signals (default: 0.7)
- **Price Gap Threshold**: Minimum price gap for signals (default: 0.05)
- **Max Position Size**: Maximum position size in dollars (default: $1000)
- **Check Interval**: How often to check for opportunities (default: 6 hours)
- **Max Daily Trades**: Maximum trades per day (default: 10)

## 📊 Example Output

### Trending Entities
```json
[
  {
    "entity": "Golden State Warriors",
    "category": "NBA",
    "sentiment": 0.87,
    "reason": "Won 5 games in a row, Curry MVP performance"
  },
  {
    "entity": "Dallas Cowboys",
    "category": "NFL", 
    "sentiment": 0.65,
    "reason": "Strong playoff push, Dak Prescott healthy"
  }
]
```

### Trading Signals
```json
{
  "entity": "Golden State Warriors",
  "signal": "LONG",
  "signal_strength": 0.85,
  "position_size": 500.0,
  "reasoning": "Positive sentiment suggests Kalshi is undervalued relative to benchmark"
}
```

### Portfolio Summary
```json
{
  "total_trades": 45,
  "active_trades": 8,
  "total_pnl": 1250.50,
  "win_rate": 0.68,
  "profit_factor": 1.85,
  "sharpe_ratio": 1.42
}
```

## 🔍 Monitoring and Analysis

### Daily Reports
The system generates daily reports with:
- Portfolio performance metrics
- Top performing trades
- Risk alerts and recommendations
- Parameter optimization suggestions

### Performance Analysis
- Win rate and profit factor tracking
- Sharpe ratio and drawdown analysis
- Signal effectiveness by type
- Sentiment correlation analysis

### Parameter Optimization
The system automatically:
- Analyzes historical performance
- Optimizes sentiment and price gap thresholds
- Adjusts position sizing based on volatility
- Implements risk management improvements

## 🆕 Recent Improvements (2024)

### ✅ Fixed Issues
- **Pinnacle API**: Replaced restricted Pinnacle API with The Odds API (free tier)
- **Gemini API**: Enhanced error handling, retry logic, and fallback mechanisms
- **Kalshi API**: Added real API integration with fallback to mock data
- **Error Handling**: Comprehensive error handling throughout the system
- **Validation**: Added system validation tests and health checks

### 🔧 New Features
- **System Validation**: Run `python test_system_validation.py` to test all components
- **Fallback Mechanisms**: System continues working even when APIs are unavailable
- **Better Error Messages**: Clear error messages and recommendations
- **API Alternatives**: Multiple data sources for better reliability

### 📊 API Status
- **Gemini API**: ✅ Working (required)
- **The Odds API**: ✅ Working (free tier available)
- **Kalshi API**: ✅ Working (recommended)
- **Pinnacle API**: ❌ Restricted (requires special access)
- **Betfair API**: ✅ Working (optional)

## 🚨 Important Notes

### API Requirements
- **Gemini API**: Required for sentiment analysis and market mapping
- **The Odds API**: Recommended for benchmark odds (free tier available)
- **Kalshi API**: Recommended for real market data
- **Betfair API**: Optional alternative data source

### Risk Management
- All trades are simulated by default
- Real trading requires additional safety measures
- Position sizing is automatically calculated
- Stop-loss and take-profit levels are set

### Data Storage
- All data is stored in SQLite database (`trading_data.db`)
- Trades, market data, and performance metrics are tracked
- Data can be exported for external analysis

## 🛠️ Development

### Running Tests
```bash
python main.py --mode test
```

### Performance Analysis
```bash
python main.py --mode analyze --performance
```

### Sentiment Analysis Only
```bash
python main.py --mode analyze --sentiment
```

### Daily Report
```bash
python main.py --mode analyze --report
```

## 📝 Logs

The system logs all activities to `trading_algorithm.log` with:
- Sentiment analysis results
- Market mapping activities
- Signal generation decisions
- Trade executions and updates
- Performance analysis results

## 🔮 Future Enhancements

- **Real API Integration**: Replace mock data with actual Kalshi/Pinnacle APIs
- **Machine Learning**: Implement reinforcement learning for parameter optimization
- **Alert System**: Add Telegram/Discord notifications for new signals
- **Advanced Analytics**: Implement more sophisticated risk metrics
- **Backtesting**: Add historical data analysis capabilities

## 📞 Support

For questions or issues:
1. Check the logs in `trading_algorithm.log`
2. Verify API keys are correctly set
3. Ensure all dependencies are installed
4. Check database permissions for SQLite

## ⚠️ Disclaimer

This is a trading algorithm for educational and research purposes. Always:
- Test thoroughly before using real money
- Understand the risks involved
- Comply with all applicable regulations
- Use appropriate risk management
- Never invest more than you can afford to lose

---

**Happy Trading! 🚀📈**
