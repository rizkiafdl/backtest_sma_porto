import time
import logging
from datetime import datetime
from typing import Optional

import pandas as pd
import requests


class MarketDataFetcher:
    BASE_URL = "https://api.binance.com"

    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.5, timeout: float = 5.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_historical_ohlcv(
        self,
        symbol: str,
        interval: str,
        start: str,
        end: str,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a symbol and interval from Binance.

        Parameters:
            symbol: e.g. 'BTCUSDT'
            interval: e.g. '1m', '1h', '1d'
            start: ISO date string or 'YYYY-MM-DD'
            end: ISO date string or 'YYYY-MM-DD'
            limit: max rows per API call (Binance max=1000)

        Returns:
            pandas DataFrame indexed by timestamp with OHLCV columns.
        """

        start_ms = self._to_ms(start)
        end_ms = self._to_ms(end)

        self.logger.info(f"Fetching OHLCV for {symbol} {interval} {start} → {end}")

        klines = []
        req_start = start_ms

        while req_start < end_ms:
            batch = self._fetch_klines(
                symbol=symbol,
                interval=interval,
                start_ms=req_start,
                end_ms=end_ms,
                limit=limit,
            )
            if not batch:
                break

            klines.extend(batch)
            last_ts = batch[-1][0]

            # Binance klines are inclusive of end, so increment to avoid duplication
            req_start = last_ts + 1

        if not klines:
            self.logger.warning(f"No OHLCV data returned for {symbol} in specified range.")
            return pd.DataFrame()

        df = self._normalize_ohlcv_binance(klines)
        return df

    def _fetch_klines(
        self,
        symbol: str,
        interval: str,
        start_ms: int,
        end_ms: int,
        limit: int
    ):
        url = (
            f"{self.BASE_URL}/api/v3/klines"
            f"?symbol={symbol}&interval={interval}&limit={limit}"
            f"&startTime={start_ms}&endTime={end_ms}"
        )

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.get(url, timeout=self.timeout)

                if resp.status_code == 429:
                    self.logger.warning(f"Rate limited on attempt {attempt}. Sleeping...")
                    time.sleep(self.backoff_factor * attempt)
                    continue

                resp.raise_for_status()
                return resp.json()

            except Exception as e:
                self.logger.error(f"Attempt {attempt}/{self.max_retries} failed: {e}")
                if attempt == self.max_retries:
                    raise
                sleep_time = self.backoff_factor * attempt
                self.logger.info(f"Retrying in {sleep_time:.1f}s...")
                time.sleep(sleep_time)

        return None

    def _normalize_ohlcv_binance(self, raw):
        """
        Normalizes Binance kline format to OHLCV DataFrame.

        Binance kline format:
        [
            [
                0 open_time,
                1 open,
                2 high,
                3 low,
                4 close,
                5 volume,
                6 close_time,
                ...
            ]
        ]
        """
        records = []
        for row in raw:
            records.append({
                "timestamp": datetime.fromtimestamp(row[0] / 1000),
                "open": float(row[1]),
                "high": float(row[2]),
                "low": float(row[3]),
                "close": float(row[4]),
                "volume": float(row[5]),
            })

        df = pd.DataFrame(records)
        df.set_index("timestamp", inplace=True)
        return df

    def _to_ms(self, dt_str: str) -> int:
        return int(pd.Timestamp(dt_str).timestamp() * 1000)
    