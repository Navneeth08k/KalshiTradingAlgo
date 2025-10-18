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
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required but not set")
        
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.logger = logging.getLogger(__name__)
            self.kalshi_markets = {}
            self._load_kalshi_markets()
            self.logger.info("Market mapper initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize market mapper: {e}")
            raise
    
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
        Map entity "{entity}" in {category} to Kalshi market.
        
        Return JSON:
        [{{"entity": "{entity}", "category": "{category}", "kalshi_ticker": "NBA_2025_GSW_CHAMPIONSHIP", "market_name": "Golden State Warriors to win 2025 NBA Championship", "relevance_score": 0.95, "market_type": "championship"}}]
        
        Use clean JSON only. No markdown, no extra text.
        """
        
        try:
            # Add retry logic for API calls
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.3,  # Lower temperature for more consistent mapping
                            max_output_tokens=1024,
                        )
                    )
                    
                    # Handle complex responses properly
                    mapping_text = ""
                    if hasattr(response, 'text') and response.text:
                        mapping_text = response.text.strip()
                    elif hasattr(response, 'parts') and response.parts:
                        mapping_text = response.parts[0].text.strip()
                    elif hasattr(response, 'candidates') and response.candidates:
                        if hasattr(response.candidates[0], 'content') and hasattr(response.candidates[0].content, 'parts'):
                            mapping_text = response.candidates[0].content.parts[0].text.strip()
                    else:
                        raise ValueError("Empty or invalid response from Gemini API")
                    
                    # Clean up JSON response
                    if mapping_text.startswith('```json'):
                        mapping_text = mapping_text[7:]
                    if mapping_text.endswith('```'):
                        mapping_text = mapping_text[:-3]
                    
                    # Try to parse JSON with better error handling
                    try:
                        mappings = json.loads(mapping_text)
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"JSON decode error on attempt {attempt + 1}: {e}")
                        # Try to extract JSON from malformed response
                        import re
                        # Look for JSON array pattern
                        json_match = re.search(r'\[.*\]', mapping_text, re.DOTALL)
                        if json_match:
                            try:
                                mappings = json.loads(json_match.group())
                            except json.JSONDecodeError:
                                # Try to fix common JSON issues
                                fixed_json = json_match.group().replace('\n', '').replace('\r', '')
                                try:
                                    mappings = json.loads(fixed_json)
                                except json.JSONDecodeError:
                                    raise ValueError(f"Could not parse JSON from response: {mapping_text[:200]}...")
                        else:
                            raise ValueError(f"No JSON found in response: {mapping_text[:200]}...")
                    
                    # Validate and filter mappings
                    valid_mappings = []
                    for mapping in mappings:
                        if (isinstance(mapping, dict) and 
                            mapping.get('relevance_score', 0) > 0.7 and
                            'kalshi_ticker' in mapping):
                            valid_mappings.append(mapping)
                    
                    if valid_mappings:
                        self.logger.info(f"Mapped {entity} to {len(valid_mappings)} relevant markets")
                        return valid_mappings
                    else:
                        self.logger.warning(f"No valid mappings found for {entity}")
                        return self._get_fallback_mappings(entity, category)
                    
                except json.JSONDecodeError as e:
                    self.logger.warning(f"JSON decode error on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return self._get_fallback_mappings(entity, category)
                
                except Exception as e:
                    self.logger.warning(f"API error on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return self._get_fallback_mappings(entity, category)
            
        except Exception as e:
            self.logger.error(f"Critical error mapping entity to markets: {e}")
            return self._get_fallback_mappings(entity, category)
    
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
    
    def _get_fallback_mappings(self, entity: str, category: str) -> List[Dict[str, Any]]:
        """
        Provide fallback mappings when API calls fail
        """
        self.logger.info(f"Using fallback mappings for {entity} in {category}")
        
        # Simple fallback mappings based on category
        fallback_mappings = {
            "NBA": [
                {
                    "entity": entity,
                    "category": category,
                    "kalshi_ticker": "NBA_2025_GSW_CHAMPIONSHIP",
                    "market_name": f"{entity} to win 2025 NBA Championship",
                    "relevance_score": 0.8,
                    "market_type": "championship"
                }
            ],
            "NFL": [
                {
                    "entity": entity,
                    "category": category,
                    "kalshi_ticker": "NFL_2025_DAL_PLAYOFFS",
                    "market_name": f"{entity} to make 2025 NFL Playoffs",
                    "relevance_score": 0.8,
                    "market_type": "playoffs"
                }
            ],
            "FINANCE": [
                {
                    "entity": entity,
                    "category": category,
                    "kalshi_ticker": "BTC_2024_100K",
                    "market_name": f"{entity} to reach $100,000 by end of 2024",
                    "relevance_score": 0.7,
                    "market_type": "price_target"
                }
            ]
        }
        
        return fallback_mappings.get(category, [])
