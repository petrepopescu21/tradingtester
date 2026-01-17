"""Data fetcher for historical market data."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf
from dotenv import load_dotenv


class DataFetcher:
    """Fetch and cache historical market data."""

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize data fetcher.

        Args:
            cache_dir: Directory for caching data (defaults to env var or './data_cache')
        """
        load_dotenv()

        self.cache_dir = Path(
            cache_dir or os.getenv("DATA_CACHE_DIR", "./data_cache")
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch(
        self,
        symbol: str,
        start_date: str | datetime,
        end_date: str | datetime,
        interval: str = "1d",
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Fetch historical data for a symbol.

        Args:
            symbol: Trading symbol (e.g., 'AAPL', 'SPY')
            start_date: Start date (YYYY-MM-DD or datetime)
            end_date: End date (YYYY-MM-DD or datetime)
            interval: Data interval (1d, 1h, etc.)
            use_cache: Whether to use cached data

        Returns:
            DataFrame with columns: Open, High, Low, Close, Volume, Adj Close

        Raises:
            ValueError: If data fetch fails
        """
        # Convert dates to strings
        if isinstance(start_date, datetime):
            start_date = start_date.strftime("%Y-%m-%d")
        if isinstance(end_date, datetime):
            end_date = end_date.strftime("%Y-%m-%d")

        # Check cache
        cache_file = self._get_cache_path(symbol, start_date, end_date, interval)

        if use_cache and cache_file.exists():
            try:
                data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                return data
            except Exception as e:
                print(f"Cache read failed: {e}, fetching fresh data")

        # Fetch from yfinance
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval
            )

            if data.empty:
                raise ValueError(f"No data returned for {symbol}")

            # Standardize column names
            data.columns = [col.lower() for col in data.columns]

            # Rename to match expected format
            column_mapping = {
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume',
                'adj close': 'adj_close'
            }

            data = data.rename(columns=column_mapping)

            # Ensure we have required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in data.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            # Save to cache
            if use_cache:
                try:
                    data.to_csv(cache_file)
                except Exception as e:
                    print(f"Cache write failed: {e}")

            return data

        except Exception as e:
            raise ValueError(f"Failed to fetch data for {symbol}: {str(e)}")

    def fetch_multiple(
        self,
        symbols: list[str],
        start_date: str | datetime,
        end_date: str | datetime,
        interval: str = "1d",
        use_cache: bool = True
    ) -> dict[str, pd.DataFrame]:
        """
        Fetch data for multiple symbols.

        Args:
            symbols: List of trading symbols
            start_date: Start date
            end_date: End date
            interval: Data interval
            use_cache: Whether to use cached data

        Returns:
            Dictionary mapping symbol to DataFrame
        """
        results = {}

        for symbol in symbols:
            try:
                data = self.fetch(
                    symbol,
                    start_date,
                    end_date,
                    interval,
                    use_cache
                )
                results[symbol] = data
            except Exception as e:
                print(f"Failed to fetch {symbol}: {e}")
                results[symbol] = pd.DataFrame()

        return results

    def _get_cache_path(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str
    ) -> Path:
        """Generate cache file path."""
        filename = f"{symbol}_{start_date}_{end_date}_{interval}.csv"
        return self.cache_dir / filename

    def clear_cache(self, symbol: Optional[str] = None):
        """
        Clear cached data.

        Args:
            symbol: If provided, only clear cache for this symbol
        """
        if symbol:
            # Clear specific symbol
            for cache_file in self.cache_dir.glob(f"{symbol}_*.csv"):
                cache_file.unlink()
        else:
            # Clear all cache
            for cache_file in self.cache_dir.glob("*.csv"):
                cache_file.unlink()
