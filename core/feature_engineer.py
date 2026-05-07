import pandas as pd
import numpy as np

class FeatureEngineer:
    def __init__(self, data_fetcher, news_analyzer):
        self.data_fetcher = data_fetcher
        self.news_analyzer = news_analyzer

    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def build_intelligence_matrix(self, ticker, price_df):
        """
        Synthesizes all available factors. If News/Fundamentals are missing,
        it uses advanced technical indicators to fill the intelligence gap.
        """
        matrix = price_df[['Open', 'High', 'Low', 'Close']].copy()

        # --- Technical Factors (Always Available) ---
        matrix['RSI'] = self.calculate_rsi(matrix['Close'])
        matrix['EMA_20'] = matrix['Close'].ewm(span=20, adjust=False).mean() # Short-term trend
        matrix['Volatility'] = matrix['Close'].rolling(window=14).std() # Risk factor

        # --- Fundamental Factors ---
        # We use .get() and a fallback of 0 to prevent crashes
        fundamentals = self.data_fetcher.get_company_fundamentals(ticker)
        if fundamentals:
            matrix['PE_Ratio'] = fundamentals.get('peAnnual', 0)
            matrix['Market_Cap'] = fundamentals.get('marketCapitalization', 0)
        else:
            # If unavailable (common for Indian stocks), use 0
            matrix['PE_Ratio'] = 0
            matrix['Market_Cap'] = 0

        # --- Sentiment Factors ---
        try:
            news = self.news_analyzer.get_news_headlines(ticker)
            sentiment_map = {'positive': 1, 'neutral': 0, 'negative': -1}
            sent_scores = [sentiment_map.get(n.get('sentiment', 'neutral'), 0) for n in news]
            matrix['Sentiment_Score'] = np.mean(sent_scores) if sent_scores else 0
        except:
            matrix['Sentiment_Score'] = 0

        # Final Clean: Use 'ffill' then 0 to ensure the AI never sees a 'NaN'
        return matrix.ffill().fillna(0)