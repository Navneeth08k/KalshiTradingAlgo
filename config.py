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
    PINNACLE_API_KEY = os.getenv('PINNACLE_API_KEY')  # Now restricted
    THE_ODDS_API_KEY = os.getenv('THE_ODDS_API_KEY')  # Free tier available
    BETFAIR_API_KEY = os.getenv('BETFAIR_API_KEY')    # Alternative source
    
    # Database
    DATABASE_PATH = 'trading_data.db'
    
    # Trading Parameters
    SENTIMENT_THRESHOLD = 0.7  # Minimum sentiment score for signals
    PRICE_GAP_THRESHOLD = 0.05  # Minimum price gap for signals
    MAX_POSITION_SIZE = 1000  # Maximum position size in dollars
    STOP_LOSS_PERCENTAGE = 0.1  # 10% stop loss
    
    # Trading Mode
    FAKE_MONEY_MODE = True  # Set to True for paper trading, False for real money
    INITIAL_BALANCE = 10000  # Starting balance for fake money mode
    
    # API Endpoints
    KALSHI_BASE_URL = 'https://api.elections.kalshi.com/trade-api/v2'  # Public endpoints
    PINNACLE_BASE_URL = 'https://api.pinnaclesports.com'  # Now restricted
    THE_ODDS_BASE_URL = 'https://api.the-odds-api.com/v4'
    BETFAIR_BASE_URL = 'https://api.betfair.com/exchange'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'trading_algorithm.log'
    
    # Automation
    CHECK_INTERVAL_HOURS = 6  # How often to check for new opportunities
    MAX_DAILY_TRADES = 10  # Maximum trades per day
    
    @classmethod
    def validate_config(cls):
        """Validate that all required API keys are set"""
        # Essential keys
        required_keys = ['GEMINI_API_KEY']
        
        # Optional but recommended keys
        recommended_keys = ['THE_ODDS_API_KEY', 'KALSHI_API_KEY']
        
        missing_required = []
        missing_recommended = []
        
        for key in required_keys:
            if not getattr(cls, key):
                missing_required.append(key)
        
        for key in recommended_keys:
            if not getattr(cls, key):
                missing_recommended.append(key)
        
        if missing_required:
            raise ValueError(f"Missing required API keys: {', '.join(missing_required)}")
        
        if missing_recommended:
            print(f"Warning: Missing recommended API keys: {', '.join(missing_recommended)}")
            print("System will use mock data for missing sources.")
        
        return True
