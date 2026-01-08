# Trading Infra Backtesting Prototype

This project implements a minimal but realistic trading research pipeline with an emphasis on **infrastructure correctness**, **deterministic simulation**, and **reproducible results** rather than alpha discovery. The goal is to demonstrate how data, strategy, execution, and accounting components interact in a research environment.

## 1. Overview

The system performs four core functions:

1. **Market Data Ingestion**
   - Fetches OHLCV historical candles via Binance REST API
   - Normalizes responses to structured DataFrames
   - Handles pagination, retries, and timestamp conversion

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

---

## 2. Architecture



┌──────────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Fetcher     │ →   │  Strategy   │ →   │   Simulator   │ →   │    PnL        │
│ (Binance API) │     │ (Signals)   │     │ (Fills)       │     │ (Metrics)     │
└──────────────┘     └─────────────┘     └──────────────┘     └──────────────┘



Each stage has a well-defined contract:

- `Fetcher` produces **market data**
- `Strategy` produces **signal intents**
- `Simulator` produces **executed trades + equity**
- `PnLCalculator` produces **performance summary**

---

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

---

## 4. Tests

Unit tests cover:

- fetcher normalization + pagination behavior (mocked API)
- strategy signal correctness
- PnL edge cases (zero trades, positive trades)

External dependencies (Binance) are mocked to ensure deterministic results.

Tests are written using:
- `pytest`
- `pytest-mock`

---

## 5. Limitations & Simplifications

This prototype omits complexities that real trading systems must address:

- no transaction costs
- no slippage models
- no latency/clock drift handling
- no shorting or leverage
- no multi-asset portfolios
- no risk management constraints
- no event-driven data ingestion
- Binance API data integrity assumed
- no order routing / book simulation
- no concurrency or async pipelines

These omissions are intentional to keep the focus on **infrastructure shape**, not market realism.

---

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
- real-time paper trading mode
- performance visualization dashboard

---

## 7. Running the Backtest

Example:

```bash
python -m trading_infra.main \
    --symbol BTCUSDT \
    --interval 1h \
    --start 2024-01-01 \
    --end 2024-01-10
````

Outputs:

* performance summary (stdout)
* trades list (optional)
* equity curve (optional csv)

---

## 8. Requirements

* Python 3.10+
* pandas
* requests
* pytest (optional)
* pytest-mock (optional)

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 9. Disclaimer

This repository is for demonstration and research infrastructure purposes only.
It is **not** intended to provide trading advice or imply production-grade quality.

```

---