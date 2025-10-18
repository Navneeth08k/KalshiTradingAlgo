"""
Sentiment Engine using Gemini API for real-time sentiment analysis
"""
import google.generativeai as genai
import json
import logging
import time
from typing import List, Dict, Any
from config import Config

class SentimentEngine:
    def __init__(self):
        """Initialize the sentiment engine with Gemini API"""
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required but not set")
        
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.logger = logging.getLogger(__name__)
            self.logger.info("Gemini API initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini API: {e}")
            raise
    
    def get_trending_entities(self) -> List[Dict[str, Any]]:
        """
        Find trending entities with sentiment scores using Gemini
        Returns list of entities with sentiment scores between -1 and +1
        """
        prompt = """
        Find 5 trending entities with sentiment scores.
        
        Return JSON array:
        [{"entity": "name", "category": "NBA", "sentiment": 0.75, "reason": "brief"}]
        
        Use clean JSON only. No markdown, no extra text.
        """
        
        try:
            # Add retry logic for API calls
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Generate content with Gemini
                    response = self.model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.7,
                            max_output_tokens=2048,
                        )
                    )
                    
                    # Handle complex responses properly
                    entities_text = ""
                    if hasattr(response, 'text') and response.text:
                        entities_text = response.text.strip()
                    elif hasattr(response, 'parts') and response.parts:
                        entities_text = response.parts[0].text.strip()
                    elif hasattr(response, 'candidates') and response.candidates:
                        if hasattr(response.candidates[0], 'content') and hasattr(response.candidates[0].content, 'parts'):
                            entities_text = response.candidates[0].content.parts[0].text.strip()
                    else:
                        raise ValueError("Empty or invalid response from Gemini API")
                    
                    # Clean up the response to extract JSON
                    if entities_text.startswith('```json'):
                        entities_text = entities_text[7:]
                    if entities_text.endswith('```'):
                        entities_text = entities_text[:-3]
                    
                    # Try to parse JSON with better error handling
                    try:
                        entities = json.loads(entities_text)
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"JSON decode error on attempt {attempt + 1}: {e}")
                        # Try to extract JSON from malformed response
                        import re
                        # Look for JSON array pattern
                        json_match = re.search(r'\[.*\]', entities_text, re.DOTALL)
                        if json_match:
                            try:
                                entities = json.loads(json_match.group())
                            except json.JSONDecodeError:
                                # Try to fix common JSON issues
                                fixed_json = json_match.group().replace('\n', '').replace('\r', '')
                                try:
                                    entities = json.loads(fixed_json)
                                except json.JSONDecodeError:
                                    raise ValueError(f"Could not parse JSON from response: {entities_text[:200]}...")
                        else:
                            raise ValueError(f"No JSON found in response: {entities_text[:200]}...")
                    
                    # Validate and clean up entities
                    valid_entities = []
                    for entity in entities:
                        if isinstance(entity, dict) and 'entity' in entity and 'sentiment' in entity:
                            # Ensure sentiment is within bounds
                            sentiment = entity['sentiment']
                            if isinstance(sentiment, (int, float)):
                                entity['sentiment'] = max(-1, min(1, float(sentiment)))
                                valid_entities.append(entity)
                    
                    if valid_entities:
                        self.logger.info(f"Found {len(valid_entities)} trending entities")
                        return valid_entities
                    else:
                        self.logger.warning("No valid entities found in response")
                        return self._get_fallback_entities()
                    
                except json.JSONDecodeError as e:
                    self.logger.warning(f"JSON decode error on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        return self._get_fallback_entities()
                
                except Exception as e:
                    self.logger.warning(f"API error on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        return self._get_fallback_entities()
            
        except Exception as e:
            self.logger.error(f"Critical error getting trending entities: {e}")
            return self._get_fallback_entities()
    
    def analyze_entity_sentiment(self, entity: str, category: str) -> Dict[str, Any]:
        """
        Deep dive sentiment analysis for a specific entity
        """
        prompt = f"""
        Analyze the current sentiment for {entity} in {category}.
        
        Consider:
        - Recent news coverage
        - Social media buzz
        - Expert opinions
        - Market reactions
        - Historical context
        
        Provide:
        1. Sentiment score (-1 to +1)
        2. Confidence level (0 to 1)
        3. Key factors driving sentiment
        4. Recent events affecting sentiment
        5. Market implications
        
        Return as JSON:
        {{
            "entity": "{entity}",
            "category": "{category}",
            "sentiment": 0.75,
            "confidence": 0.85,
            "key_factors": ["Factor 1", "Factor 2"],
            "recent_events": ["Event 1", "Event 2"],
            "market_implications": "Brief analysis"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            analysis_text = response.text.strip()
            
            # Clean up JSON response
            if analysis_text.startswith('```json'):
                analysis_text = analysis_text[7:]
            if analysis_text.endswith('```'):
                analysis_text = analysis_text[:-3]
            
            analysis = json.loads(analysis_text)
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing entity sentiment: {e}")
            return {
                "entity": entity,
                "category": category,
                "sentiment": 0.0,
                "confidence": 0.0,
                "key_factors": [],
                "recent_events": [],
                "market_implications": "Analysis failed"
            }
    
    def get_sentiment_explanation(self, entity: str, sentiment: float) -> str:
        """
        Generate human-readable explanation for sentiment score
        """
        prompt = f"""
        Explain why {entity} has a sentiment score of {sentiment:.2f}.
        
        Provide a brief, clear explanation that a trader would understand.
        Focus on the key factors driving this sentiment.
        Keep it under 100 words.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            self.logger.error(f"Error generating sentiment explanation: {e}")
            return f"Sentiment analysis unavailable for {entity}"
    
    def _get_fallback_entities(self) -> List[Dict[str, Any]]:
        """
        Provide fallback entities when API calls fail
        """
        self.logger.info("Using fallback entities due to API issues")
        return [
            {
                "entity": "Golden State Warriors",
                "category": "NBA",
                "sentiment": 0.75,
                "reason": "Strong performance in recent games"
            },
            {
                "entity": "Dallas Cowboys",
                "category": "NFL", 
                "sentiment": 0.60,
                "reason": "Playoff contention and fan excitement"
            },
            {
                "entity": "Bitcoin",
                "category": "FINANCE",
                "sentiment": 0.40,
                "reason": "Market volatility and institutional adoption"
            },
            {
                "entity": "Tesla",
                "category": "FINANCE",
                "sentiment": 0.55,
                "reason": "EV market leadership and innovation"
            }
        ]
    
    def _validate_entity_data(self, entity: Dict[str, Any]) -> bool:
        """
        Validate entity data structure and values
        """
        required_fields = ['entity', 'category', 'sentiment']
        
        for field in required_fields:
            if field not in entity:
                return False
        
        # Validate sentiment is a number between -1 and 1
        try:
            sentiment = float(entity['sentiment'])
            if not -1 <= sentiment <= 1:
                return False
        except (ValueError, TypeError):
            return False
        
        # Validate entity and category are strings
        if not isinstance(entity['entity'], str) or not isinstance(entity['category'], str):
            return False
        
        return True
