from dataclasses import dataclass
from typing import List
import pandas as pd


@dataclass
class Signal:
    timestamp: pd.Timestamp
    side: str  # "BUY" or "SELL"


class SimpleMovingAverageStrategy:
    def __init__(self, fast_window: int, slow_window: int):
        if fast_window >= slow_window:
            raise ValueError("fast_window must be < slow_window")
        self.fast_window = fast_window
        self.slow_window = slow_window

    def generate_signals(self, df: pd.DataFrame) -> List[Signal]:
        close = df["close"]
        fast = close.rolling(self.fast_window).mean()
        slow = close.rolling(self.slow_window).mean()

        signals: List[Signal] = []
        prev_fast_above = None

        for ts, f, s in zip(df.index, fast, slow):
            if pd.isna(f) or pd.isna(s):
                continue

            fast_above = f > s

            if prev_fast_above is None:
                prev_fast_above = fast_above
                continue

            if fast_above and not prev_fast_above:
                signals.append(Signal(timestamp=ts, side="BUY"))
            elif not fast_above and prev_fast_above:
                signals.append(Signal(timestamp=ts, side="SELL"))

            prev_fast_above = fast_above
            print(signals)
        return signals
