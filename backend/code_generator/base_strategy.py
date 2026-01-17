"""Base strategy class that all generated strategies inherit from."""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional


class Strategy(ABC):
    """Base class for all trading strategies."""

    def __init__(self, name: str):
        """
        Initialize strategy.

        Args:
            name: Strategy name
        """
        self.name = name
        self.positions: dict[str, dict] = {}  # symbol -> {entry_price, size, entry_date}
        self.trailing_stops: dict[str, dict] = {}  # symbol -> {stop_price, highest_price, activated}
        self.leverage: float = 1.0  # Default no leverage
        self.asset_class: str = "equity"  # equity, crypto, futures

    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators needed for the strategy.

        Args:
            data: DataFrame with OHLCV data

        Returns:
            DataFrame with added indicator columns
        """
        pass

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy/sell signals based on strategy rules.

        Args:
            data: DataFrame with OHLCV data and indicators

        Returns:
            DataFrame with 'signal' column added:
            - 1 for buy/long entry
            - -1 for sell/short entry
            - 0 for hold/no action
        """
        pass

    @abstractmethod
    def calculate_position_size(
        self,
        symbol: str,
        price: float,
        portfolio_value: float,
        data: pd.DataFrame
    ) -> int:
        """
        Calculate position size based on strategy rules.

        Args:
            symbol: Trading symbol
            price: Current price
            portfolio_value: Current portfolio value
            data: DataFrame with current market data

        Returns:
            Number of shares to buy/sell
        """
        pass

    @abstractmethod
    def check_exit_conditions(
        self,
        symbol: str,
        current_price: float,
        entry_price: float,
        days_held: int,
        data: pd.DataFrame,
        position_type: str = "LONG"
    ) -> bool:
        """
        Check if exit conditions are met for a position.

        Args:
            symbol: Trading symbol
            current_price: Current price
            entry_price: Entry price of the position
            days_held: Number of days position has been held
            data: DataFrame with current market data
            position_type: "LONG" or "SHORT"

        Returns:
            True if should exit, False otherwise
        """
        pass

    def get_position(self, symbol: str) -> Optional[dict]:
        """Get current position for a symbol."""
        return self.positions.get(symbol)

    def has_position(self, symbol: str) -> bool:
        """Check if there's an open position for a symbol."""
        return symbol in self.positions

    def open_position(
        self,
        symbol: str,
        entry_price: float,
        size: int,
        entry_date: pd.Timestamp,
        position_type: str = "LONG"
    ):
        """Record opening a position."""
        self.positions[symbol] = {
            "entry_price": entry_price,
            "size": size,
            "entry_date": entry_date,
            "type": position_type
        }

    def close_position(self, symbol: str):
        """Record closing a position."""
        if symbol in self.positions:
            del self.positions[symbol]
        if symbol in self.trailing_stops:
            del self.trailing_stops[symbol]

    def get_leverage(self, data: pd.DataFrame) -> float:
        """
        Get leverage for the current trade. Override for dynamic leverage.

        Args:
            data: DataFrame with current market data

        Returns:
            Leverage multiplier (1.0 = no leverage)
        """
        return self.leverage

    def update_trailing_stop(
        self,
        symbol: str,
        current_price: float,
        entry_price: float,
        position_type: str = "LONG"
    ) -> Optional[float]:
        """
        Update trailing stop and return current stop price.

        Args:
            symbol: Trading symbol
            current_price: Current price
            entry_price: Entry price of position
            position_type: "LONG" or "SHORT"

        Returns:
            Current stop price, or None if not set
        """
        if symbol not in self.trailing_stops:
            return None

        stop_info = self.trailing_stops[symbol]

        if position_type == "LONG":
            # Update highest price
            if current_price > stop_info.get("highest_price", entry_price):
                stop_info["highest_price"] = current_price
        else:  # SHORT
            # Update lowest price for shorts
            if current_price < stop_info.get("lowest_price", entry_price):
                stop_info["lowest_price"] = current_price

        return stop_info.get("stop_price")

    def init_trailing_stop(
        self,
        symbol: str,
        entry_price: float,
        initial_stop_pct: float,
        position_type: str = "LONG"
    ):
        """
        Initialize trailing stop for a position.

        Args:
            symbol: Trading symbol
            entry_price: Entry price
            initial_stop_pct: Initial stop loss percentage (e.g., 0.02 for 2%)
            position_type: "LONG" or "SHORT"
        """
        if position_type == "LONG":
            stop_price = entry_price * (1 - initial_stop_pct)
            self.trailing_stops[symbol] = {
                "stop_price": stop_price,
                "highest_price": entry_price,
                "activated": False,
                "initial_stop_pct": initial_stop_pct
            }
        else:  # SHORT
            stop_price = entry_price * (1 + initial_stop_pct)
            self.trailing_stops[symbol] = {
                "stop_price": stop_price,
                "lowest_price": entry_price,
                "activated": False,
                "initial_stop_pct": initial_stop_pct
            }

    def is_in_session(self, timestamp: pd.Timestamp, sessions: list[tuple[int, int]]) -> bool:
        """
        Check if timestamp is within allowed trading sessions.

        Args:
            timestamp: Current timestamp
            sessions: List of (start_hour, end_hour) tuples in UTC

        Returns:
            True if within a trading session
        """
        hour = timestamp.hour
        for start_hour, end_hour in sessions:
            if start_hour <= end_hour:
                if start_hour <= hour < end_hour:
                    return True
            else:  # Crosses midnight
                if hour >= start_hour or hour < end_hour:
                    return True
        return False
