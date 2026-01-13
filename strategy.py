from dataclasses import dataclass
from typing import List, Optional
from abc import ABC, abstractmethod

import pandas as pd


@dataclass
class Signal:
    timestamp: pd.Timestamp
    side: str  # "BUY" or "SELL"


class BaseStrategy(ABC):
    """
    Vectorized strategy base:
    - input: price DataFrame (with at least 'close')
    - core output: target_position Series indexed like df.index (e.g. -1, 0, +1)
    - optional: discrete entry/exit signals derived from position changes
    """

    @abstractmethod
    def generate_target_positions(self, df: pd.DataFrame) -> pd.Series:
        """
        Given a DataFrame of market data, return a Series of target positions.
        Convention: -1 = short, 0 = flat, +1 = long (you can limit to {0,1} for long-only).
        """
        raise NotImplementedError

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        """
        Generic implementation:
        - Compute target positions
        - Turn position changes into BUY/SELL signals
        """
        positions = self.generate_target_positions(df)

        prev_positions = positions.shift(1).fillna(0)

        buy_mask = (positions == 1) & (prev_positions == 0)
        sell_mask = (positions == 0) & (prev_positions == 1)

        signals: List[Signal] = []

        for ts in positions.index[buy_mask]:
            signals.append(Signal(timestamp=ts, side="BUY"))

        for ts in positions.index[sell_mask]:
            signals.append(Signal(timestamp=ts, side="SELL"))

        return signals


class SimpleMovingAverageStrategy(BaseStrategy):
    def __init__(self, fast_window: int, slow_window: int):
        if fast_window >= slow_window:
            raise ValueError("fast_window must be < slow_window")
        self.fast_window = fast_window
        self.slow_window = slow_window

    def generate_target_positions(self, df: pd.DataFrame) -> pd.Series:
        """
        Long-only SMA crossover:
        - Go long (1) when fast SMA > slow SMA
        - Go flat (0) otherwise
        - Ignore periods where SMAs are not yet fully defined
        """
        close = df["close"]

        fast = close.rolling(self.fast_window).mean()
        slow = close.rolling(self.slow_window).mean()

        fast_above = fast > slow

        positions = fast_above.astype(int)

        invalid = fast.isna() | slow.isna()
        positions[invalid] = 0

        positions.name = "target_position"
        return positions
