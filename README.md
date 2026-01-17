# Backtest Package
a small, modular, long-only SMA backtester structured as a Python package, runnable via CLI, with test coverage and clear component boundaries.

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

## 4. Running the Backtest

**Run Backtest**


**Structure**

```
backtest/
  fetcher.py
  strategy.py
  simulator.py
  pnl.py
  main.py
  tests/
```

## Installation

Clone repository:

```bash
git clone https://github.com/rizkiafdl/backtest_sma_porto.git
```

```bash
cd backtest_sma_porto

pip install -r requirements.txt

pip install -e .

```

Test Import :
``` bash
python -c "import backtest; print(dir(backtest))"
```

Can check examples dir for usage of the package!

**Tests**

Unit tests cover:

- fetcher normalization + pagination behavior (mocked API)
- strategy signal correctness
- PnL edge cases (zero trades, positive trades)


Tests are written using:
- `pytest`
- `pytest-mock`

Run inside the `backtest` folder:

```bash
pytest -q -vv
```

- Developed and tested on `Python 3.12.9`

## 5. Future Extensions (if developed further)

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