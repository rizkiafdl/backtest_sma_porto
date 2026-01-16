from trading_infra.strategy import SimpleMovingAverageStrategy, Signal


def test_sma_strategy_generates_signals(sample_ohlcv_df):
    strat = SimpleMovingAverageStrategy(fast_window=2, slow_window=3)
    signals = strat.generate_signals(sample_ohlcv_df)
    
    assert isinstance(signals, list)
    assert all(isinstance(s, Signal) for s in signals)
    assert all(s.side in ("BUY", "SELL") for s in signals)


def test_sma_invalid_windows():
    try:
        SimpleMovingAverageStrategy(10, 5)
        assert False, "Expected ValueError for fast>=slow"
    except ValueError:
        pass
