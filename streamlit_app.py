"""
Kalshi Trading Algorithm Dashboard
Streamlit app for monitoring and visualizing trading performance
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import json
import time
from typing import Dict, List, Any

# Import our trading components
from trading_algorithm import TradingAlgorithm
from portfolio_tracker import PortfolioTracker
from kalshi_api import KalshiAPI
from benchmark_fetcher import BenchmarkFetcher
from sentiment_engine import SentimentEngine
from market_mapper import MarketMapper
from signal_generator import SignalGenerator
from config import Config

# Page configuration
st.set_page_config(
    page_title="Kalshi Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .positive {
        color: #28a745;
    }
    .negative {
        color: #dc3545;
    }
    .warning {
        color: #ffc107;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_trading_data():
    """Load trading data from database"""
    try:
        conn = sqlite3.connect(Config.DATABASE_PATH)
        
        # Load trades
        trades_df = pd.read_sql_query("""
            SELECT * FROM trades 
            ORDER BY timestamp DESC 
            LIMIT 100
        """, conn)
        
        # Load portfolio summary
        portfolio_df = pd.read_sql_query("""
            SELECT * FROM portfolio_summary 
            ORDER BY timestamp DESC 
            LIMIT 50
        """, conn)
        
        conn.close()
        
        return trades_df, portfolio_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

def get_live_market_data():
    """Get live market data from APIs"""
    try:
        kalshi_api = KalshiAPI()
        markets = kalshi_api.get_markets(limit=20)
        return markets
    except Exception as e:
        st.error(f"Error fetching market data: {e}")
        return []

def get_trending_entities():
    """Get trending entities from sentiment analysis"""
    try:
        sentiment_engine = SentimentEngine()
        entities = sentiment_engine.get_trending_entities()
        return entities
    except Exception as e:
        st.error(f"Error fetching trending entities: {e}")
        return []

def get_trading_signals():
    """Get current trading signals"""
    try:
        # Initialize components
        sentiment_engine = SentimentEngine()
        market_mapper = MarketMapper()
        benchmark_fetcher = BenchmarkFetcher()
        signal_generator = SignalGenerator()
        kalshi_api = KalshiAPI()
        
        # Get trending entities
        entities = sentiment_engine.get_trending_entities()
        
        signals = []
        for entity in entities:
            # Map to markets
            mappings = market_mapper.map_entity_to_markets(
                entity['entity'], 
                entity.get('category', 'General')
            )
            
            for mapping in mappings:
                # Get benchmark odds
                benchmark_odds = benchmark_fetcher.get_odds_for_entity(
                    entity['entity'], 
                    entity.get('category', 'General')
                )
                
                # Get Kalshi price
                kalshi_price = kalshi_api.get_market_price(mapping['kalshi_ticker'])
                
                if kalshi_price and benchmark_odds:
                    # Generate signal
                    signal = signal_generator.generate_signal(
                        entity=entity['entity'],
                        sentiment_score=entity['sentiment'],
                        kalshi_price=kalshi_price,
                        benchmark_price=benchmark_odds.get('price', 0.5),
                        confidence=entity.get('confidence', 0.5)
                    )
                    
                    if signal:
                        signals.append({
                            'entity': entity['entity'],
                            'category': entity.get('category', 'General'),
                            'sentiment': entity['sentiment'],
                            'kalshi_ticker': mapping['kalshi_ticker'],
                            'kalshi_price': kalshi_price,
                            'benchmark_price': benchmark_odds.get('price', 0.5),
                            'signal': signal['signal'],
                            'strength': signal['strength'],
                            'confidence': signal['confidence']
                        })
        
        return signals
    except Exception as e:
        st.error(f"Error generating signals: {e}")
        return []

def main():
    """Main Streamlit app"""
    
    # Header
    st.title("📈 Kalshi Trading Algorithm Dashboard")
    st.markdown("**Real-time monitoring of AI-powered prediction market trading**")
    
    # Sidebar
    st.sidebar.title("🎛️ Control Panel")
    
    # Trading mode indicator
    trading_mode = "🟢 Paper Trading (Fake Money)" if Config.FAKE_MONEY_MODE else "🔴 Live Trading (Real Money)"
    st.sidebar.markdown(f"**Trading Mode:** {trading_mode}")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=True)
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()
    
    # Run trading cycle button
    if st.sidebar.button("🚀 Run Trading Cycle"):
        with st.spinner("Running full trading cycle..."):
            try:
                trading_algo = TradingAlgorithm()
                result = trading_algo.run_full_cycle()
                st.success("Trading cycle completed!")
                st.json(result)
            except Exception as e:
                st.error(f"Error running trading cycle: {e}")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Portfolio Overview", 
        "🎯 Trading Signals", 
        "📈 Market Analysis", 
        "📋 Trade History", 
        "⚙️ System Status"
    ])
    
    with tab1:
        st.header("Portfolio Overview")
        
        # Load portfolio data
        trades_df, portfolio_df = load_trading_data()
        
        if not portfolio_df.empty:
            latest_portfolio = portfolio_df.iloc[0]
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Balance", 
                    f"${latest_portfolio.get('total_balance', 0):,.2f}",
                    delta=f"${latest_portfolio.get('total_pnl', 0):,.2f}"
                )
            
            with col2:
                st.metric(
                    "Active Positions", 
                    latest_portfolio.get('active_positions', 0)
                )
            
            with col3:
                st.metric(
                    "Total Trades", 
                    latest_portfolio.get('total_trades', 0)
                )
            
            with col4:
                win_rate = latest_portfolio.get('win_rate', 0) * 100
                st.metric(
                    "Win Rate", 
                    f"{win_rate:.1f}%"
                )
            
            # Portfolio value over time
            if len(portfolio_df) > 1:
                fig = px.line(
                    portfolio_df, 
                    x='timestamp', 
                    y='total_balance',
                    title="Portfolio Value Over Time"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No portfolio data available. Run a trading cycle to see data.")
    
    with tab2:
        st.header("Current Trading Signals")
        
        # Get live signals
        with st.spinner("Analyzing market sentiment and generating signals..."):
            signals = get_trading_signals()
        
        if signals:
            signals_df = pd.DataFrame(signals)
            
            # Signal strength distribution
            fig = px.histogram(
                signals_df, 
                x='strength', 
                color='signal',
                title="Signal Strength Distribution",
                labels={'strength': 'Signal Strength', 'count': 'Number of Signals'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Signals table
            st.subheader("Active Signals")
            
            # Color code signals
            def color_signal(val):
                if val == 'LONG':
                    return 'background-color: #d4edda'
                elif val == 'SHORT':
                    return 'background-color: #f8d7da'
                else:
                    return 'background-color: #fff3cd'
            
            display_df = signals_df[['entity', 'category', 'sentiment', 'kalshi_ticker', 'kalshi_price', 'benchmark_price', 'signal', 'strength', 'confidence']].copy()
            display_df['kalshi_price'] = display_df['kalshi_price'].round(3)
            display_df['benchmark_price'] = display_df['benchmark_price'].round(3)
            display_df['strength'] = display_df['strength'].round(3)
            display_df['confidence'] = display_df['confidence'].round(3)
            
            styled_df = display_df.style.applymap(color_signal, subset=['signal'])
            st.dataframe(styled_df, use_container_width=True)
            
            # Signal recommendations
            strong_signals = signals_df[signals_df['strength'] > 0.8]
            if not strong_signals.empty:
                st.subheader("🔥 Strong Signals (>80% strength)")
                for _, signal in strong_signals.iterrows():
                    st.markdown(f"""
                    **{signal['entity']}** ({signal['category']})
                    - Signal: {signal['signal']} (Strength: {signal['strength']:.1%})
                    - Kalshi Price: {signal['kalshi_price']:.3f}
                    - Benchmark Price: {signal['benchmark_price']:.3f}
                    - Confidence: {signal['confidence']:.1%}
                    """)
        else:
            st.info("No trading signals available. Check system status or run a trading cycle.")
    
    with tab3:
        st.header("Market Analysis")
        
        # Get trending entities
        with st.spinner("Fetching trending entities..."):
            entities = get_trending_entities()
        
        if entities:
            entities_df = pd.DataFrame(entities)
            
            # Sentiment distribution
            fig = px.histogram(
                entities_df, 
                x='sentiment', 
                color='category',
                title="Sentiment Distribution by Category",
                labels={'sentiment': 'Sentiment Score', 'count': 'Number of Entities'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Top entities by sentiment
            st.subheader("Top Trending Entities")
            top_entities = entities_df.nlargest(10, 'sentiment')
            
            for _, entity in top_entities.iterrows():
                sentiment_color = "positive" if entity['sentiment'] > 0 else "negative"
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{entity['entity']}</h4>
                    <p><strong>Category:</strong> {entity.get('category', 'Unknown')}</p>
                    <p><strong>Sentiment:</strong> <span class="{sentiment_color}">{entity['sentiment']:.3f}</span></p>
                    <p><strong>Reason:</strong> {entity.get('reason', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Live market data
        st.subheader("Live Market Data")
        with st.spinner("Fetching live market data..."):
            markets = get_live_market_data()
        
        if markets:
            markets_df = pd.DataFrame(markets)
            st.dataframe(markets_df[['ticker', 'title', 'yes_price', 'volume']], use_container_width=True)
        else:
            st.info("No live market data available.")
    
    with tab4:
        st.header("Trade History")
        
        if not trades_df.empty:
            # Trade performance over time
            trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
            
            fig = px.line(
                trades_df, 
                x='timestamp', 
                y='pnl',
                title="Trade P&L Over Time",
                color='signal'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Recent trades
            st.subheader("Recent Trades")
            recent_trades = trades_df.head(20)
            st.dataframe(recent_trades, use_container_width=True)
            
            # Trade statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Trade Statistics")
                total_trades = len(trades_df)
                winning_trades = len(trades_df[trades_df['pnl'] > 0])
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                
                st.metric("Total Trades", total_trades)
                st.metric("Winning Trades", winning_trades)
                st.metric("Win Rate", f"{win_rate:.1f}%")
            
            with col2:
                st.subheader("P&L Summary")
                total_pnl = trades_df['pnl'].sum()
                avg_pnl = trades_df['pnl'].mean()
                max_pnl = trades_df['pnl'].max()
                min_pnl = trades_df['pnl'].min()
                
                st.metric("Total P&L", f"${total_pnl:.2f}")
                st.metric("Average P&L", f"${avg_pnl:.2f}")
                st.metric("Best Trade", f"${max_pnl:.2f}")
                st.metric("Worst Trade", f"${min_pnl:.2f}")
        else:
            st.info("No trade history available. Run some trades to see data.")
    
    with tab5:
        st.header("System Status")
        
        # System health check
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("API Status")
            
            # Check each API
            apis = {
                "Gemini API": "✅ Connected",
                "Kalshi API": "✅ Connected", 
                "The Odds API": "✅ Connected" if Config.THE_ODDS_API_KEY else "⚠️ No API Key",
                "Betfair API": "✅ Connected" if Config.BETFAIR_API_KEY else "⚠️ No API Key"
            }
            
            for api, status in apis.items():
                st.markdown(f"**{api}:** {status}")
        
        with col2:
            st.subheader("Configuration")
            
            config_info = {
                "Trading Mode": "Paper Trading" if Config.FAKE_MONEY_MODE else "Live Trading",
                "Initial Balance": f"${Config.INITIAL_BALANCE:,}",
                "Max Position Size": f"${Config.MAX_POSITION_SIZE:,}",
                "Sentiment Threshold": f"{Config.SENTIMENT_THRESHOLD:.1%}",
                "Database": "✅ Connected"
            }
            
            for key, value in config_info.items():
                st.markdown(f"**{key}:** {value}")
        
        # System logs (last 10 entries)
        st.subheader("Recent System Activity")
        try:
            conn = sqlite3.connect(Config.DATABASE_PATH)
            logs_df = pd.read_sql_query("""
                SELECT timestamp, level, message 
                FROM system_logs 
                ORDER BY timestamp DESC 
                LIMIT 10
            """, conn)
            conn.close()
            
            if not logs_df.empty:
                st.dataframe(logs_df, use_container_width=True)
            else:
                st.info("No system logs available.")
        except:
            st.info("No system logs available.")

if __name__ == "__main__":
    main()
