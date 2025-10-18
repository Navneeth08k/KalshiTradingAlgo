"""
Portfolio Tracker - Tracks trades and portfolio performance
"""
import sqlite3
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from config import Config

class PortfolioTracker:
    def __init__(self):
        """Initialize the portfolio tracker"""
        self.logger = logging.getLogger(__name__)
        self.db_path = Config.DATABASE_PATH
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for tracking trades"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity TEXT NOT NULL,
                    ticker TEXT NOT NULL,
                    signal TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    position_size REAL NOT NULL,
                    entry_timestamp TEXT NOT NULL,
                    exit_price REAL,
                    exit_timestamp TEXT,
                    pnl REAL,
                    pnl_percentage REAL,
                    status TEXT NOT NULL,
                    confidence REAL,
                    signal_strength REAL,
                    reasoning TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create portfolio metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    total_value REAL NOT NULL,
                    cash_balance REAL NOT NULL,
                    total_pnl REAL NOT NULL,
                    total_pnl_percentage REAL NOT NULL,
                    active_trades INTEGER NOT NULL,
                    win_rate REAL,
                    avg_win REAL,
                    avg_loss REAL,
                    max_drawdown REAL,
                    sharpe_ratio REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create market data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    price REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    volume INTEGER,
                    open_interest INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
    
    def execute_trade(self, signal_data: Dict[str, Any], 
                     kalshi_price: float) -> Dict[str, Any]:
        """
        Execute a trade based on signal data
        """
        try:
            trade = {
                "entity": signal_data.get('entity', ''),
                "ticker": signal_data.get('ticker', ''),
                "signal": signal_data.get('signal', ''),
                "entry_price": kalshi_price,
                "position_size": signal_data.get('position_size', 0.0),
                "entry_timestamp": datetime.now().isoformat(),
                "exit_price": None,
                "exit_timestamp": None,
                "pnl": 0.0,
                "pnl_percentage": 0.0,
                "status": "ACTIVE",
                "confidence": signal_data.get('confidence', 0.0),
                "signal_strength": signal_data.get('signal_strength', 0.0),
                "reasoning": signal_data.get('reasoning', '')
            }
            
            # Save trade to database
            trade_id = self._save_trade(trade)
            trade['id'] = trade_id
            
            self.logger.info(f"Executed {signal_data.get('signal')} trade for {signal_data.get('entity')}")
            return trade
            
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return {"error": str(e)}
    
    def _save_trade(self, trade: Dict[str, Any]) -> int:
        """Save trade to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trades (
                    entity, ticker, signal, entry_price, position_size,
                    entry_timestamp, status, confidence, signal_strength, reasoning
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade['entity'], trade['ticker'], trade['signal'],
                trade['entry_price'], trade['position_size'],
                trade['entry_timestamp'], trade['status'],
                trade['confidence'], trade['signal_strength'], trade['reasoning']
            ))
            
            trade_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return trade_id
            
        except Exception as e:
            self.logger.error(f"Error saving trade: {e}")
            return 0
    
    def update_trade(self, trade_id: int, exit_price: float, 
                    exit_reason: str = "MANUAL") -> Dict[str, Any]:
        """
        Update trade with exit price and calculate P&L
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get trade data
            cursor.execute('SELECT * FROM trades WHERE id = ?', (trade_id,))
            trade_data = cursor.fetchone()
            
            if not trade_data:
                return {"error": "Trade not found"}
            
            # Calculate P&L
            entry_price = trade_data[4]  # entry_price column
            position_size = trade_data[5]  # position_size column
            signal = trade_data[3]  # signal column
            
            if signal == "LONG":
                pnl = (exit_price - entry_price) * position_size
            elif signal == "SHORT":
                pnl = (entry_price - exit_price) * position_size
            else:
                pnl = 0.0
            
            pnl_percentage = (pnl / (entry_price * position_size)) * 100
            
            # Update trade
            cursor.execute('''
                UPDATE trades SET 
                    exit_price = ?, exit_timestamp = ?, pnl = ?, 
                    pnl_percentage = ?, status = ?
                WHERE id = ?
            ''', (exit_price, datetime.now().isoformat(), pnl, 
                  pnl_percentage, "CLOSED", trade_id))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Updated trade {trade_id} with P&L: {pnl:.2f}")
            return {
                "trade_id": trade_id,
                "pnl": pnl,
                "pnl_percentage": pnl_percentage,
                "status": "CLOSED"
            }
            
        except Exception as e:
            self.logger.error(f"Error updating trade: {e}")
            return {"error": str(e)}
    
    def get_active_trades(self) -> List[Dict[str, Any]]:
        """Get all active trades"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM trades WHERE status = 'ACTIVE'
                ORDER BY entry_timestamp DESC
            ''')
            
            trades = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            active_trades = []
            for trade in trades:
                active_trades.append({
                    "id": trade[0],
                    "entity": trade[1],
                    "ticker": trade[2],
                    "signal": trade[3],
                    "entry_price": trade[4],
                    "position_size": trade[5],
                    "entry_timestamp": trade[6],
                    "confidence": trade[8],
                    "signal_strength": trade[9],
                    "reasoning": trade[10]
                })
            
            return active_trades
            
        except Exception as e:
            self.logger.error(f"Error getting active trades: {e}")
            return []
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary with key metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total trades
            cursor.execute('SELECT COUNT(*) FROM trades')
            total_trades = cursor.fetchone()[0]
            
            # Get active trades
            cursor.execute('SELECT COUNT(*) FROM trades WHERE status = "ACTIVE"')
            active_trades = cursor.fetchone()[0]
            
            # Get closed trades
            cursor.execute('SELECT COUNT(*) FROM trades WHERE status = "CLOSED"')
            closed_trades = cursor.fetchone()[0]
            
            # Get total P&L
            cursor.execute('SELECT SUM(pnl) FROM trades WHERE status = "CLOSED"')
            total_pnl = cursor.fetchone()[0] or 0.0
            
            # Get win rate
            cursor.execute('SELECT COUNT(*) FROM trades WHERE status = "CLOSED" AND pnl > 0')
            winning_trades = cursor.fetchone()[0]
            win_rate = (winning_trades / closed_trades) if closed_trades > 0 else 0.0
            
            # Get average win/loss
            cursor.execute('SELECT AVG(pnl) FROM trades WHERE status = "CLOSED" AND pnl > 0')
            avg_win = cursor.fetchone()[0] or 0.0
            
            cursor.execute('SELECT AVG(pnl) FROM trades WHERE status = "CLOSED" AND pnl < 0')
            avg_loss = cursor.fetchone()[0] or 0.0
            
            # Get recent performance (last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            cursor.execute('''
                SELECT SUM(pnl) FROM trades 
                WHERE status = "CLOSED" AND exit_timestamp > ?
            ''', (thirty_days_ago,))
            recent_pnl = cursor.fetchone()[0] or 0.0
            
            conn.close()
            
            return {
                "total_trades": total_trades,
                "active_trades": active_trades,
                "closed_trades": closed_trades,
                "total_pnl": total_pnl,
                "win_rate": win_rate,
                "avg_win": avg_win,
                "avg_loss": avg_loss,
                "recent_pnl_30d": recent_pnl,
                "profit_factor": abs(avg_win / avg_loss) if avg_loss != 0 else 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio summary: {e}")
            return {}
    
    def update_market_data(self, ticker: str, price: float, 
                          volume: int = 0, open_interest: int = 0):
        """Update market data for a ticker"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO market_data (ticker, price, timestamp, volume, open_interest)
                VALUES (?, ?, ?, ?, ?)
            ''', (ticker, price, datetime.now().isoformat(), volume, open_interest))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error updating market data: {e}")
    
    def get_market_data(self, ticker: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical market data for a ticker"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            cursor.execute('''
                SELECT * FROM market_data 
                WHERE ticker = ? AND timestamp > ?
                ORDER BY timestamp ASC
            ''', (ticker, start_date))
            
            data = cursor.fetchall()
            conn.close()
            
            market_data = []
            for row in data:
                market_data.append({
                    "ticker": row[1],
                    "price": row[2],
                    "timestamp": row[3],
                    "volume": row[4],
                    "open_interest": row[5]
                })
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error getting market data: {e}")
            return []
    
    def simulate_trade(self, signal_data: Dict[str, Any], 
                     current_price: float, 
                     future_price: float) -> Dict[str, Any]:
        """
        Simulate a trade without executing it
        """
        try:
            entry_price = current_price
            position_size = signal_data.get('position_size', 0.0)
            signal = signal_data.get('signal', '')
            
            # Calculate simulated P&L
            if signal == "LONG":
                pnl = (future_price - entry_price) * position_size
            elif signal == "SHORT":
                pnl = (entry_price - future_price) * position_size
            else:
                pnl = 0.0
            
            pnl_percentage = (pnl / (entry_price * position_size)) * 100 if position_size > 0 else 0.0
            
            return {
                "entity": signal_data.get('entity', ''),
                "signal": signal,
                "entry_price": entry_price,
                "exit_price": future_price,
                "position_size": position_size,
                "pnl": pnl,
                "pnl_percentage": pnl_percentage,
                "simulation": True
            }
            
        except Exception as e:
            self.logger.error(f"Error simulating trade: {e}")
            return {"error": str(e)}
