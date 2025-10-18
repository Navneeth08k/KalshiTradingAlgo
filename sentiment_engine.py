"""
Sentiment Engine using Gemini API for real-time sentiment analysis
"""
import google.generativeai as genai
import json
import logging
from typing import List, Dict, Any
from config import Config

class SentimentEngine:
    def __init__(self):
        """Initialize the sentiment engine with Gemini API"""
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        self.logger = logging.getLogger(__name__)
    
    def get_trending_entities(self) -> List[Dict[str, Any]]:
        """
        Find trending entities with sentiment scores using Gemini
        Returns list of entities with sentiment scores between -1 and +1
        """
        prompt = """
        You are a financial sentiment analyst. Analyze the current trending topics in:
        1. Sports (NBA, NFL, MLB, NHL, etc.)
        2. Politics (elections, policy changes, etc.)
        3. Finance (stocks, crypto, economic indicators)
        4. Entertainment (movies, TV shows, celebrities)
        5. Technology (AI, tech companies, innovations)
        
        For each trending entity, provide:
        - Entity name
        - Category
        - Sentiment score (-1 to +1, where +1 is very positive, -1 is very negative)
        - Brief reason for the sentiment
        
        Focus on entities that are experiencing significant sentiment shifts today.
        Return ONLY a JSON array with this exact format:
        [
            {
                "entity": "Golden State Warriors",
                "category": "NBA",
                "sentiment": 0.87,
                "reason": "Won 5 games in a row, Curry MVP performance"
            }
        ]
        
        Provide 10-15 entities with the strongest sentiment signals.
        """
        
        try:
            response = self.model.generate_content(prompt)
            entities_text = response.text.strip()
            
            # Clean up the response to extract JSON
            if entities_text.startswith('```json'):
                entities_text = entities_text[7:]
            if entities_text.endswith('```'):
                entities_text = entities_text[:-3]
            
            entities = json.loads(entities_text)
            
            # Validate sentiment scores
            for entity in entities:
                if not -1 <= entity['sentiment'] <= 1:
                    entity['sentiment'] = max(-1, min(1, entity['sentiment']))
            
            self.logger.info(f"Found {len(entities)} trending entities")
            return entities
            
        except Exception as e:
            self.logger.error(f"Error getting trending entities: {e}")
            return []
    
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
