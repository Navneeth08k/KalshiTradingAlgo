"""
System Validation Test - Comprehensive testing of all components
"""
import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from sentiment_engine import SentimentEngine
from market_mapper import MarketMapper
from benchmark_fetcher import BenchmarkFetcher
from signal_generator import SignalGenerator
from portfolio_tracker import PortfolioTracker
from kalshi_api import KalshiAPI
from trading_algorithm import TradingAlgorithm

class SystemValidator:
    def __init__(self):
        """Initialize the system validator"""
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
        self.test_results = {}
    
    def setup_logging(self):
        """Setup logging for validation"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all system validation tests"""
        self.logger.info("Starting comprehensive system validation")
        
        tests = [
            ("config_validation", self.test_config_validation),
            ("sentiment_engine", self.test_sentiment_engine),
            ("market_mapper", self.test_market_mapper),
            ("benchmark_fetcher", self.test_benchmark_fetcher),
            ("signal_generator", self.test_signal_generator),
            ("portfolio_tracker", self.test_portfolio_tracker),
            ("kalshi_api", self.test_kalshi_api),
            ("trading_algorithm", self.test_trading_algorithm),
            ("integration_test", self.test_integration)
        ]
        
        for test_name, test_func in tests:
            try:
                self.logger.info(f"Running {test_name}...")
                result = test_func()
                self.test_results[test_name] = result
                status = "PASS" if result.get('success', False) else "FAIL"
                self.logger.info(f"{test_name}: {status}")
            except Exception as e:
                self.logger.error(f"{test_name} failed with exception: {e}")
                self.test_results[test_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        return self.generate_report()
    
    def test_config_validation(self) -> Dict[str, Any]:
        """Test configuration validation"""
        try:
            Config.validate_config()
            return {
                'success': True,
                'message': 'Configuration validation passed',
                'required_keys': ['GEMINI_API_KEY'],
                'optional_keys': ['THE_ODDS_API_KEY', 'KALSHI_API_KEY']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Configuration validation failed'
            }
    
    def test_sentiment_engine(self) -> Dict[str, Any]:
        """Test sentiment engine functionality"""
        try:
            engine = SentimentEngine()
            
            # Test trending entities
            entities = engine.get_trending_entities()
            
            if not entities:
                return {
                    'success': False,
                    'message': 'No entities returned from sentiment engine'
                }
            
            # Validate entity structure
            for entity in entities[:3]:  # Test first 3 entities
                if not self.validate_entity_structure(entity):
                    return {
                        'success': False,
                        'message': f'Invalid entity structure: {entity}'
                    }
            
            return {
                'success': True,
                'message': f'Sentiment engine working, found {len(entities)} entities',
                'sample_entities': entities[:3]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Sentiment engine test failed'
            }
    
    def test_market_mapper(self) -> Dict[str, Any]:
        """Test market mapper functionality"""
        try:
            mapper = MarketMapper()
            
            # Test mapping
            test_entity = "Golden State Warriors"
            test_category = "NBA"
            mappings = mapper.map_entity_to_markets(test_entity, test_category)
            
            if not mappings:
                return {
                    'success': False,
                    'message': 'No mappings returned from market mapper'
                }
            
            # Validate mapping structure
            for mapping in mappings:
                if not self.validate_mapping_structure(mapping):
                    return {
                        'success': False,
                        'message': f'Invalid mapping structure: {mapping}'
                    }
            
            return {
                'success': True,
                'message': f'Market mapper working, found {len(mappings)} mappings',
                'sample_mappings': mappings[:2]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Market mapper test failed'
            }
    
    def test_benchmark_fetcher(self) -> Dict[str, Any]:
        """Test benchmark fetcher functionality"""
        try:
            fetcher = BenchmarkFetcher()
            
            # Test odds fetching
            test_sport = "NBA"
            test_entity = "Golden State Warriors"
            odds_sources = fetcher.get_multiple_source_odds(test_sport, test_entity)
            
            if not odds_sources:
                return {
                    'success': False,
                    'message': 'No odds sources returned from benchmark fetcher'
                }
            
            # Test consensus calculation
            consensus = fetcher.calculate_consensus_odds(odds_sources)
            
            if not consensus:
                return {
                    'success': False,
                    'message': 'Consensus calculation failed'
                }
            
            return {
                'success': True,
                'message': f'Benchmark fetcher working, found {len(odds_sources)} sources',
                'consensus_odds': consensus
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Benchmark fetcher test failed'
            }
    
    def test_signal_generator(self) -> Dict[str, Any]:
        """Test signal generator functionality"""
        try:
            generator = SignalGenerator()
            
            # Test signal generation
            test_signal = generator.generate_signal(
                entity="Golden State Warriors",
                sentiment_score=0.75,
                kalshi_price=0.27,
                benchmark_price=0.30,
                confidence=0.8
            )
            
            if not test_signal:
                return {
                    'success': False,
                    'message': 'No signal generated'
                }
            
            # Validate signal structure
            if not self.validate_signal_structure(test_signal):
                return {
                    'success': False,
                    'message': f'Invalid signal structure: {test_signal}'
                }
            
            return {
                'success': True,
                'message': 'Signal generator working',
                'sample_signal': test_signal
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Signal generator test failed'
            }
    
    def test_portfolio_tracker(self) -> Dict[str, Any]:
        """Test portfolio tracker functionality"""
        try:
            tracker = PortfolioTracker()
            
            # Test portfolio summary
            summary = tracker.get_portfolio_summary()
            
            if not isinstance(summary, dict):
                return {
                    'success': False,
                    'message': 'Portfolio summary not returned as dict'
                }
            
            # Test active trades
            active_trades = tracker.get_active_trades()
            
            if not isinstance(active_trades, list):
                return {
                    'success': False,
                    'message': 'Active trades not returned as list'
                }
            
            return {
                'success': True,
                'message': 'Portfolio tracker working',
                'portfolio_summary': summary,
                'active_trades_count': len(active_trades)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Portfolio tracker test failed'
            }
    
    def test_kalshi_api(self) -> Dict[str, Any]:
        """Test Kalshi API functionality"""
        try:
            api = KalshiAPI()
            
            # Test markets
            markets = api.get_markets(limit=5)
            
            if not markets:
                return {
                    'success': False,
                    'message': 'No markets returned from Kalshi API'
                }
            
            # Test market price - use a real ticker from the markets
            if markets:
                test_ticker = markets[0].get('ticker')
                if test_ticker:
                    price = api.get_market_price(test_ticker)
                    
                    # Price can be None for some markets, that's okay
                    # Just check that the API call doesn't crash
                    return {
                        'success': True,
                        'message': 'Kalshi API working',
                        'markets_count': len(markets),
                        'test_ticker': test_ticker,
                        'price': price
                    }
            
            return {
                'success': True,
                'message': f'Kalshi API working, found {len(markets)} markets',
                'sample_markets': markets[:2]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Kalshi API test failed'
            }
    
    def test_trading_algorithm(self) -> Dict[str, Any]:
        """Test trading algorithm functionality"""
        try:
            algorithm = TradingAlgorithm()
            
            # Test system status
            status = algorithm.get_system_status()
            
            if not isinstance(status, dict):
                return {
                    'success': False,
                    'message': 'System status not returned as dict'
                }
            
            # Test sentiment analysis
            sentiment_result = algorithm.run_sentiment_analysis()
            
            if not isinstance(sentiment_result, dict):
                return {
                    'success': False,
                    'message': 'Sentiment analysis not returned as dict'
                }
            
            return {
                'success': True,
                'message': 'Trading algorithm working',
                'system_status': status,
                'sentiment_result': sentiment_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Trading algorithm test failed'
            }
    
    def test_integration(self) -> Dict[str, Any]:
        """Test full integration"""
        try:
            algorithm = TradingAlgorithm()
            
            # Test a single cycle (this might take a while)
            self.logger.info("Running integration test - this may take a few minutes...")
            result = algorithm.run_full_cycle()
            
            if not isinstance(result, dict):
                return {
                    'success': False,
                    'message': 'Full cycle not returned as dict'
                }
            
            if result.get('status') == 'error':
                return {
                    'success': False,
                    'message': f'Full cycle failed: {result.get("message", "Unknown error")}'
                }
            
            return {
                'success': True,
                'message': 'Integration test passed',
                'cycle_result': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Integration test failed'
            }
    
    def validate_entity_structure(self, entity: Dict[str, Any]) -> bool:
        """Validate entity data structure"""
        required_fields = ['entity', 'category', 'sentiment']
        return all(field in entity for field in required_fields)
    
    def validate_mapping_structure(self, mapping: Dict[str, Any]) -> bool:
        """Validate mapping data structure"""
        required_fields = ['entity', 'category', 'kalshi_ticker', 'market_name']
        return all(field in mapping for field in required_fields)
    
    def validate_signal_structure(self, signal: Dict[str, Any]) -> bool:
        """Validate signal data structure"""
        required_fields = ['entity', 'signal', 'signal_strength', 'timestamp']
        return all(field in signal for field in required_fields)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('success', False))
        failed_tests = total_tests - passed_tests
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            },
            'test_results': self.test_results,
            'recommendations': self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        for test_name, result in self.test_results.items():
            if not result.get('success', False):
                if test_name == 'config_validation':
                    recommendations.append("Set up required API keys in .env file")
                elif test_name == 'sentiment_engine':
                    recommendations.append("Check Gemini API key and connectivity")
                elif test_name == 'kalshi_api':
                    recommendations.append("Check Kalshi API key and connectivity")
                elif test_name == 'benchmark_fetcher':
                    recommendations.append("Check The Odds API key or use mock data")
        
        if not recommendations:
            recommendations.append("All tests passed! System is ready for use.")
        
        return recommendations

def main():
    """Main function to run system validation"""
    validator = SystemValidator()
    report = validator.run_all_tests()
    
    print("\n" + "="*60)
    print("SYSTEM VALIDATION REPORT")
    print("="*60)
    
    summary = report['summary']
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    
    print("\nRECOMMENDATIONS:")
    for rec in report['recommendations']:
        print(f"- {rec}")
    
    print("\nDETAILED RESULTS:")
    for test_name, result in report['test_results'].items():
        status = "PASS" if result.get('success', False) else "FAIL"
        print(f"{test_name}: {status}")
        if not result.get('success', False) and 'error' in result:
            print(f"  Error: {result['error']}")
    
    return report

if __name__ == "__main__":
    main()
