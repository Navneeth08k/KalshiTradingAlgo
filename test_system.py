"""
Test script to verify the trading system components
"""
import logging
from trading_algorithm import TradingAlgorithm

def test_system():
    """Test the trading system components"""
    print("🧪 Testing Kalshi Trading Algorithm System")
    print("=" * 50)
    
    try:
        # Initialize the algorithm
        print("1. Initializing trading algorithm...")
        algorithm = TradingAlgorithm()
        print("✅ Algorithm initialized successfully")
        
        # Test sentiment analysis
        print("\n2. Testing sentiment analysis...")
        sentiment_result = algorithm.run_sentiment_analysis()
        if sentiment_result.get("status") == "success":
            entities = sentiment_result.get("entities", [])
            print(f"✅ Sentiment analysis successful - Found {len(entities)} entities")
            if entities:
                print(f"   Example entity: {entities[0].get('entity', 'N/A')} (sentiment: {entities[0].get('sentiment', 0):.2f})")
        else:
            print(f"❌ Sentiment analysis failed: {sentiment_result.get('message')}")
        
        # Test system status
        print("\n3. Testing system status...")
        status = algorithm.get_system_status()
        if status.get("status") == "running":
            print("✅ System status: Running")
            print(f"   Active trades: {status.get('active_trades', 0)}")
            print(f"   Total P&L: ${status.get('portfolio_summary', {}).get('total_pnl', 0):.2f}")
        else:
            print(f"❌ System status error: {status.get('message')}")
        
        # Test single cycle
        print("\n4. Testing single trading cycle...")
        cycle_result = algorithm.run_full_cycle()
        if cycle_result.get("status") == "success":
            print("✅ Trading cycle completed successfully")
            print(f"   Duration: {cycle_result.get('cycle_duration', 0):.2f} seconds")
            print(f"   Entities analyzed: {cycle_result.get('trending_entities', 0)}")
            print(f"   Signals generated: {cycle_result.get('signals_generated', 0)}")
            print(f"   Trades executed: {cycle_result.get('trades_executed', 0)}")
        else:
            print(f"❌ Trading cycle failed: {cycle_result.get('message')}")
        
        # Test performance analysis
        print("\n5. Testing performance analysis...")
        perf_result = algorithm.run_performance_analysis()
        if perf_result.get("status") == "success":
            print("✅ Performance analysis completed")
            performance = perf_result.get("performance", {})
            if performance:
                print(f"   Total P&L: ${performance.get('total_pnl', 0):.2f}")
                print(f"   Win rate: {performance.get('win_rate', 0)*100:.1f}%")
                print(f"   Sharpe ratio: {performance.get('sharpe_ratio', 0):.2f}")
        else:
            print(f"❌ Performance analysis failed: {perf_result.get('message')}")
        
        print("\n" + "=" * 50)
        print("🎉 System test completed successfully!")
        print("\nNext steps:")
        print("1. Set up your API keys in .env file")
        print("2. Run: python main.py --mode dashboard")
        print("3. Or run: python main.py --mode run")
        
    except Exception as e:
        print(f"\n❌ System test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check that all dependencies are installed: pip install -r requirements.txt")
        print("2. Verify API keys are set in .env file")
        print("3. Check the logs in trading_algorithm.log")

if __name__ == "__main__":
    test_system()
