"""The Banker Ratchet Strategy - Institutional Grade Liquidity Grab.

A crypto derivatives strategy that identifies high-probability liquidity grabs
at institutional volume levels, using mean reversion within trend logic.
"""

import numpy as np
import pandas as pd

from backend.code_generator.base_strategy import Strategy


class BankerRatchetStrategy(Strategy):
    """Institutional grade liquidity grab strategy for crypto perpetual futures."""

    def __init__(self, name: str = "The Banker Ratchet"):
        super().__init__(name)

        # Asset configuration
        self.asset_class = "crypto"
        self.base_leverage = 5.0
        self.leverage = self.base_leverage

        # Indicator settings
        self.ema_period = 200
        self.bb_period = 20
        self.bb_std = 2
        self.rsi_period = 14
        self.rsi_oversold = 45
        self.rsi_overbought = 55
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.swing_lookback = 5
        self.poc_lookback = 50

        # Risk management
        self.initial_stop_pct = 0.02  # 2% hard stop
        self.breakeven_activation_pct = 0.02  # Move to BE at 2% profit
        self.trailing_distance_pct = 0.01  # Trail 1% behind peak

        # Trading sessions (UTC hours)
        self.london_start = 7
        self.london_end = 16
        self.ny_start = 13
        self.ny_end = 22

        # Volatility thresholds for band width
        self.min_bb_width = 0.02  # Minimum band width for "high energy"

        # Liquidity grab tolerance (for daily data, use looser detection)
        self.liquidity_grab_tolerance = 0.005  # 0.5% tolerance for wick detection

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all required indicators for the strategy."""
        data = data.copy()

        # 200 EMA - Trend Direction
        data['ema_200'] = data['close'].ewm(span=self.ema_period, adjust=False).mean()

        # VWAP - Value indicator
        typical_price = (data['high'] + data['low'] + data['close']) / 3
        data['vwap'] = (typical_price * data['volume']).cumsum() / data['volume'].cumsum()

        # Bollinger Bands - Volatility/Energy
        data['bb_middle'] = data['close'].rolling(window=self.bb_period).mean()
        rolling_std = data['close'].rolling(window=self.bb_period).std()
        data['bb_upper'] = data['bb_middle'] + (rolling_std * self.bb_std)
        data['bb_lower'] = data['bb_middle'] - (rolling_std * self.bb_std)
        data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / data['bb_middle']

        # RSI - Momentum Trigger
        data['rsi'] = self._calculate_rsi(data['close'])

        # MACD - Confirmation
        fast_ema = data['close'].ewm(span=self.macd_fast, adjust=False).mean()
        slow_ema = data['close'].ewm(span=self.macd_slow, adjust=False).mean()
        data['macd_line'] = fast_ema - slow_ema
        data['macd_signal_line'] = data['macd_line'].ewm(span=self.macd_signal, adjust=False).mean()
        data['macd_histogram'] = data['macd_line'] - data['macd_signal_line']
        data['macd_hist_rising'] = data['macd_histogram'] > data['macd_histogram'].shift(1)
        data['macd_hist_falling'] = data['macd_histogram'] < data['macd_histogram'].shift(1)

        # Swing High/Low Detection
        data = self._calculate_swing_points(data)

        # Volume Profile POC
        data['poc'] = self._calculate_poc(data)

        # Wick Detection for liquidity grabs
        data['lower_wick'] = data[['open', 'close']].min(axis=1) - data['low']
        data['upper_wick'] = data['high'] - data[['open', 'close']].max(axis=1)
        data['body'] = (data['close'] - data['open']).abs()

        # ATR for dynamic leverage
        data['atr'] = self._calculate_atr(data)

        return data

    def _calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """Calculate RSI using Wilder's smoothing."""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)

        alpha = 1.0 / self.rsi_period
        avg_gain = gain.ewm(alpha=alpha, min_periods=self.rsi_period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=alpha, min_periods=self.rsi_period, adjust=False).mean()

        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)

    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        high_low = data['high'] - data['low']
        high_close = (data['high'] - data['close'].shift()).abs()
        low_close = (data['low'] - data['close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(window=period).mean()

    def _calculate_swing_points(self, data: pd.DataFrame) -> pd.DataFrame:
        """Detect swing highs and lows."""
        lookback = self.swing_lookback
        window = lookback * 2 + 1

        # Swing high: highest point in window
        data['swing_high'] = data['high'].rolling(window=window, center=True).apply(
            lambda x: x.iloc[lookback] if len(x) == window and x.iloc[lookback] == x.max() else np.nan,
            raw=False
        )

        # Swing low: lowest point in window
        data['swing_low'] = data['low'].rolling(window=window, center=True).apply(
            lambda x: x.iloc[lookback] if len(x) == window and x.iloc[lookback] == x.min() else np.nan,
            raw=False
        )

        # Forward fill to get recent swing levels
        data['recent_swing_high'] = data['swing_high'].ffill()
        data['recent_swing_low'] = data['swing_low'].ffill()

        return data

    def _calculate_poc(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Point of Control from volume profile."""
        poc = []
        lookback = self.poc_lookback

        for i in range(len(data)):
            if i < lookback:
                poc.append(np.nan)
            else:
                window = data.iloc[i - lookback:i]
                price_range = window['high'].max() - window['low'].min()

                if price_range > 0 and window['volume'].sum() > 0:
                    bins = np.linspace(window['low'].min(), window['high'].max(), 20)
                    typical = (window['high'] + window['low'] + window['close']) / 3
                    bin_idx = np.digitize(typical.values, bins) - 1
                    bin_idx = np.clip(bin_idx, 0, len(bins) - 2)
                    bin_vol = np.bincount(bin_idx, weights=window['volume'].values, minlength=len(bins) - 1)
                    max_bin = bin_vol.argmax()
                    poc_price = (bins[max_bin] + bins[min(max_bin + 1, len(bins) - 1)]) / 2
                    poc.append(poc_price)
                else:
                    poc.append(window['close'].iloc[-1] if len(window) > 0 else np.nan)

        return pd.Series(poc, index=data.index)

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals based on liquidity grab logic."""
        data = data.copy()
        data['signal'] = 0

        # Check if indicators are calculated
        if 'ema_200' not in data.columns:
            data = self.calculate_indicators(data)

        for i in range(1, len(data)):
            row = data.iloc[i]
            prev_row = data.iloc[i - 1]

            # Skip if essential indicators are NaN
            if pd.isna(row['ema_200']) or pd.isna(row['vwap']) or pd.isna(row['rsi']):
                continue

            # Check trading session (if timestamp available)
            # NOTE: Session filter disabled for backtesting - enable for live trading
            # if hasattr(data.index[i], 'hour'):
            #     hour = data.index[i].hour
            #     in_session = (self.london_start <= hour < self.london_end) or \
            #                  (self.ny_start <= hour < self.ny_end)
            #     if not in_session:
            #         continue

            # Check for wide Bollinger Bands (high energy)
            if pd.isna(row['bb_width']) or row['bb_width'] < self.min_bb_width:
                continue

            # LONG SETUP - Bullish Liquidity Grab
            if row['close'] > row['ema_200']:  # Bull market prerequisite
                # The Trap: wick below (or near) recent swing low, then close above
                swing_low = row['recent_swing_low']
                if not pd.isna(swing_low):
                    tolerance = swing_low * self.liquidity_grab_tolerance
                    # Liquidity grab: low touches/breaks swing low, close recovers above
                    liquidity_grab = (row['low'] <= swing_low + tolerance) and (row['close'] > swing_low)
                    # Alternative: strong bounce from near swing low level
                    bounce_from_support = (row['low'] <= swing_low * 1.01) and (row['close'] > row['open'])

                    if liquidity_grab or bounce_from_support:
                        # The Value: price below VWAP
                        if row['close'] < row['vwap']:
                            # The Truth: near POC
                            poc = row['poc']
                            near_poc = pd.isna(poc) or abs(row['close'] - poc) / row['close'] < 0.03

                            # The Trigger
                            rsi_oversold = row['rsi'] < self.rsi_oversold
                            macd_rising = row['macd_hist_rising']

                            if rsi_oversold and macd_rising and near_poc:
                                data.iloc[i, data.columns.get_loc('signal')] = 1

            # SHORT SETUP - Bearish Liquidity Grab
            elif row['close'] < row['ema_200']:  # Bear market prerequisite
                # The Trap: wick above (or near) recent swing high, then close below
                swing_high = row['recent_swing_high']
                if not pd.isna(swing_high):
                    tolerance = swing_high * self.liquidity_grab_tolerance
                    # Liquidity grab: high touches/breaks swing high, close rejects below
                    liquidity_grab = (row['high'] >= swing_high - tolerance) and (row['close'] < swing_high)
                    # Alternative: strong rejection from near swing high level
                    rejection_from_resistance = (row['high'] >= swing_high * 0.99) and (row['close'] < row['open'])

                    if liquidity_grab or rejection_from_resistance:
                        # The Value: price above VWAP
                        if row['close'] > row['vwap']:
                            # The Truth: near POC
                            poc = row['poc']
                            near_poc = pd.isna(poc) or abs(row['close'] - poc) / row['close'] < 0.03

                            # The Trigger
                            rsi_overbought = row['rsi'] > self.rsi_overbought
                            macd_falling = row['macd_hist_falling']

                            if rsi_overbought and macd_falling and near_poc:
                                data.iloc[i, data.columns.get_loc('signal')] = -1

        return data

    def get_leverage(self, data: pd.DataFrame) -> float:
        """Dynamic leverage based on ATR volatility."""
        if data.empty or 'atr' not in data.columns:
            return self.base_leverage

        atr = data['atr'].iloc[-1]
        close = data['close'].iloc[-1]

        if pd.isna(atr) or pd.isna(close) or close == 0:
            return self.base_leverage

        atr_pct = atr / close

        # Lower leverage when volatility is high
        if atr_pct > 0.05:  # Very high volatility
            return 3.0
        elif atr_pct > 0.03:  # High volatility
            return 4.0
        else:  # Normal volatility
            return self.base_leverage

    def calculate_position_size(
        self,
        symbol: str,
        price: float,
        portfolio_value: float,
        data: pd.DataFrame
    ) -> int:
        """Calculate position size with 2% risk per trade."""
        if price <= 0 or portfolio_value <= 0:
            return 0

        # Risk 2% of portfolio per trade
        risk_amount = portfolio_value * 0.02
        leverage = self.get_leverage(data)

        # Position size based on stop loss distance
        stop_distance = price * self.initial_stop_pct
        if stop_distance <= 0:
            return 0

        # Contracts = Risk / Stop Distance
        contracts = int(risk_amount / stop_distance)

        # Apply leverage to get notional position
        max_position_value = portfolio_value * 0.5 * leverage
        max_contracts = int(max_position_value / price)

        return min(contracts, max_contracts, max(1, contracts))

    def check_exit_conditions(
        self,
        symbol: str,
        current_price: float,
        entry_price: float,
        days_held: int,
        data: pd.DataFrame,
        position_type: str = "LONG"
    ) -> bool:
        """Check exit conditions with ratchet trailing stop logic."""
        if entry_price <= 0 or current_price <= 0:
            return True

        # Initialize trailing stop if not exists
        if symbol not in self.trailing_stops:
            self.init_trailing_stop(symbol, entry_price, self.initial_stop_pct, position_type)

        stop_info = self.trailing_stops[symbol]

        # Calculate current profit percentage
        if position_type == "LONG":
            profit_pct = (current_price - entry_price) / entry_price
            # Update highest price
            if current_price > stop_info.get('highest_price', entry_price):
                stop_info['highest_price'] = current_price
        else:  # SHORT
            profit_pct = (entry_price - current_price) / entry_price
            # Update lowest price
            if current_price < stop_info.get('lowest_price', entry_price):
                stop_info['lowest_price'] = current_price

        # Ratchet Logic
        # 1. Activation: Move to breakeven at 2% profit
        if profit_pct >= self.breakeven_activation_pct and not stop_info.get('activated', False):
            stop_info['activated'] = True
            stop_info['stop_price'] = entry_price  # Move to breakeven

        # 2. Trailing: After activation, trail 1% behind peak
        if stop_info.get('activated', False):
            if position_type == "LONG":
                peak = stop_info.get('highest_price', entry_price)
                stop_info['stop_price'] = peak * (1 - self.trailing_distance_pct)
            else:  # SHORT
                trough = stop_info.get('lowest_price', entry_price)
                stop_info['stop_price'] = trough * (1 + self.trailing_distance_pct)

        # Check if stop is hit
        stop_price = stop_info.get('stop_price', entry_price * (1 - self.initial_stop_pct))

        if position_type == "LONG":
            if current_price <= stop_price:
                return True
        else:  # SHORT
            if current_price >= stop_price:
                return True

        return False
