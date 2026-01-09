from typing import List, Dict

import numpy as np
import pandas as pd

from trading_infra.simulator import Trade


class PnLCalculator:
    def summarize(self, trades: List[Trade], equity_curve: pd.Series) -> Dict:
        if equity_curve.empty:
            return {
                "start_equity": 0.0,
                "end_equity": 0.0,
                "total_return_pct": 0.0,
                "max_drawdown_pct": 0.0,
                "num_trades": 0,
                "win_rate_pct": 0.0,
            }

        start_equity = float(equity_curve.iloc[0])
        end_equity = float(equity_curve.iloc[-1])
        total_return_pct = (end_equity / start_equity - 1.0) * 100.0

        cum_max = equity_curve.cummax()
        drawdown = (equity_curve / cum_max - 1.0) * 100.0
        max_drawdown_pct = float(drawdown.min())

        num_trades = len(trades)
        if num_trades > 0:
            pnl = np.array(
                [(t.exit_price - t.entry_price) * t.qty for t in trades]
            )
            win_rate_pct = float((pnl > 0).mean() * 100.0)
        else:
            win_rate_pct = 0.0
        print(trades)
        return {
            "start_equity": start_equity,
            "end_equity": end_equity,
            "total_return_pct": total_return_pct,
            "max_drawdown_pct": max_drawdown_pct,
            "num_trades": num_trades,
            "win_rate_pct": win_rate_pct,
            "trades": trades
        }
