from trading_infra.fetcher import MarketDataFetcher


def test_fetcher_normalizes_ohlcv(mocker):
    mock_resp = mocker.MagicMock()
    mock_resp.status_code = 200
    mock_resp_empty = mocker.MagicMock()
    mock_resp_empty.status_code = 200
    mock_resp_empty.json.return_value = []
    
    mock_resp.json.return_value = [
        [1704067200000, "100", "105", "95", "102", "123.45", None, None, None, None, None, None],
        [1704070800000, "102", "108", "98", "105", "234.56", None, None, None, None, None, None],
    ]

    mocker.patch("trading_infra.fetcher.requests.get", 
                 side_effect=[mock_resp, mock_resp_empty])

    fetcher = MarketDataFetcher()
    df = fetcher.get_historical_ohlcv(
        symbol="BTCUSDT", interval="1h",
        start="2024-01-01", end="2024-01-02"
    )

    assert not df.empty
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert df.index.name == "timestamp"


def test_fetcher_empty_result(mocker):
    mock_resp = mocker.MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = []
    mocker.patch("trading_infra.fetcher.requests.get", return_value=mock_resp)

    fetcher = MarketDataFetcher()
    df = fetcher.get_historical_ohlcv(
        symbol="BTCUSDT", interval="1h",
        start="2024-01-01", end="2024-01-01"
    )

    assert df.empty
