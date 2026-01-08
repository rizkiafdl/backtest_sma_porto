import argparse
import logging
from datetime import datetime

import pandas as pd

from trading_infra.fetcher import MarketDataFetcher
from trading_infra.strategy import SimpleMovingAverageStrategy
from trading_infra.simulator import TradeSimulator
from trading_infra.pnl import PnLCalculator


def configure_logging(level: str = "INFO") -> None:
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simple Backtest runner"
    )

    parser.add_argument(
        "--symbol",
        type=str,
        default="BTCUSDT",
        help="Trading symbol, e.g. BTCUSDT",
    )
    parser.add_argument(
        "--interval",
        type=str,
        default="1h",
        help="Candle interval, e.g. 1m, 5m, 1h, 1d",
    )
    parser.add_argument(
        "--start",
        type=str,
        required=True,
        help="Start date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end",
        type=str,
        required=True,
        help="End date (YYYY-MM-DD)",
    )
    # Strategy params (simple SMA crossover)
    parser.add_argument(
        "--fast-window",
        type=int,
        default=10,
        help="Fast moving average window",
    )
    parser.add_argument(
        "--slow-window",
        type=int,
        default=30,
        help="Slow moving average window",
    )
    # Simulator parameters
    parser.add_argument(
        "--initial-cash",
        type=float,
        default=10000.0,
        help="Initial cash in quote currency",
    )
    parser.add_argument(
        "--risk-per-trade",
        type=float,
        default=0.1,
        help="Fraction of equity to allocate per trade (0–1)",
    )

    return parser.parse_args()


def run_backtest(args: argparse.Namespace) -> None:
    logger = logging.getLogger("Main")

    # 1) Fetch data
    fetcher = MarketDataFetcher()
    df = fetcher.get_historical_ohlcv(
        symbol=args.symbol,
        interval=args.interval,
        start=args.start,
        end=args.end,
    )
    print(df)
    if df.empty:
        logger.error("No data returned. Aborting.")
        return

    logger.info(f"Fetched {len(df)} candles for {args.symbol} @ {args.interval}")

    # 2) Build strategy
    strategy = SimpleMovingAverageStrategy(
        fast_window=args.fast_window,
        slow_window=args.slow_window,
    )

    signals = strategy.generate_signals(df)
    logger.info(f"Generated {len(signals)} signals")

    # 3) Run simulation
    simulator = TradeSimulator(
        initial_cash=args.initial_cash,
        risk_per_trade=args.risk_per_trade,
    )

    trades, equity_curve = simulator.run(
        price_series=df["close"],
        signals=signals,
    )

    logger.info(f"Executed {len(trades)} trades")

    # 4) Compute PnL
    pnl_calc = PnLCalculator()
    summary = pnl_calc.summarize(trades, equity_curve)

    print_summary(args, summary)


def print_summary(args: argparse.Namespace, summary: dict) -> None:
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
    print("\n========== BACKTEST SUMMARY ==========")
    print(f"Symbol           : {args.symbol}")
    print(f"Interval         : {args.interval}")
    print(f"Period           : {args.start} → {args.end}")
    print(f"Strategy         : SMA({args.fast_window}, {args.slow_window})")
    print("--------------------------------------")
    print(f"Start equity     : {summary.get('start_equity'):.2f}")
    print(f"End equity       : {summary.get('end_equity'):.2f}")
    print(f"Total return     : {summary.get('total_return_pct'):.2f}%")
    print(f"Max drawdown     : {summary.get('max_drawdown_pct'):.2f}%")
    print(f"# of trades      : {summary.get('num_trades')}")
    print(f"Win rate         : {summary.get('win_rate_pct'):.2f}%")
    print("======================================\n")


def main() -> None:
    args = parse_args()
    configure_logging()
    run_backtest(args)

if __name__ == "__main__":
    main()
