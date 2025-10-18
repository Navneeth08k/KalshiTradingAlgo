"""
Streamlit Dashboard for Trading Algorithm Monitoring
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import json

from trading_algorithm import TradingAlgorithm
from portfolio_tracker import PortfolioTracker
from feedback_loop import FeedbackLoop

class TradingDashboard:
    def __init__(self):
        """Initialize the dashboard"""
        self.algorithm = TradingAlgorithm()
        self.portfolio_tracker = PortfolioTracker()
        self.feedback_loop = FeedbackLoop()
    
    def run(self):
        """Run the Streamlit dashboard"""
        st.set_page_config(
            page_title="Kalshi Trading Algorithm Dashboard",
            page_icon="📈",
            layout="wide"
        )
        
        st.title("📈 Kalshi Trading Algorithm Dashboard")
        st.markdown("---")
        
        # Sidebar
        self.render_sidebar()
        
        # Main content
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", "💰 Portfolio", "📈 Performance", "🔍 Signals", "⚙️ Settings"
        ])
        
        with tab1:
            self.render_overview()
        
        with tab2:
            self.render_portfolio()
        
        with tab3:
            self.render_performance()
        
        with tab4:
            self.render_signals()
        
        with tab5:
            self.render_settings()
    
    def render_sidebar(self):
        """Render sidebar with controls"""
        st.sidebar.title("🎛️ Controls")
        
        # System status
        status = self.algorithm.get_system_status()
        if status.get("status") == "running":
            st.sidebar.success("🟢 System Running")
        else:
            st.sidebar.error("🔴 System Error")
        
        # Manual controls
        st.sidebar.subheader("Manual Actions")
        
        if st.sidebar.button("🔄 Run Full Cycle"):
            with st.spinner("Running full trading cycle..."):
                result = self.algorithm.run_full_cycle()
                if result.get("status") == "success":
                    st.sidebar.success("Cycle completed successfully")
                else:
                    st.sidebar.error(f"Cycle failed: {result.get('message')}")
        
        if st.sidebar.button("📊 Generate Report"):
            with st.spinner("Generating report..."):
                report = self.algorithm.run_daily_report()
                st.sidebar.success("Report generated")
        
        if st.sidebar.button("📈 Analyze Performance"):
            with st.spinner("Analyzing performance..."):
                analysis = self.algorithm.run_performance_analysis()
                st.sidebar.success("Analysis completed")
        
        # System info
        st.sidebar.subheader("System Info")
        st.sidebar.metric("Active Trades", status.get("active_trades", 0))
        st.sidebar.metric("Total P&L", f"${status.get('portfolio_summary', {}).get('total_pnl', 0):.2f}")
    
    def render_overview(self):
        """Render overview tab"""
        st.header("📊 System Overview")
        
        # Get system status
        status = self.algorithm.get_system_status()
        portfolio_summary = status.get("portfolio_summary", {})
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Trades",
                portfolio_summary.get("total_trades", 0),
                delta=None
            )
        
        with col2:
            st.metric(
                "Active Trades",
                portfolio_summary.get("active_trades", 0),
                delta=None
            )
        
        with col3:
            st.metric(
                "Total P&L",
                f"${portfolio_summary.get('total_pnl', 0):.2f}",
                delta=f"{portfolio_summary.get('total_pnl_percentage', 0):.1f}%"
            )
        
        with col4:
            st.metric(
                "Win Rate",
                f"{portfolio_summary.get('win_rate', 0)*100:.1f}%",
                delta=None
            )
        
        # Recent activity
        st.subheader("📈 Recent Activity")
        
        # Get recent trades
        try:
            conn = sqlite3.connect('trading_data.db')
            recent_trades = pd.read_sql_query('''
                SELECT entity, signal, entry_price, pnl, entry_timestamp, status
                FROM trades 
                ORDER BY entry_timestamp DESC 
                LIMIT 10
            ''', conn)
            conn.close()
            
            if not recent_trades.empty:
                st.dataframe(recent_trades, use_container_width=True)
            else:
                st.info("No trades found")
        except Exception as e:
            st.error(f"Error loading recent trades: {e}")
    
    def render_portfolio(self):
        """Render portfolio tab"""
        st.header("💰 Portfolio")
        
        # Portfolio summary
        portfolio_summary = self.portfolio_tracker.get_portfolio_summary()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Portfolio Summary")
            st.json(portfolio_summary)
        
        with col2:
            st.subheader("Active Trades")
            active_trades = self.portfolio_tracker.get_active_trades()
            
            if active_trades:
                df = pd.DataFrame(active_trades)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No active trades")
        
        # P&L Chart
        st.subheader("📈 P&L Over Time")
        
        try:
            conn = sqlite3.connect('trading_data.db')
            pnl_data = pd.read_sql_query('''
                SELECT exit_timestamp, pnl, pnl_percentage
                FROM trades 
                WHERE status = 'CLOSED' AND exit_timestamp IS NOT NULL
                ORDER BY exit_timestamp
            ''', conn)
            conn.close()
            
            if not pnl_data.empty:
                pnl_data['cumulative_pnl'] = pnl_data['pnl'].cumsum()
                
                fig = px.line(
                    pnl_data, 
                    x='exit_timestamp', 
                    y='cumulative_pnl',
                    title='Cumulative P&L Over Time'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No closed trades to display")
        except Exception as e:
            st.error(f"Error loading P&L data: {e}")
    
    def render_performance(self):
        """Render performance tab"""
        st.header("📈 Performance Analysis")
        
        # Performance metrics
        if st.button("🔄 Refresh Performance Data"):
            with st.spinner("Analyzing performance..."):
                performance = self.algorithm.run_performance_analysis()
                
                if performance.get("status") == "success":
                    st.success("Performance analysis completed")
                    
                    # Display performance metrics
                    perf_data = performance.get("performance", {})
                    if perf_data:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total P&L", f"${perf_data.get('total_pnl', 0):.2f}")
                            st.metric("Average P&L", f"${perf_data.get('avg_pnl', 0):.2f}")
                        
                        with col2:
                            st.metric("Win Rate", f"{perf_data.get('win_rate', 0)*100:.1f}%")
                            st.metric("Profit Factor", f"{perf_data.get('profit_factor', 0):.2f}")
                        
                        with col3:
                            st.metric("Sharpe Ratio", f"{perf_data.get('sharpe_ratio', 0):.2f}")
                            st.metric("Max Drawdown", f"{perf_data.get('max_drawdown', 0):.1f}%")
                    
                    # Recommendations
                    recommendations = performance.get("recommendations", [])
                    if recommendations:
                        st.subheader("💡 Recommendations")
                        for rec in recommendations:
                            st.info(rec)
                else:
                    st.error(f"Performance analysis failed: {performance.get('message')}")
    
    def render_signals(self):
        """Render signals tab"""
        st.header("🔍 Signal Analysis")
        
        # Run sentiment analysis
        if st.button("🔍 Analyze Current Signals"):
            with st.spinner("Analyzing signals..."):
                # Run sentiment analysis
                sentiment_result = self.algorithm.run_sentiment_analysis()
                
                if sentiment_result.get("status") == "success":
                    entities = sentiment_result.get("entities", [])
                    
                    if entities:
                        st.subheader("📊 Trending Entities")
                        df = pd.DataFrame(entities)
                        st.dataframe(df, use_container_width=True)
                        
                        # Sentiment distribution
                        fig = px.bar(
                            df, 
                            x='entity', 
                            y='sentiment',
                            title='Sentiment Scores by Entity',
                            color='sentiment',
                            color_continuous_scale='RdYlGn'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No trending entities found")
                else:
                    st.error(f"Sentiment analysis failed: {sentiment_result.get('message')}")
    
    def render_settings(self):
        """Render settings tab"""
        st.header("⚙️ System Settings")
        
        # Current configuration
        st.subheader("Current Configuration")
        
        config_data = {
            "Sentiment Threshold": Config.SENTIMENT_THRESHOLD,
            "Price Gap Threshold": Config.PRICE_GAP_THRESHOLD,
            "Max Position Size": Config.MAX_POSITION_SIZE,
            "Check Interval (hours)": Config.CHECK_INTERVAL_HOURS,
            "Max Daily Trades": Config.MAX_DAILY_TRADES
        }
        
        st.json(config_data)
        
        # Parameter optimization
        st.subheader("🔧 Parameter Optimization")
        
        if st.button("🎯 Optimize Parameters"):
            with st.spinner("Optimizing parameters..."):
                # Get performance data
                performance = self.algorithm.run_performance_analysis()
                
                if performance.get("status") == "success":
                    # Run optimization
                    optimization = self.feedback_loop.optimize_parameters(performance)
                    
                    if optimization.get("error"):
                        st.error(f"Optimization failed: {optimization.get('error')}")
                    else:
                        st.success("Parameter optimization completed")
                        
                        # Display optimization results
                        st.subheader("Optimization Results")
                        
                        current = optimization.get("current_thresholds", {})
                        optimized = optimization.get("optimized_thresholds", {})
                        changes = optimization.get("changes", {})
                        
                        opt_data = {
                            "Parameter": ["Sentiment Threshold", "Price Gap Threshold"],
                            "Current": [current.get("sentiment_threshold", 0), 
                                      current.get("price_gap_threshold", 0)],
                            "Optimized": [optimized.get("sentiment_threshold", 0), 
                                        optimized.get("price_gap_threshold", 0)],
                            "Change": [changes.get("sentiment_threshold", 0), 
                                     changes.get("price_gap_threshold", 0)]
                        }
                        
                        df = pd.DataFrame(opt_data)
                        st.dataframe(df, use_container_width=True)
                        
                        st.info(f"Optimization Confidence: {optimization.get('confidence', 0)*100:.1f}%")
                else:
                    st.error(f"Performance analysis failed: {performance.get('message')}")

if __name__ == "__main__":
    dashboard = TradingDashboard()
    dashboard.run()
