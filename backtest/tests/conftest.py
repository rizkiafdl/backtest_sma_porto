import pandas as pd
from datetime import datetime, timedelta
import pytest


@pytest.fixture
def sample_ohlcv_df():
    base = datetime(2024, 1, 1)
    data = {
        "timestamp": [base + timedelta(hours=i) for i in range(10)],
        "open": [100 + i for i in range(10)],
        "high": [101 + i for i in range(10)],
        "low": [99 + i for i in range(10)],
        "close": [100 + i for i in range(10)],
        "volume": [10 for _ in range(10)],
    }
    df = pd.DataFrame(data).set_index("timestamp")
    return df
