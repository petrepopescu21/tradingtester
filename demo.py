"""Demo script showing how to use Trading Tester programmatically."""

from backend.strategy_parser.parser import StrategyParser
from backend.llm.client import ClaudeClient
from backend.code_generator.generator import CodeGenerator
from backend.data.fetcher import DataFetcher
from backend.backtester.engine import BacktestEngine
import json


def demo_basic_test():
    """Demo: Test a single strategy."""
    print("=" * 60)
    print("DEMO: Basic Strategy Test")
    print("=" * 60)

    # 1. Parse strategy
    print("\n1. Parsing strategy...")
    parser = StrategyParser()
    strategy = parser.parse_file("strategies/rsi_mean_reversion.md")
    print(f"   Strategy: {strategy.name}")
    print(f"   Entry Rules: {strategy.entry_rules[:100]}...")

    # 2. Generate code
    print("\n2. Generating code with Claude...")
    generator = CodeGenerator()
    class_name, code = generator.generate(strategy, validate=True)
    print(f"   Generated class: {class_name}")
    print(f"   Code length: {len(code)} characters")

    # Save generated code for inspection
    with open("generated/rsi_strategy_code.py", "w") as f:
        f.write(code)
    print("   Saved to: generated/rsi_strategy_code.py")

    # 3. Load strategy class
    print("\n3. Loading strategy class...")
    namespace = {}
    exec(code, namespace)
    strategy_class = namespace[class_name]
    strategy_instance = strategy_class(strategy.name)
    print("   Strategy loaded successfully")

    # 4. Fetch data
    print("\n4. Fetching historical data...")
    fetcher = DataFetcher()
    data = fetcher.fetch("AAPL", "2022-01-01", "2023-12-31")
    print(f"   Fetched {len(data)} data points for AAPL")

    # 5. Run backtest
    print("\n5. Running backtest...")
    engine = BacktestEngine()
    result = engine.run(strategy_instance, data, "AAPL")

    # 6. Display results
    print("\n6. Results:")
    print(f"   Total Return: ${result.total_return:,.2f} ({result.total_return_pct:.2f}%)")
    print(f"   Number of Trades: {result.num_trades}")
    print(f"   Win Rate: {result.win_rate * 100:.2f}%")
    print(f"   Sharpe Ratio: {result.sharpe_ratio:.3f}")
    print(f"   Max Drawdown: ${result.max_drawdown:,.2f} ({result.max_drawdown_pct:.2f}%)")

    # Save results
    with open("reports/demo_results.json", "w") as f:
        json.dump(result.to_dict(), f, indent=2)
    print("\n   Full results saved to: reports/demo_results.json")


def demo_generate_variations():
    """Demo: Generate strategy variations."""
    print("\n" + "=" * 60)
    print("DEMO: Generate Strategy Variations")
    print("=" * 60)

    # 1. Parse original strategy
    parser = StrategyParser()
    strategy = parser.parse_file("strategies/rsi_mean_reversion.md")
    print(f"\nOriginal strategy: {strategy.name}")

    # 2. Generate variations
    print("\nGenerating 3 variations with Claude...")
    client = ClaudeClient()
    variations = client.generate_variations(strategy.raw_content, num_variations=3)

    print(f"\nGenerated {len(variations)} variations:")

    # 3. Save variations
    for i, variation_content in enumerate(variations, 1):
        try:
            var_strategy = parser.parse(variation_content)
            filename = f"generated/{var_strategy.name.lower().replace(' ', '_')}.md"
        except Exception:
            filename = f"generated/variation_{i}.md"

        with open(filename, "w") as f:
            f.write(variation_content)

        print(f"   {i}. Saved to: {filename}")


def demo_batch_test():
    """Demo: Batch test multiple strategies."""
    print("\n" + "=" * 60)
    print("DEMO: Batch Test Multiple Strategies")
    print("=" * 60)

    symbols = ["AAPL", "MSFT"]
    strategies = ["strategies/rsi_mean_reversion.md", "strategies/momentum_breakout.md"]

    print(f"\nTesting {len(strategies)} strategies on {len(symbols)} symbols")

    results = []

    for strategy_file in strategies:
        print(f"\nStrategy: {strategy_file}")

        # Parse and generate code
        parser = StrategyParser()
        strategy = parser.parse_file(strategy_file)

        generator = CodeGenerator()
        class_name, code = generator.generate(strategy, validate=True)

        namespace = {}
        exec(code, namespace)
        strategy_class = namespace[class_name]

        for symbol in symbols:
            print(f"  Testing {symbol}...", end=" ")

            try:
                strategy_instance = strategy_class(strategy.name)

                fetcher = DataFetcher()
                data = fetcher.fetch(symbol, "2022-01-01", "2023-12-31")

                engine = BacktestEngine()
                result = engine.run(strategy_instance, data, symbol)

                print(f"Return: {result.total_return_pct:+.2f}%, Sharpe: {result.sharpe_ratio:.2f}")

                results.append({
                    "strategy": strategy.name,
                    "symbol": symbol,
                    "return_pct": result.total_return_pct,
                    "sharpe_ratio": result.sharpe_ratio,
                    "num_trades": result.num_trades
                })

            except Exception as e:
                print(f"Error: {str(e)}")

    # Save summary
    with open("reports/batch_summary.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nBatch results saved to: reports/batch_summary.json")


if __name__ == "__main__":
    import sys

    print("\n" + "=" * 60)
    print("Trading Tester - Demo Script")
    print("=" * 60)
    print("\nThis demo shows how to use Trading Tester programmatically.")
    print("\nAvailable demos:")
    print("  1. Basic strategy test")
    print("  2. Generate variations")
    print("  3. Batch test")
    print("  all. Run all demos")

    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("\nEnter choice (1/2/3/all): ").strip()

    try:
        if choice == "1":
            demo_basic_test()
        elif choice == "2":
            demo_generate_variations()
        elif choice == "3":
            demo_batch_test()
        elif choice == "all":
            demo_basic_test()
            demo_generate_variations()
            demo_batch_test()
        else:
            print("Invalid choice")

        print("\n" + "=" * 60)
        print("Demo complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running demo: {str(e)}")
        import traceback
        traceback.print_exc()
