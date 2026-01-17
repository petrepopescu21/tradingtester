"""Momentum Breakout Strategy.

A trend-following strategy that captures strong momentum moves when price breaks
out of consolidation patterns with increasing volume.
"""

import numpy as np
import pandas as pd

from backend.code_generator.base_strategy import Strategy


class MomentumBreakoutStrategy(Strategy):
    """Momentum breakout trading strategy."""

    def __init__(self, name: str = "Momentum Breakout"):
        super().__init__(name)
        self.breakout_period = 20
        self.adx_period = 14
        self.adx_threshold = 25
        self.sma_50_period = 50
        self.sma_200_period = 200
        self.volume_avg_period = 50
        self.volume_multiplier = 2.0
        self.breakout_pct = 0.02
        self.ema_exit_period = 10
        self.atr_period = 14
        self.profit_target_pct = 0.15
        self.initial_stop_pct = 0.05
        self.max_hold_days = 30
        self.chase_lookback = 5
        self.chase_threshold = 0.10
        self.risk_amount = 1000
        self.min_position_value = 2000
        self.max_position_value = 15000
        self.highest_price_since_entry: dict[str, float] = {}

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate breakout, trend, and volatility indicators."""
        data = data.copy()

        # 20-day high
        data['high_20'] = data['high'].rolling(window=self.breakout_period).max()

        # 50-day and 200-day SMAs
        data['sma_50'] = data['close'].rolling(window=self.sma_50_period).mean()
        data['sma_200'] = data['close'].rolling(window=self.sma_200_period).mean()

        # Volume average
        data['volume_avg'] = data['volume'].rolling(window=self.volume_avg_period).mean()
        data['volume_ratio'] = data['volume'] / data['volume_avg'].replace(0, np.nan)

        # ATR calculation
        high_low = data['high'] - data['low']
        high_close = (data['high'] - data['close'].shift()).abs()
        low_close = (data['low'] - data['close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        data['atr'] = true_range.rolling(window=self.atr_period).mean()

        # ADX calculation
        data['adx'] = self._calculate_adx(data)

        # 10-day EMA for exit
        data['ema_10'] = data['close'].ewm(span=self.ema_exit_period, adjust=False).mean()

        # 5-day price change for chase detection
        data['price_change_5d'] = data['close'].pct_change(periods=self.chase_lookback)

        return data

    def _calculate_adx(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Average Directional Index (ADX)."""
        high = data['high']
        low = data['low']
        close = data['close']

        # +DM and -DM
        plus_dm = high.diff()
        minus_dm = -low.diff()

        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

        # True Range
        high_low = high - low
        high_close = (high - close.shift()).abs()
        low_close = (low - close.shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

        # Smoothed values
        alpha = 1.0 / self.adx_period
        atr = tr.ewm(alpha=alpha, min_periods=self.adx_period, adjust=False).mean()
        plus_di = 100 * (plus_dm.ewm(alpha=alpha, min_periods=self.adx_period, adjust=False).mean() / atr.replace(0, np.nan))
        minus_di = 100 * (minus_dm.ewm(alpha=alpha, min_periods=self.adx_period, adjust=False).mean() / atr.replace(0, np.nan))

        # DX and ADX
        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
        adx = dx.ewm(alpha=alpha, min_periods=self.adx_period, adjust=False).mean()

        return adx

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy signals based on breakout conditions."""
        data = data.copy()
        data['signal'] = 0

        # Previous day's 20-day high (to detect breakout)
        prev_high_20 = data['high_20'].shift(1)

        # Long entry conditions
        breakout = data['close'] > prev_high_20 * (1 + self.breakout_pct)
        strong_trend = data['adx'] > self.adx_threshold
        above_mas = (data['close'] > data['sma_50']) & (data['close'] > data['sma_200'])
        high_volume = data['volume_ratio'] >= self.volume_multiplier
        not_chasing = data['price_change_5d'].abs() <= self.chase_threshold

        long_condition = breakout & strong_trend & above_mas & high_volume & not_chasing

        data.loc[long_condition, 'signal'] = 1

        return data

    def calculate_position_size(
        self,
        symbol: str,
        price: float,
        portfolio_value: float,
        data: pd.DataFrame
    ) -> int:
        """Calculate position size using ATR-based volatility adjustment."""
        if price <= 0 or data.empty:
            return 0

        atr = data['atr'].iloc[-1]
        if pd.isna(atr) or atr <= 0:
            # Fallback to minimum position
            return int(self.min_position_value / price)

        # Position size = Risk Amount / (2 * ATR)
        shares = int(self.risk_amount / (2 * atr))
        position_value = shares * price

        # Apply min/max constraints
        if position_value < self.min_position_value:
            shares = int(self.min_position_value / price)
        elif position_value > self.max_position_value:
            shares = int(self.max_position_value / price)

        return max(shares, 1)

    def check_exit_conditions(
        self,
        symbol: str,
        current_price: float,
        entry_price: float,
        days_held: int,
        data: pd.DataFrame,
        position_type: str = "LONG"
    ) -> bool:
        """Check exit conditions with trailing stop logic."""
        if data.empty or position_type != "LONG":
            return False

        # Update highest price since entry
        if symbol not in self.highest_price_since_entry:
            self.highest_price_since_entry[symbol] = entry_price
        self.highest_price_since_entry[symbol] = max(
            self.highest_price_since_entry[symbol],
            current_price
        )
        highest_price = self.highest_price_since_entry[symbol]

        # Calculate profit percentage
        profit_pct = (current_price - entry_price) / entry_price

        # Profit target: 15% gain
        if profit_pct >= self.profit_target_pct:
            self._cleanup_tracking(symbol)
            return True

        # Time-based exit: more than 30 days
        if days_held > self.max_hold_days:
            self._cleanup_tracking(symbol)
            return True

        # Price below 10-day EMA (trend reversal)
        if 'ema_10' in data.columns:
            ema_10 = data['ema_10'].iloc[-1]
            if not pd.isna(ema_10) and current_price < ema_10:
                self._cleanup_tracking(symbol)
                return True

        # Trailing stop logic
        atr = data['atr'].iloc[-1] if 'atr' in data.columns else None

        if profit_pct < 0.05:
            # Initial stop: 5% below entry
            stop_price = entry_price * (1 - self.initial_stop_pct)
        elif profit_pct < 0.10:
            # After 5% profit: Move stop to breakeven
            stop_price = entry_price
        else:
            # After 10% profit: Trail 2 * ATR below highest price
            if atr is not None and not pd.isna(atr):
                stop_price = highest_price - (2 * atr)
            else:
                stop_price = highest_price * 0.95

        if current_price < stop_price:
            self._cleanup_tracking(symbol)
            return True

        return False

    def _cleanup_tracking(self, symbol: str):
        """Clean up tracking data when exiting a position."""
        if symbol in self.highest_price_since_entry:
            del self.highest_price_since_entry[symbol]
