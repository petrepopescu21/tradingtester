# Trading Tester - Project Summary

## Overview

Trading Tester is a complete LLM-powered trading strategy testing framework that enables rapid iteration and testing of trading strategies using Anthropic Claude AI.

## What Has Been Built (Phase 1 - MVP)

### ✓ Project Structure
- Modern Python project with `pyproject.toml`
- Organized module structure
- Environment configuration
- Documentation

### ✓ Core Modules

#### 1. Strategy Parser (`backend/strategy_parser/`)
- Parses markdown strategies with structured sections
- Validates required sections
- Extracts metadata
- Type-safe with Pydantic models

**Key File**: `parser.py`
- Class: `StrategyParser`
- Class: `ParsedStrategy` (data model)

#### 2. LLM Integration (`backend/llm/`)
- Claude API client with prompt caching support
- Specialized prompts for strategy variation and code generation
- Code validation capabilities

**Key Files**:
- `client.py` - `ClaudeClient` class
- `prompts.py` - `PromptTemplates` class

#### 3. Code Generator (`backend/code_generator/`)
- Converts markdown strategies to executable Python code
- Base strategy class for all implementations
- Automatic code validation and correction

**Key Files**:
- `generator.py` - `CodeGenerator` class
- `base_strategy.py` - `Strategy` base class

#### 4. Data Management (`backend/data/`)
- yfinance integration for historical data
- Local caching for performance
- Support for multiple symbols and timeframes

**Key File**: `fetcher.py`
- Class: `DataFetcher`

#### 5. Backtesting Engine (`backend/backtester/`)
- Vectorized backtesting with pandas
- Comprehensive performance metrics
- Trade-by-trade logging
- Equity curve tracking

**Key File**: `engine.py`
- Class: `BacktestEngine`
- Class: `BacktestResult` (data model)

#### 6. CLI Interface (`backend/cli/`)
- Three main commands: `test`, `generate`, `batch`
- Rich terminal output with tables
- JSON export capabilities
- Progress tracking

**Key File**: `main.py`

### ✓ Example Strategies

Two complete example strategies provided:

1. **RSI Mean Reversion** (`strategies/rsi_mean_reversion.md`)
   - Oversold/overbought entry signals
   - Multiple exit conditions
   - Risk management rules

2. **Momentum Breakout** (`strategies/momentum_breakout.md`)
   - Breakout entry with volume confirmation
   - Trailing stop loss
   - Volatility-based position sizing

### ✓ Documentation

- `README.md` - Project overview
- `INSTALL.md` - Installation instructions
- `GETTING_STARTED.md` - Comprehensive guide
- `PROJECT_SUMMARY.md` - This file
- `demo.py` - Programmatic usage examples

## File Structure

```
tradingtester/
├── backend/
│   ├── __init__.py
│   ├── strategy_parser/
│   │   ├── __init__.py
│   │   └── parser.py              # Parse markdown strategies
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py              # Claude API client
│   │   └── prompts.py             # Prompt templates
│   ├── code_generator/
│   │   ├── __init__.py
│   │   ├── base_strategy.py       # Base Strategy class
│   │   └── generator.py           # Convert strategy to code
│   ├── backtester/
│   │   ├── __init__.py
│   │   └── engine.py              # Backtesting engine
│   ├── data/
│   │   ├── __init__.py
│   │   └── fetcher.py             # Data fetching with yfinance
│   └── cli/
│       ├── __init__.py
│       └── main.py                # CLI commands
├── strategies/
│   ├── rsi_mean_reversion.md
│   └── momentum_breakout.md
├── generated/                      # LLM-generated variations
│   └── .gitkeep
├── reports/                        # Backtest results
│   └── .gitkeep
├── pyproject.toml                 # Project config
├── requirements.txt               # Dependencies
├── .env.example                   # Environment template
├── .gitignore
├── README.md
├── INSTALL.md
├── GETTING_STARTED.md
├── PROJECT_SUMMARY.md
└── demo.py                        # Demo script
```

## How to Use

### Installation

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install
pip install -e .

# 3. Configure
copy .env.example .env
# Edit .env and add ANTHROPIC_API_KEY
```

### CLI Commands

```bash
# Test a single strategy
tradingtester test strategies/rsi_mean_reversion.md \
  --symbol AAPL \
  --start 2020-01-01 \
  --end 2023-12-31

# Generate variations
tradingtester generate strategies/rsi_mean_reversion.md \
  --variations 5

# Batch test
tradingtester batch strategies/ \
  --symbols AAPL,MSFT,GOOGL
```

### Programmatic Usage

```python
from backend.strategy_parser.parser import StrategyParser
from backend.code_generator.generator import CodeGenerator
from backend.data.fetcher import DataFetcher
from backend.backtester.engine import BacktestEngine

# Parse strategy
parser = StrategyParser()
strategy = parser.parse_file("strategies/rsi_mean_reversion.md")

# Generate code
generator = CodeGenerator()
class_name, code = generator.generate(strategy)

# Load strategy
namespace = {}
exec(code, namespace)
strategy_instance = namespace[class_name](strategy.name)

# Fetch data
fetcher = DataFetcher()
data = fetcher.fetch("AAPL", "2020-01-01", "2023-12-31")

# Run backtest
engine = BacktestEngine()
result = engine.run(strategy_instance, data, "AAPL")

# View results
print(f"Return: {result.total_return_pct:.2f}%")
print(f"Sharpe: {result.sharpe_ratio:.2f}")
```

## Key Features Implemented

### 1. Hybrid Markdown Format
- Structured sections (Entry Rules, Exit Rules, etc.)
- Natural language descriptions within sections
- Easy to read and write
- Parseable by both humans and LLMs

### 2. LLM-Powered Variation Generation
- Claude generates N variations of any strategy
- Explores parameter space intelligently
- Maintains strategy structure
- Creates meaningfully different approaches

### 3. Automated Code Generation
- Natural language → executable Python
- Implements technical indicators
- Signal generation logic
- Position sizing algorithms
- Exit condition checking

### 4. Comprehensive Backtesting
- Day-by-day simulation
- Commission accounting
- Position tracking
- Multiple performance metrics:
  - Total return & %
  - Win rate
  - Average win/loss
  - Maximum drawdown
  - Sharpe ratio
  - Complete trade log

### 5. Flexible Data Handling
- yfinance for free market data
- Local caching for performance
- Support for stocks, ETFs, indices
- Easy to extend to other data sources

## Performance Metrics Calculated

The backtester calculates:

1. **Returns**
   - Total return ($)
   - Total return (%)

2. **Trade Statistics**
   - Number of trades
   - Winning trades
   - Losing trades
   - Win rate (%)

3. **Risk Metrics**
   - Average win
   - Average loss
   - Maximum drawdown ($)
   - Maximum drawdown (%)
   - Sharpe ratio

4. **Trade Details**
   - Entry/exit dates
   - Entry/exit prices
   - Position size
   - P&L per trade
   - Days held

5. **Equity Curve**
   - Portfolio value over time
   - Used for drawdown calculation
   - Can be visualized (Phase 2)

## Dependencies

### Core
- `anthropic` - Claude API
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `yfinance` - Market data
- `pydantic` - Data validation
- `python-dotenv` - Environment management
- `click` - CLI framework
- `rich` - Terminal formatting

### Dev (Optional)
- `pytest` - Testing
- `black` - Code formatting
- `ruff` - Linting
- `mypy` - Type checking

## What's Next (Future Phases)

### Phase 2: Enhancement
- [ ] TypeScript/React frontend
- [ ] Interactive charts (Plotly/Recharts)
- [ ] HTML report generation
- [ ] Parallel strategy execution
- [ ] Additional data sources (Alpha Vantage, Alpaca)
- [ ] Strategy comparison dashboard

### Phase 3: Advanced Features
- [ ] Portfolio-level backtesting
- [ ] Walk-forward optimization
- [ ] Monte Carlo simulation
- [ ] Parameter optimization
- [ ] Real-time paper trading
- [ ] Strategy evolution/genetic algorithms
- [ ] Multi-asset support
- [ ] Transaction cost analysis

## Technical Decisions

### Why Python?
- Excellent financial libraries (pandas, numpy)
- Strong LLM API support
- Large quant/trading community
- Easy to prototype and iterate

### Why Anthropic Claude?
- Superior reasoning for strategy variations
- Good at code generation
- Prompt caching for cost efficiency
- Latest model (Sonnet 4.5) is fast and capable

### Why yfinance?
- Free and easy to use
- Good coverage of US stocks
- Sufficient for MVP
- Can be extended with other sources

### Why Markdown for Strategies?
- Human-readable
- Easy to version control
- LLM-friendly format
- Structured yet flexible

### Why Pydantic?
- Type safety
- Automatic validation
- Great for data models
- Good IDE support

## Testing the System

### Option 1: Use CLI
```bash
tradingtester test strategies/rsi_mean_reversion.md --symbol AAPL
```

### Option 2: Use Demo Script
```bash
python demo.py 1    # Basic test
python demo.py 2    # Generate variations
python demo.py 3    # Batch test
python demo.py all  # Run all demos
```

### Option 3: Write Your Own Strategy
1. Copy an example strategy
2. Modify the rules
3. Test it: `tradingtester test your_strategy.md`

## Limitations & Considerations

### Current Limitations
1. **No Short Selling**: Basic implementation supports long-only (can be extended)
2. **Simple Position Sizing**: Fixed or percentage-based (can add more sophisticated methods)
3. **Daily Data Only**: Higher-frequency data requires code changes
4. **No Slippage Modeling**: Assumes fills at close price
5. **Basic Commission Model**: Flat percentage (can add tiered structures)

### LLM Considerations
1. **API Costs**: Each code generation costs ~$0.01-0.10 depending on strategy complexity
2. **Rate Limits**: Be mindful of API rate limits for batch operations
3. **Code Quality**: Generated code should be reviewed, especially for complex strategies
4. **Validation**: Always validate generated code before running on real capital

### Data Considerations
1. **Historical Bias**: Past performance ≠ future results
2. **Survivorship Bias**: yfinance data may have survivorship bias
3. **Lookback Period**: Ensure sufficient data for indicators
4. **Market Regime**: Strategies may work differently in different market conditions

## Best Practices

### Writing Strategies
1. Be specific and clear in rules
2. Include explicit risk management
3. Define all parameters
4. Consider edge cases
5. Start simple, iterate

### Testing Strategies
1. Use realistic date ranges (multiple years)
2. Test on multiple symbols
3. Compare against buy-and-hold
4. Check sensitivity to parameters
5. Review individual trades

### Using Variations
1. Generate 5-10 variations
2. Test all on same data
3. Compare performance
4. Identify robust patterns
5. Avoid overfitting

## Troubleshooting

See [INSTALL.md](INSTALL.md) for common issues.

Quick fixes:
- **Import errors**: Run `pip install -e .`
- **API key errors**: Check `.env` file
- **No data**: Check symbol and date range
- **Code errors**: Try regenerating with `validate=True`

## Contributing Ideas

Future contributors could add:
- More example strategies
- Additional technical indicators
- Better visualization
- Optimization algorithms
- Risk management tools
- Portfolio analytics
- More data sources
- Live trading integration

## License

MIT

---

## Summary

Phase 1 (MVP) is **COMPLETE**!

The system can:
✓ Parse strategy markdown
✓ Generate variations with Claude
✓ Convert strategies to Python code
✓ Backtest on historical data
✓ Generate comprehensive reports
✓ Run via CLI or programmatically

Ready for testing and iteration!
