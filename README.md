# Backtest Package
a small, modular, vectorized, long-only SMA backtester structured as a Python package, runnable via CLI, with test coverage and clear component boundaries.

## 1. Overview

The system performs four core functions:

1. **Market Data Ingestion**
   - Fetches OHLCV historical candles via Binance REST API
   - Normalizes responses to structured DataFrames
   - Handles request, retries, and timestamp conversion

2. **Signal Generation (Strategy Layer)**
   - Converts price series into discrete BUY/SELL/FLAT intents
   - Implements a simple SMA crossover model for demonstration

3. **Execution Simulation (Fill Engine)**
   - Converts signals into filled trades based on mid-price execution
   - Maintains open/closed positions and equity curve over time

4. **Performance Accounting**
   - Computes realized PnL, total return, win rate, and basic drawdowns
   - Produces a time series equity curve for analysis

The primary purpose is to show **modularity and lifecycle control**, not to predict markets.

## 2. Architecture


```
┌──────────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Fetcher    │ →   │  Strategy   │ →   │   Simulator  │ →   │    PnL       │
│ (Binance API)│     │ (Signals)   │     │ (Fills)      │     │ (Metrics)    │
└──────────────┘     └─────────────┘     └──────────────┘     └──────────────┘
```


Each stage has a well-defined contract:

- `Fetcher` produces **market data**
- `Strategy` produces **signal intents**
- `Simulator` produces **executed trades + equity**
- `PnLCalculator` produces **performance summary**

## 3. Components

### **MarketDataFetcher**
Responsibilities:
- REST calls to Binance public endpoints
- retry & backoff for robustness
- pagination for large date windows
- DataFrame normalization
- millisecond → timestamp conversion

Output format:

```
timestamp (index)
open, high, low, close, volume
```

### **Strategy**
Uses a simple moving-average crossover model:

- BUY when fast SMA > slow SMA
- SELL when fast SMA < slow SMA
- ignores sideways/flat noise

Signals are represented as typed objects rather than raw strings to keep the interface clean.

### **Simulator**
Responsibilities:
- position state machine
- fills on next-bar open/mid price (deterministic)
- no slippage, no fees (simplified)
- supports long-only, single position at a time
- outputs equity curve + trade list

Execution model (simplified):

signal → fill → update → next bar


### **PnLCalculator**
Computes:
- realized PnL
- total return %
- win rate %
- max drawdown (basic)
- number of trades

Handles empty-trade cases without error.

## 5. Running the Backtest

**Run Backtest**

```bash
python -m trading_infra.main \
  --symbol BTCUSDT \
  --interval 1h \
  --start 2024-01-01 \
  --end 2024-01-10
```

**Structure**

```
trading_infra/
  fetcher.py
  strategy.py
  simulator.py
  pnl.py
  main.py
  tests/
```

**Install**

```bash
pip install -r trading_infra/requirements.txt
```

**Tests**

Unit tests cover:

- fetcher normalization + pagination behavior (mocked API)
- strategy signal correctness
- PnL edge cases (zero trades, positive trades)


Tests are written using:
- `pytest`
- `pytest-mock`

Run inside the `trading_infra` folder:

```bash
pytest -q -vv
```

- Developed and tested on `Python 3.12.9`
- Executed as a package (must run from outside the folder)

## 6. Future Extensions (if developed further)

Potential upgrades include:

- fee & slippage models
- multi-asset portfolio support
- shorting & leverage
- order-book execution probability
- exchange adapters (REST + WebSocket)
- risk limits & kill-switch logic
- strategy registry + config
- Docker containerization
- performance visualization dashboard