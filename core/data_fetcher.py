# core/data_fetcher.py

from core.api_manager import APIManager
import yfinance as yf
import pandas as pd
import ta
import os

class DataFetcher:
    def __init__(self):
        # 1. Initialize the API Manager (for company fundamentals)
        self.api_manager = APIManager()
        
        # 2. Re-initialize the Cache Directory (for historical data)
        self.cache_dir = "data_cache" # Or "cache" if that's what you originally named your folder
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_company_fundamentals(self, ticker: str) -> dict:
        return self.api_manager.fetch_company_fundamentals(ticker)
        return self.api_manager.fetch_company_fundamentals(ticker)
    
    def fetch_historical_data(self, ticker_symbol: str, period: str = "1y") -> pd.DataFrame:
        """Fetches historical stock data using yfinance, with local caching."""
        cache_path = os.path.join(self.cache_dir, f"{ticker_symbol}_{period}.csv")
        
        # Load from cache if it exists and is recent
        if os.path.exists(cache_path):
            try:
                df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
                if not df.empty:
                    return df
            except Exception as e:
                print(f"Cache read error: {e}")

        # Fetch fresh data
        try:
            stock = yf.Ticker(ticker_symbol)
            df = stock.history(period=period)
            if df.empty:
                return pd.DataFrame()
                
            # Clean index and save to cache
            df.index = pd.to_datetime(df.index).tz_localize(None)
            df.to_csv(cache_path)
            return df
        except Exception as e:
            print(f"Error fetching data for {ticker_symbol}: {e}")
            return pd.DataFrame()

    def calculate_rsi(self, df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """Calculates the Relative Strength Index."""
        if 'Close' not in df.columns or len(df) < window:
            df['RSI'] = None
            return df
        indicator_rsi = ta.momentum.RSIIndicator(close=df["Close"], window=window, fillna=True)
        df['RSI'] = indicator_rsi.rsi()
        return df

    def calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates MACD, Signal Line, and Difference."""
        if 'Close' not in df.columns or len(df) < 30:
            df['MACD'] = None
            df['MACD_Signal'] = None
            df['MACD_Diff'] = None
            return df
        macd = ta.trend.MACD(close=df['Close'], fillna=True)
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Diff'] = macd.macd_diff()
        return df