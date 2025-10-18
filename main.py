"""
Main entry point for the Kalshi Trading Algorithm
"""
import argparse
import logging
import sys
from trading_algorithm import TradingAlgorithm

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Kalshi Trading Algorithm")
    parser.add_argument(
        "--mode", 
        choices=["run", "dashboard", "test", "analyze"], 
        default="run",
        help="Mode to run the algorithm"
    )
    parser.add_argument(
        "--cycle", 
        action="store_true",
        help="Run a single trading cycle"
    )
    parser.add_argument(
        "--sentiment", 
        action="store_true",
        help="Run sentiment analysis only"
    )
    parser.add_argument(
        "--performance", 
        action="store_true",
        help="Run performance analysis"
    )
    parser.add_argument(
        "--report", 
        action="store_true",
        help="Generate daily report"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize the algorithm
        algorithm = TradingAlgorithm()
        
        if args.mode == "run":
            if args.cycle:
                # Run single cycle
                print("Running single trading cycle...")
                result = algorithm.run_full_cycle()
                print(f"Cycle result: {result}")
            else:
                # Start automation
                print("Starting automated trading system...")
                algorithm.start_automation()
        
        elif args.mode == "dashboard":
            print("Starting Streamlit dashboard...")
            import subprocess
            subprocess.run(["streamlit", "run", "dashboard.py"])
        
        elif args.mode == "test":
            print("Running system test...")
            result = algorithm.run_full_cycle()
            print(f"Test result: {result}")
        
        elif args.mode == "analyze":
            if args.sentiment:
                print("Running sentiment analysis...")
                result = algorithm.run_sentiment_analysis()
                print(f"Sentiment result: {result}")
            
            elif args.performance:
                print("Running performance analysis...")
                result = algorithm.run_performance_analysis()
                print(f"Performance result: {result}")
            
            elif args.report:
                print("Generating daily report...")
                result = algorithm.run_daily_report()
                print(f"Report result: {result}")
            
            else:
                print("Please specify analysis type: --sentiment, --performance, or --report")
    
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
