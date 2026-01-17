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
