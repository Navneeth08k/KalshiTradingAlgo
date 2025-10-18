"""
Signal Generator - Generates trading signals based on sentiment and price gaps
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from config import Config

class SignalGenerator:
    def __init__(self):
        """Initialize the signal generator"""
        self.logger = logging.getLogger(__name__)
        self.sentiment_threshold = Config.SENTIMENT_THRESHOLD
        self.price_gap_threshold = Config.PRICE_GAP_THRESHOLD
    
    def generate_signal(self, 
                       entity: str, 
                       sentiment_score: float, 
                       kalshi_price: float, 
                       benchmark_price: float,
                       confidence: float = 0.5) -> Dict[str, Any]:
        """
        Generate trading signal based on sentiment and price gap
        """
        try:
            # Calculate price gap
            price_gap = kalshi_price - benchmark_price
            gap_percentage = (price_gap / benchmark_price) * 100 if benchmark_price > 0 else 0
            
            # Determine signal strength
            signal_strength = self._calculate_signal_strength(
                sentiment_score, price_gap, confidence
            )
            
            # Generate signal
            signal = self._determine_signal(
                sentiment_score, price_gap, signal_strength
            )
            
            # Calculate position size
            position_size = self._calculate_position_size(
                signal_strength, price_gap, confidence
            )
            
            # Generate risk metrics
            risk_metrics = self._calculate_risk_metrics(
                kalshi_price, benchmark_price, signal_strength
            )
            
            signal_data = {
                "entity": entity,
                "timestamp": datetime.now().isoformat(),
                "sentiment_score": sentiment_score,
                "kalshi_price": kalshi_price,
                "benchmark_price": benchmark_price,
                "price_gap": price_gap,
                "gap_percentage": gap_percentage,
                "signal": signal,
                "signal_strength": signal_strength,
                "position_size": position_size,
                "confidence": confidence,
                "risk_metrics": risk_metrics,
                "reasoning": self._generate_signal_reasoning(
                    sentiment_score, price_gap, signal
                )
            }
            
            self.logger.info(f"Generated {signal} signal for {entity} with strength {signal_strength:.2f}")
            return signal_data
            
        except Exception as e:
            self.logger.error(f"Error generating signal: {e}")
            return self._create_error_signal(entity, str(e))
    
    def _calculate_signal_strength(self, 
                                 sentiment_score: float, 
                                 price_gap: float, 
                                 confidence: float) -> float:
        """
        Calculate signal strength based on multiple factors
        """
        # Normalize sentiment score to 0-1 range
        sentiment_factor = (sentiment_score + 1) / 2
        
        # Price gap factor (absolute value)
        gap_factor = min(1.0, abs(price_gap) / 0.2)  # Cap at 20% gap
        
        # Confidence factor
        confidence_factor = confidence
        
        # Weighted combination
        signal_strength = (
            0.4 * sentiment_factor +
            0.4 * gap_factor +
            0.2 * confidence_factor
        )
        
        return min(1.0, signal_strength)
    
    def _determine_signal(self, 
                         sentiment_score: float, 
                         price_gap: float, 
                         signal_strength: float) -> str:
        """
        Determine the trading signal (LONG, SHORT, or NONE)
        """
        # Check if signal is strong enough
        if signal_strength < 0.6:
            return "NONE"
        
        # Check sentiment threshold
        if abs(sentiment_score) < self.sentiment_threshold:
            return "NONE"
        
        # Check price gap threshold
        if abs(price_gap) < self.price_gap_threshold:
            return "NONE"
        
        # Determine direction
        if sentiment_score > 0 and price_gap < -self.price_gap_threshold:
            return "LONG"  # Positive sentiment, Kalshi undervalued
        elif sentiment_score < 0 and price_gap > self.price_gap_threshold:
            return "SHORT"  # Negative sentiment, Kalshi overvalued
        else:
            return "NONE"
    
    def _calculate_position_size(self, 
                               signal_strength: float, 
                               price_gap: float, 
                               confidence: float) -> float:
        """
        Calculate position size based on signal strength and risk
        """
        # Base position size
        base_size = Config.MAX_POSITION_SIZE * 0.1  # 10% of max position
        
        # Adjust for signal strength
        strength_multiplier = signal_strength
        
        # Adjust for price gap (larger gaps = larger positions)
        gap_multiplier = min(2.0, abs(price_gap) / 0.1)  # Cap at 2x for 10%+ gaps
        
        # Adjust for confidence
        confidence_multiplier = confidence
        
        # Calculate final position size
        position_size = (
            base_size * 
            strength_multiplier * 
            gap_multiplier * 
            confidence_multiplier
        )
        
        return min(Config.MAX_POSITION_SIZE, position_size)
    
    def _calculate_risk_metrics(self, 
                              kalshi_price: float, 
                              benchmark_price: float, 
                              signal_strength: float) -> Dict[str, float]:
        """
        Calculate risk metrics for the signal
        """
        # Stop loss level
        stop_loss = kalshi_price * (1 - Config.STOP_LOSS_PERCENTAGE)
        
        # Take profit level (based on price gap)
        take_profit = benchmark_price
        
        # Risk-reward ratio
        risk = kalshi_price - stop_loss
        reward = take_profit - kalshi_price
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        # Expected value (simplified)
        expected_value = (take_profit - kalshi_price) * signal_strength
        
        return {
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_reward_ratio": risk_reward_ratio,
            "expected_value": expected_value,
            "max_loss": risk,
            "max_gain": reward
        }
    
    def _generate_signal_reasoning(self, 
                                 sentiment_score: float, 
                                 price_gap: float, 
                                 signal: str) -> str:
        """
        Generate human-readable reasoning for the signal
        """
        if signal == "NONE":
            return "Insufficient signal strength or unclear market direction"
        
        sentiment_desc = "positive" if sentiment_score > 0 else "negative"
        gap_desc = "undervalued" if price_gap < 0 else "overvalued"
        
        if signal == "LONG":
            return f"LONG signal: {sentiment_desc} sentiment suggests Kalshi is {gap_desc} relative to benchmark"
        elif signal == "SHORT":
            return f"SHORT signal: {sentiment_desc} sentiment suggests Kalshi is {gap_desc} relative to benchmark"
        
        return "Signal analysis completed"
    
    def _create_error_signal(self, entity: str, error: str) -> Dict[str, Any]:
        """
        Create error signal when generation fails
        """
        return {
            "entity": entity,
            "timestamp": datetime.now().isoformat(),
            "signal": "ERROR",
            "signal_strength": 0.0,
            "position_size": 0.0,
            "confidence": 0.0,
            "error": error,
            "reasoning": f"Signal generation failed: {error}"
        }
    
    def batch_generate_signals(self, 
                             entities_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate signals for multiple entities
        """
        signals = []
        
        for entity_data in entities_data:
            signal = self.generate_signal(
                entity=entity_data.get('entity', ''),
                sentiment_score=entity_data.get('sentiment', 0.0),
                kalshi_price=entity_data.get('kalshi_price', 0.0),
                benchmark_price=entity_data.get('benchmark_price', 0.0),
                confidence=entity_data.get('confidence', 0.5)
            )
            signals.append(signal)
        
        return signals
    
    def filter_signals(self, signals: List[Dict[str, Any]], 
                      min_strength: float = 0.6) -> List[Dict[str, Any]]:
        """
        Filter signals based on minimum strength and other criteria
        """
        filtered_signals = []
        
        for signal in signals:
            if (signal.get('signal') != 'NONE' and 
                signal.get('signal') != 'ERROR' and
                signal.get('signal_strength', 0) >= min_strength):
                filtered_signals.append(signal)
        
        return filtered_signals
    
    def rank_signals(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank signals by potential profitability
        """
        def signal_score(signal):
            strength = signal.get('signal_strength', 0)
            confidence = signal.get('confidence', 0)
            gap_percentage = abs(signal.get('gap_percentage', 0))
            
            return strength * confidence * (1 + gap_percentage / 100)
        
        return sorted(signals, key=signal_score, reverse=True)
