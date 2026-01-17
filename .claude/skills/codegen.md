# /codegen - Generate Strategy Code

Generate Python code from a trading strategy markdown file.

## Usage

```
/codegen <strategy_file.md> [output_file.py]
```

If no output file is specified, saves to `generated/<strategy_name>.py`.

## Instructions

When this skill is invoked:

1. Read the strategy markdown file
2. Read `backend/code_generator/base_strategy.py` to understand the interface
3. Generate a Python class that:
   - Imports from `backend.code_generator.base_strategy import Strategy`
   - Implements all abstract methods with EXACT signatures
   - Follows the strategy rules from the markdown

## Required Method Signatures

```python
from backend.code_generator.base_strategy import Strategy

class <StrategyName>(Strategy):
    def __init__(self, name: str = "<Strategy Name>"):
        super().__init__(name)
        # Initialize strategy parameters

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators. Return DataFrame with indicator columns added."""

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate signals. Add 'signal' column: 1=buy, -1=sell, 0=hold."""

    def calculate_position_size(self, symbol: str, price: float, portfolio_value: float, data: pd.DataFrame) -> int:
        """Return number of shares to trade."""

    def check_exit_conditions(self, symbol: str, current_price: float, entry_price: float,
                             days_held: int, data: pd.DataFrame, position_type: str = "LONG") -> bool:
        """Return True if position should be exited. position_type is "LONG" or "SHORT"."""
```

## Technical Indicator Patterns

```python
# RSI
delta = data['close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
alpha = 1.0 / period
avg_gain = gain.ewm(alpha=alpha, min_periods=period, adjust=False).mean()
avg_loss = loss.ewm(alpha=alpha, min_periods=period, adjust=False).mean()
rs = avg_gain / avg_loss.replace(0, np.nan)
data['rsi'] = 100 - (100 / (1 + rs))

# SMA
data['sma_50'] = data['close'].rolling(window=50).mean()

# EMA
data['ema_20'] = data['close'].ewm(span=20, adjust=False).mean()

# ATR
high_low = data['high'] - data['low']
high_close = (data['high'] - data['close'].shift()).abs()
low_close = (data['low'] - data['close'].shift()).abs()
ranges = pd.concat([high_low, high_close, low_close], axis=1)
true_range = ranges.max(axis=1)
data['atr'] = true_range.rolling(14).mean()
```

## Output

Write the generated code to the output file. Include:
- Import statements (pandas, numpy, Strategy base class)
- Strategy class with all methods implemented
- Type hints and docstrings
- Proper handling of edge cases (NaN, division by zero)
