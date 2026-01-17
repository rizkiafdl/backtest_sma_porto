from typing import List, Dict

import numpy as np
import pandas as pd

from backtest.simulator import Trade


class PnLCalculator:
    def __init__(self):
        
        self.summary_data = {}

        
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
        self.summary_data = {
            "start_equity": start_equity,
            "end_equity": end_equity,
            "total_return_pct": total_return_pct,
            "max_drawdown_pct": max_drawdown_pct,
            "num_trades": num_trades,
            "win_rate_pct": win_rate_pct,
            "trades": trades
        }
        return self.summary_data
        
    def print_summary(self,print_trades) -> None:
        """
        Pretty-print backtest summary.
        Expected keys in summary:
        - total_return_pct
        - max_drawdown_pct
        - num_trades
        - win_rate_pct
        - start_equity
        - end_equity
        """
  
        trades = self.summary_data.get("trades", [])
        if trades and print_trades:
            print("======================================\n")
            print("Trades:")
            for t in trades:
                pnl = (t.exit_price - t.entry_price) * t.qty
                print(
                    f"{t.entry_time} → {t.exit_time} | "
                    f"entry={t.entry_price:.2f}, exit={t.exit_price:.2f}, "
                    f"qty={t.qty:.5f}, pnl={pnl:.2f}"
                )
            
        print("\n========== BACKTEST SUMMARY ==========")
        print("--------------------------------------")
        print(f"Start equity     : {self.summary_data.get('start_equity'):.2f}")
        print(f"End equity       : {self.summary_data.get('end_equity'):.2f}")
        print(f"Total return     : {self.summary_data.get('total_return_pct'):.2f}%")
        print(f"Max drawdown     : {self.summary_data.get('max_drawdown_pct'):.2f}%")
        print(f"# of trades      : {self.summary_data.get('num_trades')}")
        print(f"Win rate         : {self.summary_data.get('win_rate_pct'):.2f}%")
        print("======================================")
