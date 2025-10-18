"""
Main Trading Algorithm - Orchestrates the entire trading system
"""
import logging
import time
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from sentiment_engine import SentimentEngine
from market_mapper import MarketMapper
from benchmark_fetcher import BenchmarkFetcher
from signal_generator import SignalGenerator
from portfolio_tracker import PortfolioTracker
from feedback_loop import FeedbackLoop
from config import Config

class TradingAlgorithm:
    def __init__(self):
        """Initialize the trading algorithm"""
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        
        # Initialize components
        self.sentiment_engine = SentimentEngine()
        self.market_mapper = MarketMapper()
        self.benchmark_fetcher = BenchmarkFetcher()
        self.signal_generator = SignalGenerator()
        self.portfolio_tracker = PortfolioTracker()
        self.feedback_loop = FeedbackLoop()
        
        # Validate configuration
        try:
            Config.validate_config()
            self.logger.info("Configuration validated successfully")
        except ValueError as e:
            self.logger.error(f"Configuration error: {e}")
            raise
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(Config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
    
    def run_full_cycle(self) -> Dict[str, Any]:
        """
        Run the complete trading cycle:
        1. Get trending entities with sentiment
        2. Map to Kalshi markets
        3. Fetch benchmark odds
        4. Generate signals
        5. Execute trades
        6. Update portfolio
        """
        try:
            self.logger.info("Starting full trading cycle")
            cycle_start = datetime.now()
            
            # Step 1: Get trending entities with sentiment
            self.logger.info("Step 1: Analyzing sentiment for trending entities")
            trending_entities = self.sentiment_engine.get_trending_entities()
            
            if not trending_entities:
                self.logger.warning("No trending entities found")
                return {"status": "no_entities", "message": "No trending entities found"}
            
            self.logger.info(f"Found {len(trending_entities)} trending entities")
            
            # Step 2: Map entities to Kalshi markets
            self.logger.info("Step 2: Mapping entities to Kalshi markets")
            market_mappings = []
            for entity in trending_entities:
                mappings = self.market_mapper.map_entity_to_markets(
                    entity['entity'], entity['category']
                )
                for mapping in mappings:
                    mapping['sentiment_score'] = entity['sentiment']
                    mapping['sentiment_reason'] = entity.get('reason', '')
                market_mappings.extend(mappings)
            
            if not market_mappings:
                self.logger.warning("No market mappings found")
                return {"status": "no_mappings", "message": "No market mappings found"}
            
            self.logger.info(f"Found {len(market_mappings)} market mappings")
            
            # Step 3: Fetch benchmark odds
            self.logger.info("Step 3: Fetching benchmark odds")
            entities_with_odds = []
            for mapping in market_mappings:
                odds_sources = self.benchmark_fetcher.get_multiple_source_odds(
                    mapping['category'], mapping['entity']
                )
                
                if odds_sources:
                    consensus_odds = self.benchmark_fetcher.calculate_consensus_odds(odds_sources)
                    mapping['benchmark_price'] = consensus_odds['consensus_probability']
                    mapping['benchmark_confidence'] = consensus_odds['confidence']
                    entities_with_odds.append(mapping)
            
            if not entities_with_odds:
                self.logger.warning("No benchmark odds found")
                return {"status": "no_odds", "message": "No benchmark odds found"}
            
            self.logger.info(f"Found odds for {len(entities_with_odds)} entities")
            
            # Step 4: Generate signals
            self.logger.info("Step 4: Generating trading signals")
            signals = []
            for entity_data in entities_with_odds:
                # Mock Kalshi price (in real implementation, fetch from Kalshi API)
                kalshi_price = self._get_mock_kalshi_price(entity_data['kalshi_ticker'])
                
                signal = self.signal_generator.generate_signal(
                    entity=entity_data['entity'],
                    sentiment_score=entity_data['sentiment_score'],
                    kalshi_price=kalshi_price,
                    benchmark_price=entity_data['benchmark_price'],
                    confidence=entity_data.get('benchmark_confidence', 0.5)
                )
                
                signal['ticker'] = entity_data['kalshi_ticker']
                signal['market_name'] = entity_data['market_name']
                signals.append(signal)
            
            # Filter and rank signals
            filtered_signals = self.signal_generator.filter_signals(signals)
            ranked_signals = self.signal_generator.rank_signals(filtered_signals)
            
            self.logger.info(f"Generated {len(ranked_signals)} valid signals")
            
            # Step 5: Execute trades (simulation mode)
            self.logger.info("Step 5: Executing trades")
            executed_trades = []
            for signal in ranked_signals[:Config.MAX_DAILY_TRADES]:  # Limit daily trades
                if signal['signal'] != 'NONE':
                    # In simulation mode, we don't actually execute trades
                    trade = self.portfolio_tracker.execute_trade(
                        signal, signal['kalshi_price']
                    )
                    executed_trades.append(trade)
            
            self.logger.info(f"Executed {len(executed_trades)} trades")
            
            # Step 6: Update portfolio and generate report
            self.logger.info("Step 6: Updating portfolio and generating report")
            portfolio_summary = self.portfolio_tracker.get_portfolio_summary()
            
            cycle_end = datetime.now()
            cycle_duration = (cycle_end - cycle_start).total_seconds()
            
            return {
                "status": "success",
                "cycle_duration": cycle_duration,
                "trending_entities": len(trending_entities),
                "market_mappings": len(market_mappings),
                "signals_generated": len(signals),
                "trades_executed": len(executed_trades),
                "portfolio_summary": portfolio_summary,
                "timestamp": cycle_end.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in full trading cycle: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_mock_kalshi_price(self, ticker: str) -> float:
        """Get mock Kalshi price (replace with actual API call)"""
        # Mock prices based on ticker
        mock_prices = {
            "NBA_2025_GSW_CHAMPIONSHIP": 0.27,
            "NBA_2025_LAL_CHAMPIONSHIP": 0.15,
            "NBA_2025_BOS_CHAMPIONSHIP": 0.18,
            "NFL_2025_DAL_PLAYOFFS": 0.45,
            "NFL_2025_KC_CHAMPIONSHIP": 0.35,
            "PRES_2024_TRUMP": 0.52,
            "PRES_2024_BIDEN": 0.48,
            "BTC_2024_100K": 0.25,
            "SPY_2024_500": 0.60
        }
        return mock_prices.get(ticker, 0.50)  # Default to 50% if not found
    
    def run_sentiment_analysis(self) -> Dict[str, Any]:
        """Run sentiment analysis only"""
        try:
            self.logger.info("Running sentiment analysis")
            entities = self.sentiment_engine.get_trending_entities()
            return {"status": "success", "entities": entities}
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {e}")
            return {"status": "error", "message": str(e)}
    
    def run_market_mapping(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run market mapping for given entities"""
        try:
            self.logger.info("Running market mapping")
            mappings = []
            for entity in entities:
                entity_mappings = self.market_mapper.map_entity_to_markets(
                    entity['entity'], entity['category']
                )
                mappings.extend(entity_mappings)
            return {"status": "success", "mappings": mappings}
        except Exception as e:
            self.logger.error(f"Error in market mapping: {e}")
            return {"status": "error", "message": str(e)}
    
    def run_signal_generation(self, entities_with_odds: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run signal generation for given entities"""
        try:
            self.logger.info("Running signal generation")
            signals = []
            for entity_data in entities_with_odds:
                kalshi_price = self._get_mock_kalshi_price(entity_data['kalshi_ticker'])
                signal = self.signal_generator.generate_signal(
                    entity=entity_data['entity'],
                    sentiment_score=entity_data['sentiment_score'],
                    kalshi_price=kalshi_price,
                    benchmark_price=entity_data['benchmark_price'],
                    confidence=entity_data.get('benchmark_confidence', 0.5)
                )
                signals.append(signal)
            
            filtered_signals = self.signal_generator.filter_signals(signals)
            ranked_signals = self.signal_generator.rank_signals(filtered_signals)
            
            return {"status": "success", "signals": ranked_signals}
        except Exception as e:
            self.logger.error(f"Error in signal generation: {e}")
            return {"status": "error", "message": str(e)}
    
    def run_performance_analysis(self) -> Dict[str, Any]:
        """Run performance analysis"""
        try:
            self.logger.info("Running performance analysis")
            performance = self.feedback_loop.analyze_performance()
            return performance
        except Exception as e:
            self.logger.error(f"Error in performance analysis: {e}")
            return {"status": "error", "message": str(e)}
    
    def run_daily_report(self) -> Dict[str, Any]:
        """Generate daily report"""
        try:
            self.logger.info("Generating daily report")
            report = self.feedback_loop.generate_daily_report()
            return report
        except Exception as e:
            self.logger.error(f"Error generating daily report: {e}")
            return {"status": "error", "message": str(e)}
    
    def start_automation(self):
        """Start the automated trading system"""
        self.logger.info("Starting automated trading system")
        
        # Schedule regular runs
        schedule.every(Config.CHECK_INTERVAL_HOURS).hours.do(self.run_full_cycle)
        schedule.every().day.at("09:00").do(self.run_daily_report)
        schedule.every().week.do(self.run_performance_analysis)
        
        self.logger.info(f"Scheduled runs every {Config.CHECK_INTERVAL_HOURS} hours")
        
        # Run initial cycle
        self.run_full_cycle()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop_automation(self):
        """Stop the automated trading system"""
        self.logger.info("Stopping automated trading system")
        schedule.clear()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            portfolio_summary = self.portfolio_tracker.get_portfolio_summary()
            active_trades = self.portfolio_tracker.get_active_trades()
            
            return {
                "status": "running",
                "timestamp": datetime.now().isoformat(),
                "portfolio_summary": portfolio_summary,
                "active_trades": len(active_trades),
                "configuration": {
                    "sentiment_threshold": Config.SENTIMENT_THRESHOLD,
                    "price_gap_threshold": Config.PRICE_GAP_THRESHOLD,
                    "max_position_size": Config.MAX_POSITION_SIZE,
                    "check_interval_hours": Config.CHECK_INTERVAL_HOURS
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {"status": "error", "message": str(e)}
