# Trading Tester - Architecture

## System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                              │
│                  (Markdown Strategy File)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   STRATEGY PARSER                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • Reads markdown file                                   │  │
│  │  • Extracts structured sections                          │  │
│  │  • Validates required fields                             │  │
│  │  • Creates ParsedStrategy object                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ├────────────┐
                         │            │
                         ▼            ▼
        ┌───────────────────────────────────────┐
        │   LLM VARIATION GENERATOR (Optional)  │
        │  ┌─────────────────────────────────┐  │
        │  │  • Sends strategy to Claude     │  │
        │  │  • Requests N variations        │  │
        │  │  • Gets modified strategies     │  │
        │  │  • Saves to generated/          │  │
        │  └─────────────────────────────────┘  │
        └───────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CODE GENERATOR                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • Sends strategy to Claude                              │  │
│  │  • Claude generates Python code                          │  │
│  │  • Validates generated code                              │  │
│  │  • Extracts Strategy class                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  GENERATED STRATEGY CLASS                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  class MyStrategy(Strategy):                             │  │
│  │      def calculate_indicators(self, data): ...           │  │
│  │      def generate_signals(self, data): ...               │  │
│  │      def calculate_position_size(...): ...               │  │
│  │      def check_exit_conditions(...): ...                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DATA FETCHER                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • Fetches from yfinance                                 │  │
│  │  • Caches locally                                        │  │
│  │  • Returns OHLCV DataFrame                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  BACKTEST ENGINE                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FOR EACH DAY:                                           │  │
│  │    1. Calculate indicators                               │  │
│  │    2. Generate signals                                   │  │
│  │    3. Check exit conditions for open positions          │  │
│  │    4. Execute exits if needed                            │  │
│  │    5. Check entry signals                                │  │
│  │    6. Calculate position size                            │  │
│  │    7. Execute entries if cash available                  │  │
│  │    8. Update portfolio value                             │  │
│  │    9. Record equity curve                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKTEST RESULT                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • Performance metrics (return, Sharpe, drawdown)        │  │
│  │  • Trade statistics (win rate, avg win/loss)             │  │
│  │  • Complete trade log                                    │  │
│  │  • Equity curve                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        OUTPUT                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • Terminal display (Rich tables)                        │  │
│  │  • JSON file (reports/)                                  │  │
│  │  • Trade log                                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Module Dependencies

```
CLI (main.py)
    ├── StrategyParser (parser.py)
    ├── ClaudeClient (client.py)
    │   └── PromptTemplates (prompts.py)
    ├── CodeGenerator (generator.py)
    │   ├── ClaudeClient
    │   └── Strategy (base_strategy.py)
    ├── DataFetcher (fetcher.py)
    └── BacktestEngine (engine.py)
        ├── Strategy (base_strategy.py)
        └── BacktestResult
```

## Data Flow

### Strategy Testing Flow
```
strategy.md
    → StrategyParser
    → ParsedStrategy
    → CodeGenerator (uses Claude)
    → Python code
    → exec()
    → Strategy instance
    → DataFetcher
    → Historical data
    → BacktestEngine
    → BacktestResult
    → JSON output
```

### Variation Generation Flow
```
strategy.md
    → StrategyParser
    → ParsedStrategy
    → ClaudeClient.generate_variations()
    → List of variation markdown strings
    → Save to generated/*.md
```

### Batch Testing Flow
```
strategies/*.md (multiple files)
    → For each strategy:
        → For each symbol:
            → Test (above flow)
            → Collect results
    → Aggregate results
    → Generate summary
```

## Component Details

### 1. Strategy Parser
**Input**: Markdown file
**Output**: `ParsedStrategy` object
**Key Operations**:
- Regex parsing of H1 and H2 headers
- Section extraction
- Validation of required sections

### 2. LLM Client
**Input**: Strategy content + prompt template
**Output**: Generated text
**Key Operations**:
- Anthropic API calls
- Prompt formatting
- Response parsing
- Code extraction from markdown blocks

### 3. Code Generator
**Input**: `ParsedStrategy`
**Output**: Python class code (string)
**Key Operations**:
- Construct prompt with strategy details
- Call LLM to generate code
- Validate code (optional)
- Ensure imports are present
- Extract class name

### 4. Data Fetcher
**Input**: Symbol, date range
**Output**: pandas DataFrame
**Key Operations**:
- Check cache
- Fetch from yfinance if needed
- Standardize column names
- Save to cache

### 5. Backtest Engine
**Input**: Strategy instance, data, symbol
**Output**: `BacktestResult`
**Key Operations**:
- Initialize state (cash, positions)
- Iterate through data
- Execute strategy logic
- Track trades
- Calculate metrics

## State Management

### During Backtesting

```
BacktestEngine maintains:
├── cash: float                    # Available cash
├── position_size: int             # Current shares held
├── position_entry_price: float    # Entry price of position
├── position_entry_date: datetime  # When position opened
├── position_type: str             # "LONG" or "SHORT"
├── trades: list[dict]             # Completed trades
└── equity_curve: list[float]      # Portfolio value over time

Strategy maintains:
└── positions: dict[symbol, dict]  # Open positions by symbol
```

## Configuration

### Environment Variables (.env)
```
ANTHROPIC_API_KEY=sk-ant-...       # Required
ANTHROPIC_MODEL=claude-sonnet-...  # Optional (has default)
DATA_CACHE_DIR=./data_cache        # Optional (has default)
DEFAULT_INITIAL_CAPITAL=100000     # Optional (has default)
DEFAULT_COMMISSION=0.001           # Optional (has default)
LOG_LEVEL=INFO                     # Optional
```

### Project Configuration (pyproject.toml)
- Dependencies and versions
- CLI entry point
- Build configuration
- Tool settings (black, ruff, mypy)

## Extension Points

### Add New Data Sources
Implement in `backend/data/`:
```python
class AlpacaFetcher(DataFetcher):
    def fetch(self, symbol, start, end):
        # Custom implementation
        pass
```

### Add New Indicators
Extend in generated strategy code:
```python
def calculate_indicators(self, data):
    # Standard indicators
    data = super().calculate_indicators(data)

    # Custom indicator
    data['custom'] = ...
    return data
```

### Add New Metrics
Extend `BacktestResult`:
```python
@dataclass
class BacktestResult:
    # Existing fields
    ...

    # New metrics
    sortino_ratio: float
    calmar_ratio: float
```

### Add New Output Formats
Implement in `backend/cli/`:
```python
def export_html(result: BacktestResult, output_path: str):
    # Generate HTML report
    pass
```

## Performance Considerations

### Caching
- Historical data cached locally
- Cache key: `{symbol}_{start}_{end}_{interval}.csv`
- Saves API calls and time

### Vectorization
- Use pandas operations where possible
- Avoid row-by-row iteration
- Numpy for numerical calculations

### LLM Costs
- Strategy variation: ~$0.05-0.20 per request
- Code generation: ~$0.01-0.10 per strategy
- Use prompt caching for repeated patterns

### Memory
- Large date ranges use more memory
- Equity curve stored as pandas Series
- Consider chunking for very long backtests

## Error Handling

### Strategy Parsing
- Missing sections → ValueError with clear message
- Invalid markdown → Parse error with line number

### Code Generation
- LLM errors → Retry or manual intervention
- Invalid code → Validation catches and corrects
- exec() errors → Caught and reported

### Data Fetching
- Symbol not found → ValueError with symbol name
- Network errors → Retry logic (built into yfinance)
- Invalid dates → ValueError

### Backtesting
- Empty data → ValueError before starting
- Division by zero → Handled in metric calculations
- NaN values → Propagate carefully, check in signals

## Security Considerations

### Code Execution
- Generated code is exec()'d → Review before production use
- Runs in isolated namespace
- No file system access in generated strategies
- Consider sandboxing for untrusted strategies

### API Keys
- Stored in .env (git-ignored)
- Never commit to version control
- Use environment variables in production

### Data Validation
- Pydantic validates all data models
- Type hints throughout
- Input sanitization in CLI

## Testing Strategy

### Unit Tests (Future)
```python
# test_parser.py
def test_parse_valid_strategy():
    parser = StrategyParser()
    strategy = parser.parse(valid_markdown)
    assert strategy.name == "Test Strategy"

# test_backtester.py
def test_backtest_long_trade():
    engine = BacktestEngine()
    result = engine.run(mock_strategy, mock_data, "TEST")
    assert result.num_trades > 0
```

### Integration Tests (Future)
```python
def test_end_to_end():
    # Parse → Generate → Backtest
    parser = StrategyParser()
    strategy = parser.parse_file("test_strategy.md")

    generator = CodeGenerator()
    class_name, code = generator.generate(strategy)

    # ... execute and backtest
    assert result.total_return_pct > -100
```

## Monitoring & Logging

### Current
- Rich console output
- Error messages to stderr
- Basic progress indicators

### Future
- Structured logging (loguru)
- Performance metrics
- LLM token usage tracking
- Backtest duration tracking

---

This architecture is designed to be:
- **Modular**: Each component has clear responsibilities
- **Extensible**: Easy to add new features
- **Testable**: Clear interfaces for mocking
- **Maintainable**: Well-documented and typed
