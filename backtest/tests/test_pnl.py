from trading_infra.pnl import PnLCalculator
from trading_infra.simulator import Trade
from datetime import datetime
import pandas as pd


def test_pnl_summary_positive():
    trades = [
        Trade(
            entry_time=datetime(2024, 1, 1),
            exit_time=datetime(2024, 1, 2),
            entry_price=100,
            exit_price=110,
            qty=1.0
        )
    ]
    equity = pd.Series([10000, 10100], index=[datetime(2024, 1, 1), datetime(2024, 1, 2)])

    pnl = PnLCalculator().summarize(trades, equity)

    assert pnl["total_return_pct"] > 0
    assert pnl["num_trades"] == 1
    assert pnl["win_rate_pct"] == 100.0


def test_pnl_summary_zero_trades():
    pnl = PnLCalculator().summarize([], pd.Series([10000, 10000]))
    assert pnl["num_trades"] == 0
    assert pnl["win_rate_pct"] == 0.0
