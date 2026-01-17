# Trading Tester

An LLM-powered trading strategy testing framework that generates strategy variations and backtests them against historical market data.

## Features

- **Strategy Definition**: Write trading strategies in structured markdown format
- **LLM-Powered Variations**: Use Anthropic Claude to generate strategy variations (chaos testing approach)
- **Automated Code Generation**: Convert strategies from markdown to executable Python code
- **Backtesting**: Test strategies against historical stock and forex data
- **Comprehensive Reports**: Generate detailed performance reports in JSON format

## Architecture

### Backend (Python)
- `backend/strategy_parser/` - Parse and validate markdown strategies
- `backend/llm/` - Claude API integration for variations and code generation
- `backend/code_generator/` - Convert strategies to executable code
- `backend/backtester/` - Backtesting engine with performance metrics
- `backend/data/` - Historical market data management (yfinance)
- `backend/cli/` - Command-line interface

### Data Directories
- `strategies/` - User-defined strategies in markdown
- `generated/` - LLM-generated strategy variations
- `reports/` - Backtest results and performance reports

## Installation

### Quick Setup (Windows)
```bash
# Run the automated setup script
setup.bat
```

### Manual Setup

**Windows:**
```bash
python3.14.exe -m venv venv
venv\Scripts\activate
pip install -e .
copy .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

**Unix/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

For detailed instructions, see [INSTALL.md](INSTALL.md)

## Usage

### Test a single strategy
```bash
tradingtester test strategies/my_strategy.md --symbol AAPL --start 2020-01-01 --end 2023-12-31
```

### Generate strategy variations
```bash
tradingtester generate strategies/my_strategy.md --variations 5
```

### Batch test multiple strategies
```bash
tradingtester batch strategies/ --symbols AAPL,MSFT,GOOGL
```

## Strategy Format

Strategies are written in markdown with structured sections:

```markdown
# Strategy Name
Brief description of the strategy

## Entry Rules
Natural language description of when to enter trades

## Exit Rules
Natural language description of when to exit trades

## Position Sizing
How much capital to allocate per trade

## Risk Management
Stop loss, take profit, and other risk parameters
```

## Development Roadmap

### Phase 1 (MVP) - Current
- [x] Project setup
- [ ] Strategy parser
- [ ] Claude API integration
- [ ] Basic backtesting engine
- [ ] CLI interface

### Phase 2 (Enhancement)
- TypeScript/React frontend
- Parallel strategy execution
- Additional data sources
- HTML reports with charts

### Phase 3 (Advanced)
- Portfolio-level backtesting
- Walk-forward optimization
- Monte Carlo simulation
- Real-time paper trading

## License

MIT
