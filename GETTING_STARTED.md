# Getting Started with Trading Tester

## What is Trading Tester?

Trading Tester is an LLM-powered framework that:
1. Takes trading strategies written in markdown
2. Uses Claude AI to generate variations (chaos testing approach)
3. Converts strategies to executable Python code
4. Backtests them against historical market data
5. Generates comprehensive performance reports

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Trading Tester                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Strategy Parser (Markdown → Structured Data)           │
│     ↓                                                       │
│  2. LLM Variation Generator (Claude API)                    │
│     ↓                                                       │
│  3. Code Generator (Markdown → Python Code)                 │
│     ↓                                                       │
│  4. Backtest Engine (Execute on Historical Data)            │
│     ↓                                                       │
│  5. Report Generator (JSON Results)                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
tradingtester/
├── backend/                    # Python backend
│   ├── strategy_parser/        # Parse markdown strategies
│   │   └── parser.py          # StrategyParser class
│   ├── llm/                   # Claude API integration
│   │   ├── client.py          # ClaudeClient class
│   │   └── prompts.py         # Prompt templates
│   ├── code_generator/        # Strategy → Python code
│   │   ├── base_strategy.py   # Base Strategy class
│   │   └── generator.py       # CodeGenerator class
│   ├── backtester/            # Backtesting engine
│   │   └── engine.py          # BacktestEngine & Result classes
│   ├── data/                  # Market data fetching
│   │   └── fetcher.py         # DataFetcher class
│   └── cli/                   # Command-line interface
│       └── main.py            # CLI commands
├── strategies/                # User strategy markdown files
│   ├── rsi_mean_reversion.md
│   └── momentum_breakout.md
├── generated/                 # LLM-generated variations
├── reports/                   # Backtest results (JSON)
├── pyproject.toml            # Project configuration
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
└── README.md                # Documentation
```

## Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

Quick version:

**Windows:**
```bash
# 1. Create virtual environment
python3.14.exe -m venv venv
venv\Scripts\activate

# 2. Install dependencies
pip install -e .

# 3. Set up API key
copy .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

**Unix/Mac:**
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -e .

# 3. Set up API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Strategy Format

Strategies use a hybrid markdown format with structured sections:

```markdown
# Strategy Name
Brief description

## Entry Rules
Natural language description of entry conditions
- Can use bullet points
- Reference indicators (RSI, MA, etc.)
- Define thresholds

## Exit Rules
Natural language description of exit conditions
- Profit targets
- Stop losses
- Time-based exits

## Position Sizing
How to calculate position sizes
- Fixed fractional
- Volatility-based
- Risk-based

## Risk Management
Risk controls and limits
- Max risk per trade
- Portfolio limits
- Drawdown limits
```

## Usage Examples

### 1. Test a Single Strategy

```bash
tradingtester test strategies/rsi_mean_reversion.md \
  --symbol AAPL \
  --start 2020-01-01 \
  --end 2023-12-31 \
  --output reports/rsi_aapl.json
```

This will:
- Parse the strategy markdown
- Generate Python code using Claude
- Fetch AAPL historical data
- Run backtest
- Display results and save to JSON

### 2. Generate Strategy Variations

```bash
tradingtester generate strategies/rsi_mean_reversion.md \
  --variations 5 \
  --output-dir generated
```

This creates 5 variations:
- Modified parameters (e.g., RSI 14 → RSI 21)
- Different indicators
- Adjusted risk levels
- Alternative timeframes

### 3. Batch Test Multiple Strategies

```bash
tradingtester batch strategies/ \
  --symbols AAPL,MSFT,GOOGL,SPY \
  --start 2020-01-01 \
  --end 2023-12-31 \
  --output-dir reports
```

This tests all strategies in `strategies/` directory on all symbols and generates a summary report.

## How It Works

### Step 1: Parse Strategy

The `StrategyParser` reads markdown and extracts:
- Strategy name and description
- Entry rules
- Exit rules
- Position sizing rules
- Risk management rules

### Step 2: Generate Variations (Optional)

Claude generates variations by:
- Modifying indicator parameters
- Changing thresholds
- Adjusting timeframes
- Exploring different approaches

### Step 3: Convert to Code

Claude converts natural language strategy rules into executable Python:
- Implements `calculate_indicators()` - Technical indicators
- Implements `generate_signals()` - Buy/sell signals
- Implements `calculate_position_size()` - Position sizing
- Implements `check_exit_conditions()` - Exit logic

### Step 4: Backtest

The `BacktestEngine`:
- Fetches historical data (yfinance)
- Simulates trading day-by-day
- Tracks positions, cash, equity
- Calculates commissions
- Records all trades

### Step 5: Generate Report

Results include:
- Total return and % return
- Number of trades
- Win rate
- Average win/loss
- Maximum drawdown
- Sharpe ratio
- Complete trade log
- Equity curve

## Example Output

```
Backtest Results:

Strategy             RSI Mean Reversion Strategy
Symbol               AAPL
Period               2020-01-01 to 2023-12-31
Initial Capital      $100,000.00
Final Capital        $142,350.00
Total Return         $42,350.00 (42.35%)
Number of Trades     127
Winning Trades       78
Losing Trades        49
Win Rate             61.42%
Average Win          $1,234.56
Average Loss         -$567.89
Max Drawdown         -$8,234.00 (-6.54%)
Sharpe Ratio         1.234
```

## Next Steps

### Phase 2 Enhancements (Future)

- **TypeScript Frontend**: React dashboard for visualization
- **Interactive Charts**: View equity curves, drawdowns
- **Parallel Processing**: Test multiple strategies simultaneously
- **More Data Sources**: Alpha Vantage, Alpaca, etc.
- **HTML Reports**: Rich reports with charts

### Phase 3 Advanced Features (Future)

- **Portfolio Backtesting**: Test multiple strategies together
- **Walk-Forward Optimization**: Avoid overfitting
- **Monte Carlo Simulation**: Assess robustness
- **Real-time Paper Trading**: Test live with fake money

## Tips for Writing Good Strategies

1. **Be Specific**: Clear entry/exit conditions
2. **Include Risk Management**: Always define stops and position sizing
3. **Use Multiple Conditions**: Combine indicators for better signals
4. **Consider Context**: Market regime, volatility, trends
5. **Test Variations**: Let Claude explore the parameter space

## Troubleshooting

See [INSTALL.md](INSTALL.md) for common issues.

## Contributing

This is a greenfield project. Future enhancements welcome:
- More sophisticated backtesting metrics
- Additional data sources
- Strategy templates
- Optimization algorithms
- Risk analysis tools

## License

MIT
