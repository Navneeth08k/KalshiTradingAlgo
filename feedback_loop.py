"""
Feedback Loop - Performance analysis and parameter optimization
"""
import sqlite3
import json
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from config import Config

class FeedbackLoop:
    def __init__(self):
        """Initialize the feedback loop"""
        self.logger = logging.getLogger(__name__)
        self.db_path = Config.DATABASE_PATH
    
    def analyze_performance(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze trading performance over the specified period
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get all closed trades in the period
            cursor.execute('''
                SELECT * FROM trades 
                WHERE status = 'CLOSED' AND exit_timestamp > ?
                ORDER BY exit_timestamp ASC
            ''', (start_date,))
            
            trades = cursor.fetchall()
            conn.close()
            
            if not trades:
                return {"error": "No trades found in the specified period"}
            
            # Calculate performance metrics
            performance = self._calculate_performance_metrics(trades)
            
            # Analyze signal effectiveness
            signal_analysis = self._analyze_signal_effectiveness(trades)
            
            # Analyze sentiment correlation
            sentiment_analysis = self._analyze_sentiment_correlation(trades)
            
            return {
                "period_days": days,
                "total_trades": len(trades),
                "performance": performance,
                "signal_analysis": signal_analysis,
                "sentiment_analysis": sentiment_analysis,
                "recommendations": self._generate_recommendations(performance, signal_analysis)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing performance: {e}")
            return {"error": str(e)}
    
    def _calculate_performance_metrics(self, trades: List[Tuple]) -> Dict[str, Any]:
        """Calculate key performance metrics"""
        if not trades:
            return {}
        
        # Extract P&L data
        pnl_values = [trade[10] for trade in trades if trade[10] is not None]  # pnl column
        pnl_percentages = [trade[11] for trade in trades if trade[11] is not None]  # pnl_percentage column
        
        if not pnl_values:
            return {}
        
        # Basic metrics
        total_pnl = sum(pnl_values)
        avg_pnl = np.mean(pnl_values)
        total_return = sum(pnl_percentages)
        avg_return = np.mean(pnl_percentages)
        
        # Win rate
        winning_trades = [pnl for pnl in pnl_values if pnl > 0]
        win_rate = len(winning_trades) / len(pnl_values)
        
        # Average win/loss
        avg_win = np.mean(winning_trades) if winning_trades else 0
        losing_trades = [pnl for pnl in pnl_values if pnl < 0]
        avg_loss = np.mean(losing_trades) if losing_trades else 0
        
        # Risk metrics
        returns_std = np.std(pnl_percentages)
        sharpe_ratio = avg_return / returns_std if returns_std > 0 else 0
        
        # Drawdown calculation
        cumulative_returns = np.cumsum(pnl_percentages)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = cumulative_returns - running_max
        max_drawdown = np.min(drawdown)
        
        # Profit factor
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        return {
            "total_pnl": total_pnl,
            "avg_pnl": avg_pnl,
            "total_return": total_return,
            "avg_return": avg_return,
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "volatility": returns_std
        }
    
    def _analyze_signal_effectiveness(self, trades: List[Tuple]) -> Dict[str, Any]:
        """Analyze effectiveness of different signal types"""
        signal_performance = {}
        
        for trade in trades:
            signal = trade[3]  # signal column
            pnl = trade[10] if trade[10] is not None else 0  # pnl column
            
            if signal not in signal_performance:
                signal_performance[signal] = {
                    "trades": 0,
                    "total_pnl": 0,
                    "wins": 0,
                    "losses": 0
                }
            
            signal_performance[signal]["trades"] += 1
            signal_performance[signal]["total_pnl"] += pnl
            
            if pnl > 0:
                signal_performance[signal]["wins"] += 1
            elif pnl < 0:
                signal_performance[signal]["losses"] += 1
        
        # Calculate metrics for each signal type
        for signal in signal_performance:
            data = signal_performance[signal]
            data["win_rate"] = data["wins"] / data["trades"] if data["trades"] > 0 else 0
            data["avg_pnl"] = data["total_pnl"] / data["trades"] if data["trades"] > 0 else 0
        
        return signal_performance
    
    def _analyze_sentiment_correlation(self, trades: List[Tuple]) -> Dict[str, Any]:
        """Analyze correlation between sentiment scores and performance"""
        sentiment_pnl_pairs = []
        
        for trade in trades:
            # Extract sentiment-related data (assuming it's stored in reasoning or as metadata)
            # This would need to be adapted based on how sentiment data is stored
            signal_strength = trade[9] if trade[9] is not None else 0  # signal_strength column
            pnl = trade[10] if trade[10] is not None else 0  # pnl column
            
            sentiment_pnl_pairs.append((signal_strength, pnl))
        
        if len(sentiment_pnl_pairs) < 2:
            return {"correlation": 0, "sample_size": len(sentiment_pnl_pairs)}
        
        # Calculate correlation
        sentiments, pnls = zip(*sentiment_pnl_pairs)
        correlation = np.corrcoef(sentiments, pnls)[0, 1]
        
        return {
            "correlation": correlation,
            "sample_size": len(sentiment_pnl_pairs),
            "interpretation": self._interpret_correlation(correlation)
        }
    
    def _interpret_correlation(self, correlation: float) -> str:
        """Interpret correlation coefficient"""
        if abs(correlation) < 0.1:
            return "No correlation"
        elif abs(correlation) < 0.3:
            return "Weak correlation"
        elif abs(correlation) < 0.5:
            return "Moderate correlation"
        elif abs(correlation) < 0.7:
            return "Strong correlation"
        else:
            return "Very strong correlation"
    
    def _generate_recommendations(self, performance: Dict[str, Any], 
                                signal_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on performance analysis"""
        recommendations = []
        
        # Win rate recommendations
        if performance.get("win_rate", 0) < 0.4:
            recommendations.append("Consider increasing sentiment threshold to improve signal quality")
        
        # Profit factor recommendations
        if performance.get("profit_factor", 0) < 1.0:
            recommendations.append("Average losses exceed average wins - review risk management")
        
        # Drawdown recommendations
        if performance.get("max_drawdown", 0) < -20:
            recommendations.append("High drawdown detected - consider reducing position sizes")
        
        # Signal type recommendations
        for signal, data in signal_analysis.items():
            if data.get("win_rate", 0) < 0.3:
                recommendations.append(f"Consider reducing {signal} signal frequency - low win rate")
        
        # Volatility recommendations
        if performance.get("volatility", 0) > 50:
            recommendations.append("High volatility detected - consider position sizing adjustments")
        
        return recommendations
    
    def optimize_parameters(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize trading parameters based on performance
        """
        try:
            current_thresholds = {
                "sentiment_threshold": Config.SENTIMENT_THRESHOLD,
                "price_gap_threshold": Config.PRICE_GAP_THRESHOLD
            }
            
            # Simple optimization based on performance
            win_rate = performance_data.get("performance", {}).get("win_rate", 0.5)
            profit_factor = performance_data.get("performance", {}).get("profit_factor", 1.0)
            
            optimized_thresholds = current_thresholds.copy()
            
            # Adjust sentiment threshold based on win rate
            if win_rate < 0.4:
                optimized_thresholds["sentiment_threshold"] = min(0.9, 
                    current_thresholds["sentiment_threshold"] + 0.1)
            elif win_rate > 0.7:
                optimized_thresholds["sentiment_threshold"] = max(0.5,
                    current_thresholds["sentiment_threshold"] - 0.05)
            
            # Adjust price gap threshold based on profit factor
            if profit_factor < 1.0:
                optimized_thresholds["price_gap_threshold"] = min(0.15,
                    current_thresholds["price_gap_threshold"] + 0.02)
            elif profit_factor > 2.0:
                optimized_thresholds["price_gap_threshold"] = max(0.03,
                    current_thresholds["price_gap_threshold"] - 0.01)
            
            return {
                "current_thresholds": current_thresholds,
                "optimized_thresholds": optimized_thresholds,
                "changes": {
                    "sentiment_threshold": optimized_thresholds["sentiment_threshold"] - 
                                         current_thresholds["sentiment_threshold"],
                    "price_gap_threshold": optimized_thresholds["price_gap_threshold"] - 
                                        current_thresholds["price_gap_threshold"]
                },
                "confidence": self._calculate_optimization_confidence(performance_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing parameters: {e}")
            return {"error": str(e)}
    
    def _calculate_optimization_confidence(self, performance_data: Dict[str, Any]) -> float:
        """Calculate confidence in optimization recommendations"""
        sample_size = performance_data.get("total_trades", 0)
        
        if sample_size < 10:
            return 0.3  # Low confidence with small sample
        elif sample_size < 50:
            return 0.6  # Medium confidence
        else:
            return 0.8  # High confidence with large sample
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily performance report"""
        try:
            # Get today's trades
            today = datetime.now().date().isoformat()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM trades 
                WHERE DATE(entry_timestamp) = ? OR DATE(exit_timestamp) = ?
            ''', (today, today))
            
            today_trades = cursor.fetchall()
            conn.close()
            
            # Calculate daily metrics
            daily_pnl = sum(trade[10] for trade in today_trades if trade[10] is not None)
            daily_trades = len(today_trades)
            
            # Get portfolio summary
            portfolio_summary = self._get_portfolio_summary()
            
            return {
                "date": today,
                "daily_trades": daily_trades,
                "daily_pnl": daily_pnl,
                "portfolio_summary": portfolio_summary,
                "top_performers": self._get_top_performers(today_trades),
                "alerts": self._generate_alerts(portfolio_summary)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating daily report: {e}")
            return {"error": str(e)}
    
    def _get_portfolio_summary(self) -> Dict[str, Any]:
        """Get current portfolio summary"""
        # This would integrate with PortfolioTracker
        return {"total_value": 10000, "active_trades": 5, "total_pnl": 500}
    
    def _get_top_performers(self, trades: List[Tuple]) -> List[Dict[str, Any]]:
        """Get top performing trades"""
        performers = []
        for trade in trades:
            if trade[10] and trade[10] > 0:  # pnl > 0
                performers.append({
                    "entity": trade[1],
                    "pnl": trade[10],
                    "pnl_percentage": trade[11]
                })
        
        return sorted(performers, key=lambda x: x["pnl"], reverse=True)[:5]
    
    def _generate_alerts(self, portfolio_summary: Dict[str, Any]) -> List[str]:
        """Generate alerts based on portfolio status"""
        alerts = []
        
        if portfolio_summary.get("total_pnl", 0) < -1000:
            alerts.append("Portfolio showing significant losses")
        
        if portfolio_summary.get("active_trades", 0) > 20:
            alerts.append("High number of active trades - consider position management")
        
        return alerts
