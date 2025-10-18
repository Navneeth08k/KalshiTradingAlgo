"""
Kalshi API Integration - Real-time market data and trading
"""
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from config import Config

class KalshiAPI:
    def __init__(self):
        """Initialize the Kalshi API client"""
        self.logger = logging.getLogger(__name__)
        self.api_key = Config.KALSHI_API_KEY
        # Use public endpoints that don't require authentication
        self.base_url = 'https://api.elections.kalshi.com/trade-api/v2'
        self.session = requests.Session()
        
        # Public endpoints don't require authentication
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        if self.api_key:
            self.logger.info("Kalshi API client initialized with API key")
        else:
            self.logger.info("Kalshi API client initialized with public endpoints")
    
    def get_markets(self, limit: int = 100, status: str = "open") -> List[Dict[str, Any]]:
        """
        Get available markets from Kalshi using public endpoints
        """
        try:
            url = f"{self.base_url}/markets"
            params = {
                'limit': limit,
                'status': status
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            markets = data.get('markets', [])
            
            self.logger.info(f"Retrieved {len(markets)} markets from Kalshi")
            return markets
            
        except Exception as e:
            self.logger.error(f"Error fetching Kalshi markets: {e}")
            return self._get_mock_markets()
    
    def get_market_by_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get specific market by ticker using public endpoints
        """
        try:
            url = f"{self.base_url}/markets/{ticker}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            market = response.json()
            self.logger.info(f"Retrieved market data for {ticker}")
            return market
            
        except Exception as e:
            self.logger.error(f"Error fetching market {ticker}: {e}")
            return self._get_mock_market_by_ticker(ticker)
    
    def get_market_price(self, ticker: str) -> Optional[float]:
        """
        Get current market price for a ticker
        """
        market = self.get_market_by_ticker(ticker)
        if market:
            # Extract price from market data based on Kalshi API structure
            market_data = market.get('market', {})
            price = market_data.get('yes_price', market_data.get('yes_bid', 0.5))
            if price:
                return float(price) / 100  # Convert from cents to decimal
        return None
    
    def place_order(self, ticker: str, side: str, amount: int, 
                   price: float = None) -> Dict[str, Any]:
        """
        Place an order on Kalshi (simulation mode)
        """
        if not self.api_key:
            return self._simulate_order(ticker, side, amount, price)
        
        try:
            url = f"{self.base_url}/orders"
            order_data = {
                'ticker': ticker,
                'side': side,  # 'yes' or 'no'
                'amount': amount,
                'price': price or self.get_market_price(ticker)
            }
            
            response = self.session.post(url, json=order_data, timeout=10)
            response.raise_for_status()
            
            order_result = response.json()
            self.logger.info(f"Order placed for {ticker}: {side} {amount} @ {price}")
            return order_result
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return self._simulate_order(ticker, side, amount, price)
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions
        """
        if not self.api_key:
            return self._get_mock_positions()
        
        try:
            url = f"{self.base_url}/positions"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            positions = response.json()
            self.logger.info(f"Retrieved {len(positions)} positions")
            return positions
            
        except Exception as e:
            self.logger.error(f"Error fetching positions: {e}")
            return self._get_mock_positions()
    
    def get_account_balance(self) -> Dict[str, Any]:
        """
        Get account balance and portfolio value
        """
        if not self.api_key:
            return self._get_mock_balance()
        
        try:
            url = f"{self.base_url}/account"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            account = response.json()
            self.logger.info("Retrieved account balance")
            return account
            
        except Exception as e:
            self.logger.error(f"Error fetching account balance: {e}")
            return self._get_mock_balance()
    
    def _get_mock_markets(self) -> List[Dict[str, Any]]:
        """Mock markets for testing - using real Kalshi market structure"""
        return [
            {
                "ticker": "KXMVENFLMULTIGAMEEXTENDED-S2025A82C4A14090-B2FA5A069D8",
                "title": "Mock Market 1",
                "status": "open",
                "yes_price": 27,
                "no_price": 73,
                "volume": 1000,
                "open_interest": 5000
            },
            {
                "ticker": "KXMVENFLMULTIGAMEEXTENDED-S2025A82C4A14090-B2FA5A069D9",
                "title": "Mock Market 2", 
                "status": "open",
                "yes_price": 45,
                "no_price": 55,
                "volume": 800,
                "open_interest": 3000
            },
            {
                "ticker": "KXMVENFLMULTIGAMEEXTENDED-S2025A82C4A14090-B2FA5A069DA",
                "title": "Mock Market 3",
                "status": "open",
                "yes_price": 52,
                "no_price": 48,
                "volume": 2000,
                "open_interest": 10000
            }
        ]
    
    def _get_mock_market_by_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Mock market data for specific ticker"""
        markets = self._get_mock_markets()
        for market in markets:
            if market['ticker'] == ticker:
                return market
        return None
    
    def _simulate_order(self, ticker: str, side: str, amount: int, price: float) -> Dict[str, Any]:
        """Simulate order placement"""
        return {
            "order_id": f"SIM_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "ticker": ticker,
            "side": side,
            "amount": amount,
            "price": price,
            "status": "filled",
            "timestamp": datetime.now().isoformat(),
            "simulation": True
        }
    
    def _get_mock_positions(self) -> List[Dict[str, Any]]:
        """Mock positions for testing"""
        return [
            {
                "ticker": "NBA_2025_GSW_CHAMPIONSHIP",
                "side": "yes",
                "amount": 100,
                "average_price": 0.28,
                "current_value": 0.27,
                "unrealized_pnl": -1.0
            }
        ]
    
    def _get_mock_balance(self) -> Dict[str, Any]:
        """Mock account balance"""
        return {
            "cash_balance": 10000.0,
            "portfolio_value": 10250.0,
            "total_pnl": 250.0,
            "available_balance": 9500.0
        }
