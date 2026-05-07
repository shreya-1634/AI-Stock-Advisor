# your_project/tests/test_data_fetcher.py

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import os
from core.data_fetcher import DataFetcher

@pytest.fixture
def mock_yfinance_history():
    data = {
        'Open': [100]*30, 'High': [105]*30, 'Low': [95]*30, 'Close': [102]*30, 'Volume': [100000]*30
    }
    dates = pd.date_range(start='2023-01-01', periods=30)
    return pd.DataFrame(data, index=dates)

@pytest.fixture
def data_fetcher_instance():
    test_cache_dir = "tests/test_cache"
    if not os.path.exists(test_cache_dir): os.makedirs(test_cache_dir)
    with patch('core.data_fetcher.DataFetcher.cache_dir', test_cache_dir):
        yield DataFetcher()

def test_fetch_historical_data_fresh(data_fetcher_instance, mock_yfinance_history):
    with patch('yfinance.Ticker') as mock_ticker:
        mock_ticker_instance = MagicMock()
        mock_ticker.return_value = mock_ticker_instance
        mock_ticker_instance.history.return_value = mock_yfinance_history.copy()

        df = data_fetcher_instance.fetch_historical_data("TEST", "1mo")
        assert not df.empty
        assert 'Close' in df.columns

def test_calculate_rsi(data_fetcher_instance, mock_yfinance_history):
    rsi_series = data_fetcher_instance.calculate_rsi(mock_yfinance_history)
    assert not rsi_series.empty

def test_calculate_macd(data_fetcher_instance, mock_yfinance_history):
    macd_df = data_fetcher_instance.calculate_macd(mock_yfinance_history)
    assert not macd_df.empty
    assert 'MACD' in macd_df.columns