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
        # For leveraged strategies:
        self.leverage = 1.0  # Default leverage (set 3.0-5.0 for crypto derivatives)
        self.asset_class = "equity"  # or "crypto", "futures"

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators. Return DataFrame with indicator columns added."""

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate signals. Add 'signal' column: 1=buy, -1=sell, 0=hold."""

    def calculate_position_size(self, symbol: str, price: float, portfolio_value: float, data: pd.DataFrame) -> int:
        """Return number of shares/contracts to trade."""

    def check_exit_conditions(self, symbol: str, current_price: float, entry_price: float,
                             days_held: int, data: pd.DataFrame, position_type: str = "LONG") -> bool:
        """Return True if position should be exited. position_type is "LONG" or "SHORT"."""

    # Optional: Override for dynamic leverage based on volatility
    def get_leverage(self, data: pd.DataFrame) -> float:
        """Return leverage multiplier (1.0 = no leverage). Override for dynamic leverage."""
        return self.leverage
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

# VWAP (Volume Weighted Average Price)
typical_price = (data['high'] + data['low'] + data['close']) / 3
data['vwap'] = (typical_price * data['volume']).cumsum() / data['volume'].cumsum()
# For session-based VWAP, reset cumsum at session boundaries

# Bollinger Bands
period = 20
std_dev = 2
data['bb_middle'] = data['close'].rolling(window=period).mean()
rolling_std = data['close'].rolling(window=period).std()
data['bb_upper'] = data['bb_middle'] + (rolling_std * std_dev)
data['bb_lower'] = data['bb_middle'] - (rolling_std * std_dev)
data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / data['bb_middle']

# MACD
fast_ema = data['close'].ewm(span=12, adjust=False).mean()
slow_ema = data['close'].ewm(span=26, adjust=False).mean()
data['macd_line'] = fast_ema - slow_ema
data['macd_signal'] = data['macd_line'].ewm(span=9, adjust=False).mean()
data['macd_histogram'] = data['macd_line'] - data['macd_signal']
data['macd_hist_rising'] = data['macd_histogram'] > data['macd_histogram'].shift(1)

# Swing High/Low Detection
lookback = 5
data['swing_high'] = data['high'].rolling(window=lookback*2+1, center=True).apply(
    lambda x: x.iloc[lookback] if x.iloc[lookback] == x.max() else np.nan, raw=False
)
data['swing_low'] = data['low'].rolling(window=lookback*2+1, center=True).apply(
    lambda x: x.iloc[lookback] if x.iloc[lookback] == x.min() else np.nan, raw=False
)
data['recent_swing_high'] = data['swing_high'].ffill()
data['recent_swing_low'] = data['swing_low'].ffill()

# Wick Detection (for liquidity grabs)
data['lower_wick'] = data[['open', 'close']].min(axis=1) - data['low']
data['upper_wick'] = data['high'] - data[['open', 'close']].max(axis=1)
data['body'] = (data['close'] - data['open']).abs()
data['wick_ratio_lower'] = data['lower_wick'] / data['body'].replace(0, np.nan)
data['wick_ratio_upper'] = data['upper_wick'] / data['body'].replace(0, np.nan)

# Volume Profile POC (simplified - uses rolling window)
def calc_poc(df, lookback=50):
    """Calculate Point of Control as price level with highest volume."""
    poc = []
    for i in range(len(df)):
        if i < lookback:
            poc.append(np.nan)
        else:
            window = df.iloc[i-lookback:i]
            # Create price bins
            price_range = window['high'].max() - window['low'].min()
            if price_range > 0:
                bins = np.linspace(window['low'].min(), window['high'].max(), 20)
                # Assign volume to bins based on typical price
                typical = (window['high'] + window['low'] + window['close']) / 3
                bin_idx = np.digitize(typical, bins) - 1
                bin_vol = np.bincount(bin_idx.clip(0, len(bins)-2), weights=window['volume'], minlength=len(bins)-1)
                poc_price = (bins[bin_vol.argmax()] + bins[bin_vol.argmax()+1]) / 2
                poc.append(poc_price)
            else:
                poc.append(window['close'].iloc[-1])
    return poc
data['poc'] = calc_poc(data)
```

## Crypto/Derivatives Specific Patterns

```python
# Dynamic Leverage based on volatility (ATR)
def get_leverage(self, data: pd.DataFrame) -> float:
    if data.empty or 'atr' not in data.columns:
        return self.base_leverage
    atr_pct = data['atr'].iloc[-1] / data['close'].iloc[-1]
    # Lower leverage when volatility is high
    if atr_pct > 0.05:  # High volatility
        return max(1.0, self.base_leverage - 2)
    elif atr_pct > 0.03:  # Medium volatility
        return max(1.0, self.base_leverage - 1)
    return self.base_leverage

# Trading Session Filter (UTC hours)
# London: 07:00-16:00, New York: 13:00-22:00
def is_in_trading_session(self, timestamp):
    hour = timestamp.hour
    london = 7 <= hour < 16
    new_york = 13 <= hour < 22
    return london or new_york

# Ratchet Trailing Stop
def update_ratchet_stop(self, symbol, current_price, entry_price, position_type="LONG"):
    if symbol not in self.trailing_stops:
        return None
    stop_info = self.trailing_stops[symbol]
    profit_pct = (current_price - entry_price) / entry_price if position_type == "LONG" else (entry_price - current_price) / entry_price

    # Activation: move to breakeven after 2% profit
    if profit_pct >= 0.02 and not stop_info['activated']:
        stop_info['activated'] = True
        stop_info['stop_price'] = entry_price  # Breakeven

    # Trail at 1% behind peak after activation
    if stop_info['activated']:
        peak = stop_info.get('highest_price', entry_price)
        if position_type == "LONG":
            if current_price > peak:
                stop_info['highest_price'] = current_price
            stop_info['stop_price'] = stop_info['highest_price'] * 0.99
        else:
            if current_price < stop_info.get('lowest_price', entry_price):
                stop_info['lowest_price'] = current_price
            stop_info['stop_price'] = stop_info['lowest_price'] * 1.01

    return stop_info['stop_price']
```

## Output

Write the generated code to the output file. Include:
- Import statements (pandas, numpy, Strategy base class)
- Strategy class with all methods implemented
- Type hints and docstrings
- Proper handling of edge cases (NaN, division by zero)
