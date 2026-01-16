from dataclasses import dataclass
from typing import List, Tuple

import pandas as pd

from backtest.strategy import Signal


@dataclass
class Trade:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry_price: float
    exit_price: float
    qty: float


class TradeSimulator:
    def __init__(self, initial_cash: float, risk_per_trade: float = 0.1):
        self.initial_cash = initial_cash
        self.risk_per_trade = risk_per_trade

    def run(
        self,
        price_series: pd.Series,
        signals: List[Signal],
    ) -> Tuple[List[Trade], pd.Series]:
        equity = self.initial_cash
        position_qty = 0.0
        entry_price = None
        entry_time = None

        trades: List[Trade] = []
        equity_curve = []

        signal_idx = {s.timestamp: s for s in signals}

        for ts, price in price_series.items():
         
            if ts in signal_idx:
                sig = signal_idx[ts]
                if sig.side == "BUY" and position_qty == 0:
                    alloc = equity * self.risk_per_trade
                    position_qty = alloc / price
                    entry_price = price
                    entry_time = ts
                elif sig.side == "SELL" and position_qty > 0:
                    exit_price = price
                    pnl = (exit_price - entry_price) * position_qty
                    equity += pnl
                    trades.append(
                        Trade(
                            entry_time=entry_time,
                            exit_time=ts,
                            entry_price=entry_price,
                            exit_price=exit_price,
                            qty=position_qty,
                        )
                    )
                    position_qty = 0.0
                    entry_price = None
                    entry_time = None

            if position_qty > 0:
                current_equity = equity + (price - entry_price) * position_qty
            else:
                current_equity = equity

            equity_curve.append((ts, current_equity))

        equity_series = pd.Series(
            [e for _, e in equity_curve],
            index=[ts for ts, _ in equity_curve],
        )

        return trades, equity_series
