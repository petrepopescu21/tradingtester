"""Prompt templates for LLM interactions."""


class PromptTemplates:
    """Collection of prompt templates for different LLM tasks."""

    @staticmethod
    def generate_variations(strategy_content: str, num_variations: int) -> str:
        """
        Generate prompt for creating strategy variations.

        Args:
            strategy_content: Original strategy markdown
            num_variations: Number of variations to generate

        Returns:
            Formatted prompt
        """
        return f"""You are an expert quantitative trading strategist. Your task is to generate {num_variations} variations of the following trading strategy.

Each variation should:
1. Maintain the same general structure (Entry Rules, Exit Rules, Position Sizing, Risk Management)
2. Modify key parameters, indicators, or conditions to create meaningfully different strategies
3. Be realistic and potentially profitable (not random nonsense)
4. Explore different approaches: more aggressive, more conservative, different indicators, different timeframes, etc.

Guidelines for variations:
- Change indicator parameters (e.g., RSI 14 → RSI 21, or use different indicators)
- Modify thresholds and percentages
- Adjust position sizing methods
- Alter risk management rules
- Change timeframes or holding periods
- Combine different technical analysis approaches

Original Strategy:
```markdown
{strategy_content}
```

Please generate {num_variations} distinct variations. For each variation:
1. Give it a descriptive name that reflects how it differs from the original
2. Maintain the same markdown structure
3. Explain in the description how this variation differs from the original

Output each strategy as a complete markdown document, separated by:
---STRATEGY_SEPARATOR---

Make each variation substantively different, not just minor parameter tweaks."""

    @staticmethod
    def strategy_to_code(strategy_content: str) -> str:
        """
        Generate prompt for converting strategy to Python code.

        Args:
            strategy_content: Strategy markdown content

        Returns:
            Formatted prompt
        """
        return f"""You are an expert Python developer specializing in algorithmic trading systems. Your task is to convert the following trading strategy from markdown into executable Python code.

Strategy:
```markdown
{strategy_content}
```

Generate a Python class that implements this strategy. The class must:

1. Import and inherit from the base Strategy class:
```python
from backend.code_generator.base_strategy import Strategy
```

2. Implement these abstract methods with EXACT signatures:
```python
def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
    '''Calculate technical indicators. Return DataFrame with indicator columns added.'''

def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
    '''Generate signals. Add 'signal' column: 1=buy, -1=sell, 0=hold.'''

def calculate_position_size(self, symbol: str, price: float, portfolio_value: float, data: pd.DataFrame) -> int:
    '''Return number of shares to trade.'''

def check_exit_conditions(self, symbol: str, current_price: float, entry_price: float,
                         days_held: int, data: pd.DataFrame, position_type: str = "LONG") -> bool:
    '''Return True if position should be exited. position_type is "LONG" or "SHORT".'''
```

Requirements:
1. Implement all methods according to the strategy rules
2. Use pandas for data manipulation
3. Use numpy for calculations
4. Add type hints
5. Include docstrings
6. Handle edge cases (missing data, division by zero, etc.)
7. Use clear variable names that reflect the strategy logic
8. Add comments explaining key decisions

For technical indicators, use this pattern:
```python
# RSI
delta = data['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
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

Output ONLY the Python code for the strategy class. Do not include example usage or test code."""

    @staticmethod
    def validate_code(code: str, strategy_name: str) -> str:
        """
        Generate prompt for validating generated code.

        Args:
            code: Generated Python code
            strategy_name: Name of the strategy

        Returns:
            Formatted prompt
        """
        return f"""Review this generated trading strategy code for the strategy "{strategy_name}".

```python
{code}
```

Check for:
1. Syntax errors
2. Logic errors
3. Missing imports
4. Incorrect implementation of technical indicators
5. Edge cases not handled
6. Type hint issues

If there are issues, provide corrected code. If the code is correct, respond with "VALIDATED".

Output format:
If issues found:
```python
[corrected code]
```

If no issues:
VALIDATED"""
