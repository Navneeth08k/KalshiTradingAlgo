"""
Benchmark Fetcher - Fetches odds from Pinnacle and other sources
"""
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from config import Config

class BenchmarkFetcher:
    def __init__(self):
        """Initialize the benchmark fetcher"""
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def get_pinnacle_odds(self, market_type: str, entity: str) -> Optional[Dict[str, Any]]:
        """
        Fetch odds from Pinnacle for a specific market
        """
        try:
            # This would be replaced with actual Pinnacle API call
            # For now, we'll use mock data based on market type
            mock_odds = self._get_mock_pinnacle_odds(market_type, entity)
            
            if mock_odds:
                self.logger.info(f"Fetched Pinnacle odds for {entity}: {mock_odds['implied_probability']:.3f}")
                return mock_odds
            else:
                self.logger.warning(f"No Pinnacle odds found for {entity}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error fetching Pinnacle odds: {e}")
            return None
    
    def _get_mock_pinnacle_odds(self, market_type: str, entity: str) -> Optional[Dict[str, Any]]:
        """
        Generate mock Pinnacle odds for testing
        """
        # Mock odds based on market type and entity
        mock_data = {
            "NBA": {
                "Golden State Warriors": {"odds": -150, "implied_prob": 0.60},
                "Los Angeles Lakers": {"odds": +200, "implied_prob": 0.33},
                "Boston Celtics": {"odds": +300, "implied_prob": 0.25},
            },
            "NFL": {
                "Dallas Cowboys": {"odds": +120, "implied_prob": 0.45},
                "Kansas City Chiefs": {"odds": -200, "implied_prob": 0.67},
            },
            "POLITICS": {
                "Donald Trump": {"odds": -110, "implied_prob": 0.52},
                "Joe Biden": {"odds": +110, "implied_prob": 0.48},
            },
            "FINANCE": {
                "Bitcoin": {"odds": +300, "implied_prob": 0.25},
                "S&P 500": {"odds": -150, "implied_prob": 0.60},
            }
        }
        
        if market_type in mock_data and entity in mock_data[market_type]:
            data = mock_data[market_type][entity]
            return {
                "source": "Pinnacle",
                "market_type": market_type,
                "entity": entity,
                "odds": data["odds"],
                "implied_probability": data["implied_prob"],
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.85
            }
        
        return None
    
    def get_multiple_source_odds(self, market_type: str, entity: str) -> List[Dict[str, Any]]:
        """
        Fetch odds from multiple sources for comparison
        """
        odds_sources = []
        
        # Pinnacle odds
        pinnacle_odds = self.get_pinnacle_odds(market_type, entity)
        if pinnacle_odds:
            odds_sources.append(pinnacle_odds)
        
        # Mock other sources
        other_sources = self._get_mock_other_sources(market_type, entity)
        odds_sources.extend(other_sources)
        
        return odds_sources
    
    def _get_mock_other_sources(self, market_type: str, entity: str) -> List[Dict[str, Any]]:
        """
        Generate mock odds from other sources
        """
        sources = []
        
        # Mock DraftKings odds
        draftkings_odds = self._get_mock_draftkings_odds(market_type, entity)
        if draftkings_odds:
            sources.append(draftkings_odds)
        
        # Mock Bet365 odds
        bet365_odds = self._get_mock_bet365_odds(market_type, entity)
        if bet365_odds:
            sources.append(bet365_odds)
        
        return sources
    
    def _get_mock_draftkings_odds(self, market_type: str, entity: str) -> Optional[Dict[str, Any]]:
        """Mock DraftKings odds"""
        # Slightly different odds than Pinnacle for arbitrage opportunities
        base_odds = {
            "NBA": {"Golden State Warriors": {"odds": -140, "implied_prob": 0.58}},
            "NFL": {"Dallas Cowboys": {"odds": +130, "implied_prob": 0.43}},
            "POLITICS": {"Donald Trump": {"odds": -105, "implied_prob": 0.51}},
            "FINANCE": {"Bitcoin": {"odds": +320, "implied_prob": 0.24}},
        }
        
        if market_type in base_odds and entity in base_odds[market_type]:
            data = base_odds[market_type][entity]
            return {
                "source": "DraftKings",
                "market_type": market_type,
                "entity": entity,
                "odds": data["odds"],
                "implied_probability": data["implied_prob"],
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.80
            }
        return None
    
    def _get_mock_bet365_odds(self, market_type: str, entity: str) -> Optional[Dict[str, Any]]:
        """Mock Bet365 odds"""
        base_odds = {
            "NBA": {"Golden State Warriors": {"odds": -160, "implied_prob": 0.62}},
            "NFL": {"Dallas Cowboys": {"odds": +110, "implied_prob": 0.48}},
            "POLITICS": {"Donald Trump": {"odds": -115, "implied_prob": 0.53}},
            "FINANCE": {"Bitcoin": {"odds": +280, "implied_prob": 0.26}},
        }
        
        if market_type in base_odds and entity in base_odds[market_type]:
            data = base_odds[market_type][entity]
            return {
                "source": "Bet365",
                "market_type": market_type,
                "entity": entity,
                "odds": data["odds"],
                "implied_probability": data["implied_prob"],
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.82
            }
        return None
    
    def calculate_consensus_odds(self, odds_sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate consensus odds from multiple sources
        """
        if not odds_sources:
            return None
        
        # Weight by confidence and recency
        total_weight = 0
        weighted_prob = 0
        
        for source in odds_sources:
            weight = source.get('confidence', 0.5)
            total_weight += weight
            weighted_prob += source['implied_probability'] * weight
        
        consensus_prob = weighted_prob / total_weight if total_weight > 0 else 0.5
        
        # Calculate consensus odds
        if consensus_prob > 0.5:
            consensus_odds = -100 * consensus_prob / (1 - consensus_prob)
        else:
            consensus_odds = 100 * (1 - consensus_prob) / consensus_prob
        
        return {
            "consensus_odds": round(consensus_odds),
            "consensus_probability": round(consensus_prob, 3),
            "sources_count": len(odds_sources),
            "confidence": min(0.95, total_weight / len(odds_sources)),
            "timestamp": datetime.now().isoformat()
        }
    
    def detect_arbitrage_opportunities(self, kalshi_price: float, benchmark_odds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect arbitrage opportunities between Kalshi and benchmark odds
        """
        opportunities = []
        
        for source in benchmark_odds:
            gap = kalshi_price - source['implied_probability']
            gap_percentage = (gap / source['implied_probability']) * 100
            
            if abs(gap) > 0.05:  # 5% threshold
                opportunity = {
                    "source": source['source'],
                    "kalshi_price": kalshi_price,
                    "benchmark_price": source['implied_probability'],
                    "gap": gap,
                    "gap_percentage": gap_percentage,
                    "recommendation": "LONG" if gap < -0.05 else "SHORT",
                    "confidence": min(0.95, abs(gap) * 10)
                }
                opportunities.append(opportunity)
        
        return opportunities
