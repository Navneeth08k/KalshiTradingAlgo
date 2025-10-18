"""
Market Mapper - Maps entities to Kalshi markets using Gemini API
"""
import google.generativeai as genai
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from config import Config

class MarketMapper:
    def __init__(self):
        """Initialize the market mapper"""
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        self.logger = logging.getLogger(__name__)
        self.kalshi_markets = {}
        self._load_kalshi_markets()
    
    def _load_kalshi_markets(self):
        """Load available Kalshi markets from API"""
        try:
            # This would be replaced with actual Kalshi API call
            # For now, we'll use a mock structure
            self.kalshi_markets = {
                "NBA": [
                    {"ticker": "NBA_2025_GSW_CHAMPIONSHIP", "name": "Golden State Warriors to win 2025 NBA Championship"},
                    {"ticker": "NBA_2025_LAL_CHAMPIONSHIP", "name": "Los Angeles Lakers to win 2025 NBA Championship"},
                    {"ticker": "NBA_2025_BOS_CHAMPIONSHIP", "name": "Boston Celtics to win 2025 NBA Championship"},
                ],
                "NFL": [
                    {"ticker": "NFL_2025_DAL_PLAYOFFS", "name": "Dallas Cowboys to make 2025 NFL Playoffs"},
                    {"ticker": "NFL_2025_KC_CHAMPIONSHIP", "name": "Kansas City Chiefs to win 2025 Super Bowl"},
                ],
                "POLITICS": [
                    {"ticker": "PRES_2024_TRUMP", "name": "Donald Trump to win 2024 Presidential Election"},
                    {"ticker": "PRES_2024_BIDEN", "name": "Joe Biden to win 2024 Presidential Election"},
                ],
                "FINANCE": [
                    {"ticker": "BTC_2024_100K", "name": "Bitcoin to reach $100,000 by end of 2024"},
                    {"ticker": "SPY_2024_500", "name": "S&P 500 to reach 5000 by end of 2024"},
                ]
            }
            self.logger.info(f"Loaded {sum(len(markets) for markets in self.kalshi_markets.values())} Kalshi markets")
        except Exception as e:
            self.logger.error(f"Error loading Kalshi markets: {e}")
            self.kalshi_markets = {}
    
    def map_entity_to_markets(self, entity: str, category: str) -> List[Dict[str, Any]]:
        """
        Map an entity to relevant Kalshi markets using Gemini
        """
        prompt = f"""
        You are a market mapping expert. Given the entity "{entity}" in category "{category}",
        find the most relevant Kalshi prediction markets.
        
        Available market categories and examples:
        - NBA: Championship winners, playoff teams, player awards
        - NFL: Super Bowl winners, playoff teams, division winners
        - Politics: Election outcomes, policy changes, approval ratings
        - Finance: Stock prices, crypto prices, economic indicators
        - Entertainment: Awards, box office, ratings
        
        For "{entity}", identify:
        1. The most relevant Kalshi market ticker
        2. Market name/description
        3. Relevance score (0-1)
        4. Market type (championship, playoff, price target, etc.)
        
        Return as JSON array:
        [
            {{
                "entity": "{entity}",
                "category": "{category}",
                "kalshi_ticker": "NBA_2025_GSW_CHAMPIONSHIP",
                "market_name": "Golden State Warriors to win 2025 NBA Championship",
                "relevance_score": 0.95,
                "market_type": "championship"
            }}
        ]
        
        Only return markets that are highly relevant (relevance_score > 0.7).
        If no relevant markets exist, return empty array.
        """
        
        try:
            response = self.model.generate_content(prompt)
            mapping_text = response.text.strip()
            
            # Clean up JSON response
            if mapping_text.startswith('```json'):
                mapping_text = mapping_text[7:]
            if mapping_text.endswith('```'):
                mapping_text = mapping_text[:-3]
            
            mappings = json.loads(mapping_text)
            
            # Validate and filter mappings
            valid_mappings = []
            for mapping in mappings:
                if mapping.get('relevance_score', 0) > 0.7:
                    valid_mappings.append(mapping)
            
            self.logger.info(f"Mapped {entity} to {len(valid_mappings)} relevant markets")
            return valid_mappings
            
        except Exception as e:
            self.logger.error(f"Error mapping entity to markets: {e}")
            return []
    
    def get_market_details(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific Kalshi market
        """
        try:
            # This would be replaced with actual Kalshi API call
            # For now, return mock data
            for category, markets in self.kalshi_markets.items():
                for market in markets:
                    if market['ticker'] == ticker:
                        return {
                            'ticker': ticker,
                            'name': market['name'],
                            'category': category,
                            'status': 'active',
                            'volume': 1000,  # Mock volume
                            'open_interest': 5000  # Mock open interest
                        }
            return None
        except Exception as e:
            self.logger.error(f"Error getting market details for {ticker}: {e}")
            return None
    
    def find_similar_markets(self, entity: str, category: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar markets for an entity using semantic matching
        """
        prompt = f"""
        Find Kalshi markets similar to "{entity}" in {category}.
        
        Look for markets that might be related through:
        - Same team/player in different contexts
        - Related events (playoffs -> championship)
        - Similar timeframes
        - Related categories
        
        Return top {limit} most similar markets as JSON array:
        [
            {{
                "ticker": "NBA_2025_GSW_PLAYOFFS",
                "name": "Golden State Warriors to make 2025 NBA Playoffs",
                "similarity_score": 0.85,
                "relationship": "playoff qualification"
            }}
        ]
        """
        
        try:
            response = self.model.generate_content(prompt)
            similar_text = response.text.strip()
            
            # Clean up JSON response
            if similar_text.startswith('```json'):
                similar_text = similar_text[7:]
            if similar_text.endswith('```'):
                similar_text = similar_text[:-3]
            
            similar_markets = json.loads(similar_text)
            return similar_markets[:limit]
            
        except Exception as e:
            self.logger.error(f"Error finding similar markets: {e}")
            return []
    
    def validate_market_mapping(self, entity: str, ticker: str) -> Dict[str, Any]:
        """
        Validate that a market mapping is correct and relevant
        """
        prompt = f"""
        Validate that the Kalshi market "{ticker}" is correctly mapped to entity "{entity}".
        
        Check:
        1. Is the market relevant to the entity?
        2. Is the mapping semantically correct?
        3. Are there any obvious mismatches?
        
        Return validation result as JSON:
        {{
            "is_valid": true,
            "confidence": 0.95,
            "issues": [],
            "suggestions": []
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            validation_text = response.text.strip()
            
            # Clean up JSON response
            if validation_text.startswith('```json'):
                validation_text = validation_text[7:]
            if validation_text.endswith('```'):
                validation_text = validation_text[:-3]
            
            validation = json.loads(validation_text)
            return validation
            
        except Exception as e:
            self.logger.error(f"Error validating market mapping: {e}")
            return {
                "is_valid": False,
                "confidence": 0.0,
                "issues": ["Validation failed"],
                "suggestions": []
            }
