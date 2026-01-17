"""RSI Mean Reversion Strategy - Generated from strategies/rsi_mean_reversion.md"""

import pandas as pd
import numpy as np

from backend.code_generator.base_strategy import Strategy


class RSIMeanReversionStrategy(Strategy):
    """
    A classic mean reversion strategy based on the Relative Strength Index (RSI).
    Identifies oversold and overbought conditions to capture short-term price reversals.
    """

    def __init__(self, name: str = "RSI Mean Reversion Strategy"):
        super().__init__(name)
        # RSI parameters
        self.rsi_period = 14
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        self.rsi_exit_long = 60
        self.rsi_exit_short = 40
        self.rsi_deep_oversold = 20
        self.rsi_deep_overbought = 80

        # Trend filter
        self.sma_period = 200

        # Volume filter
        self.volume_ma_period = 20
        self.volume_multiplier = 1.2

        # Position sizing
        self.allocation = 0.10
        self.min_position_value = 1000
        self.max_position_value = 10000

        # Exit rules
        self.stop_loss_pct = 0.03
        self.max_holding_days = 10

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI, SMA, and volume indicators."""
        df = data.copy()

        # RSI calculation using Wilder's smoothing
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)

        alpha = 1.0 / self.rsi_period
        avg_gain = gain.ewm(alpha=alpha, min_periods=self.rsi_period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=alpha, min_periods=self.rsi_period, adjust=False).mean()

        rs = avg_gain / avg_loss.replace(0, np.nan)
        df['rsi'] = 100 - (100 / (1 + rs))
        df['rsi'] = df['rsi'].fillna(50)

        # 200-day SMA for trend filter
        df['sma_200'] = df['close'].rolling(window=self.sma_period).mean()

        # Volume moving average
        df['volume_ma'] = df['volume'].rolling(window=self.volume_ma_period).mean()
        df['high_volume'] = df['volume'] >= (self.volume_multiplier * df['volume_ma'])

        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals based on RSI mean reversion rules."""
        df = data.copy()

        # Ensure indicators are calculated
        if 'rsi' not in df.columns:
            df = self.calculate_indicators(df)

        df['signal'] = 0

        # LONG entry: RSI < 30, price > SMA200, high volume
        long_condition = (
            (df['rsi'] < self.rsi_oversold) &
            (df['close'] > df['sma_200']) &
            (df['high_volume']) &
            (df['sma_200'].notna())
        )

        # SHORT entry: RSI > 70, price < SMA200, high volume
        short_condition = (
            (df['rsi'] > self.rsi_overbought) &
            (df['close'] < df['sma_200']) &
            (df['high_volume']) &
            (df['sma_200'].notna())
        )

        df.loc[long_condition, 'signal'] = 1
        df.loc[short_condition, 'signal'] = -1

        return df

    def calculate_position_size(
        self,
        symbol: str,
        price: float,
        portfolio_value: float,
        data: pd.DataFrame
    ) -> int:
        """Calculate position size: 10% of portfolio, capped at $10k."""
        if price <= 0 or portfolio_value <= 0:
            return 0

        # 10% allocation
        position_value = portfolio_value * self.allocation

        # Apply min/max constraints
        position_value = max(self.min_position_value, min(position_value, self.max_position_value))

        # Check if we meet minimum
        if position_value < self.min_position_value:
            return 0

        # Calculate shares (round down)
        shares = int(position_value / price)

        return shares

    def check_exit_conditions(
        self,
        symbol: str,
        current_price: float,
        entry_price: float,
        days_held: int,
        data: pd.DataFrame,
        position_type: str = "LONG"
    ) -> bool:
        """Check RSI-based and stop-loss exit conditions."""
        if entry_price <= 0 or current_price <= 0:
            return True

        # Time-based exit: 10 days max
        if days_held >= self.max_holding_days:
            return True

        # Get current RSI
        if 'rsi' not in data.columns or data.empty:
            return False

        current_rsi = data['rsi'].iloc[-1]
        if pd.isna(current_rsi):
            return False

        if position_type == "LONG":
            # Profit target: RSI > 60
            if current_rsi > self.rsi_exit_long:
                return True
            # Cut loss: RSI < 20 (deeper oversold)
            if current_rsi < self.rsi_deep_oversold:
                return True
            # Stop loss: price down 3%
            if current_price <= entry_price * (1 - self.stop_loss_pct):
                return True

        elif position_type == "SHORT":
            # Profit target: RSI < 40
            if current_rsi < self.rsi_exit_short:
                return True
            # Cut loss: RSI > 80 (deeper overbought)
            if current_rsi > self.rsi_deep_overbought:
                return True
            # Stop loss: price up 3%
            if current_price >= entry_price * (1 + self.stop_loss_pct):
                return True

        return False
