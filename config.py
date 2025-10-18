"""
Configuration file for the Kalshi Trading Algorithm
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Keys (set these in your .env file)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    KALSHI_API_KEY = os.getenv('KALSHI_API_KEY')
    PINNACLE_API_KEY = os.getenv('PINNACLE_API_KEY')
    
    # Database
    DATABASE_PATH = 'trading_data.db'
    
    # Trading Parameters
    SENTIMENT_THRESHOLD = 0.7  # Minimum sentiment score for signals
    PRICE_GAP_THRESHOLD = 0.05  # Minimum price gap for signals
    MAX_POSITION_SIZE = 1000  # Maximum position size in dollars
    STOP_LOSS_PERCENTAGE = 0.1  # 10% stop loss
    
    # API Endpoints
    KALSHI_BASE_URL = 'https://trading-api.kalshi.com'
    PINNACLE_BASE_URL = 'https://api.pinnaclesports.com'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'trading_algorithm.log'
    
    # Automation
    CHECK_INTERVAL_HOURS = 6  # How often to check for new opportunities
    MAX_DAILY_TRADES = 10  # Maximum trades per day
    
    @classmethod
    def validate_config(cls):
        """Validate that all required API keys are set"""
        required_keys = ['GEMINI_API_KEY', 'KALSHI_API_KEY', 'PINNACLE_API_KEY']
        missing_keys = []
        
        for key in required_keys:
            if not getattr(cls, key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
        
        return True
