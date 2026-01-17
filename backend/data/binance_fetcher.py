"""Binance data fetcher for crypto market data."""

import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import requests


class BinanceFetcher:
    """Fetch historical crypto data from Binance public API."""

    BASE_URL = "https://api.binance.com/api/v3"

    # Map friendly intervals to Binance intervals
    INTERVAL_MAP = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h",
        "4h": "4h",
        "1d": "1d",
        "1w": "1w",
    }

    # Map friendly symbols to Binance symbols
    SYMBOL_MAP = {
        "BTC-USD": "BTCUSDT",
        "BTC/USDT": "BTCUSDT",
        "BTCUSDT": "BTCUSDT",
        "ETH-USD": "ETHUSDT",
        "ETH/USDT": "ETHUSDT",
        "ETHUSDT": "ETHUSDT",
        "SOL-USD": "SOLUSDT",
        "SOL/USDT": "SOLUSDT",
        "SOLUSDT": "SOLUSDT",
    }

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize Binance fetcher.

        Args:
            cache_dir: Directory for caching data
        """
        self.cache_dir = Path(cache_dir or "./data_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch(
        self,
        symbol: str,
        start_date: str | datetime,
        end_date: str | datetime,
        interval: str = "15m",
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Fetch historical klines from Binance.

        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT', 'BTC-USD', 'BTC/USDT')
            start_date: Start date (YYYY-MM-DD or datetime)
            end_date: End date (YYYY-MM-DD or datetime)
            interval: Data interval (1m, 5m, 15m, 30m, 1h, 4h, 1d)
            use_cache: Whether to use cached data

        Returns:
            DataFrame with columns: open, high, low, close, volume

        Raises:
            ValueError: If data fetch fails or invalid parameters
        """
        # Normalize symbol
        binance_symbol = self.SYMBOL_MAP.get(symbol.upper(), symbol.upper())

        # Normalize interval
        binance_interval = self.INTERVAL_MAP.get(interval, interval)
        if binance_interval not in self.INTERVAL_MAP.values():
            raise ValueError(f"Invalid interval: {interval}. Valid: {list(self.INTERVAL_MAP.keys())}")

        # Convert dates to timestamps
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        start_ts = int(start_date.timestamp() * 1000)
        end_ts = int(end_date.timestamp() * 1000)

        # Check cache
        cache_file = self._get_cache_path(binance_symbol, start_date, end_date, binance_interval)

        if use_cache and cache_file.exists():
            try:
                data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                if not data.empty:
                    return data
            except Exception as e:
                print(f"Cache read failed: {e}, fetching fresh data")

        # Fetch from Binance API (paginated)
        all_klines = []
        current_start = start_ts

        while current_start < end_ts:
            params = {
                "symbol": binance_symbol,
                "interval": binance_interval,
                "startTime": current_start,
                "endTime": end_ts,
                "limit": 1000  # Max per request
            }

            try:
                response = requests.get(
                    f"{self.BASE_URL}/klines",
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                klines = response.json()

                if not klines:
                    break

                all_klines.extend(klines)

                # Move to next batch
                last_time = klines[-1][0]
                if last_time <= current_start:
                    break
                current_start = last_time + 1

                # Rate limiting
                time.sleep(0.1)

            except requests.exceptions.RequestException as e:
                raise ValueError(f"Binance API error: {str(e)}")

        if not all_klines:
            raise ValueError(f"No data returned for {binance_symbol}")

        # Convert to DataFrame
        data = pd.DataFrame(all_klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])

        # Process data
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data = data.set_index('timestamp')

        # Convert to float
        for col in ['open', 'high', 'low', 'close', 'volume']:
            data[col] = data[col].astype(float)

        # Keep only required columns
        data = data[['open', 'high', 'low', 'close', 'volume']]

        # Remove duplicates
        data = data[~data.index.duplicated(keep='first')]

        # Sort by index
        data = data.sort_index()

        # Save to cache
        if use_cache:
            try:
                data.to_csv(cache_file)
            except Exception as e:
                print(f"Cache write failed: {e}")

        return data

    def _get_cache_path(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str
    ) -> Path:
        """Generate cache file path."""
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        filename = f"binance_{symbol}_{start_str}_{end_str}_{interval}.csv"
        return self.cache_dir / filename

    def get_available_symbols(self) -> list[str]:
        """Get list of available trading pairs."""
        try:
            response = requests.get(f"{self.BASE_URL}/exchangeInfo", timeout=30)
            response.raise_for_status()
            data = response.json()
            return [s['symbol'] for s in data['symbols'] if s['status'] == 'TRADING']
        except Exception as e:
            print(f"Failed to get symbols: {e}")
            return list(self.SYMBOL_MAP.values())
