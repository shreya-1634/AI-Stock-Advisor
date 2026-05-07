# core/trading_engine.py

import pandas as pd
import numpy as np

class TradingEngine:
    def calculate_volatility(self, prices: pd.Series, window: int = 20) -> float:
        """Calculates the annualized historical volatility."""
        if prices.empty or len(prices) < window + 1:
            return 0.0

        log_returns = np.log(prices / prices.shift(1)).dropna()
        if log_returns.empty or len(log_returns) < window:
             return 0.0

        volatility = log_returns.rolling(window=window).std() * np.sqrt(252)
        return float(volatility.iloc[-1]) if not volatility.empty else 0.0

    def generate_recommendation(self, predicted_close_price: float, current_close_price: float, 
                                volatility: float, rsi: float, macd_diff: float,
                                news_sentiment: str = "neutral", price_change_threshold: float = 0.02) -> str:
        """Generates a Buy/Sell/Hold recommendation."""
        recommendation_score = 0
        
        # 1. Prediction Logic
        if current_close_price > 0:
            price_change_percent = (predicted_close_price - current_close_price) / current_close_price
            if price_change_percent > price_change_threshold:
                recommendation_score += 2
            elif price_change_percent < -price_change_threshold:
                recommendation_score -= 2
            else:
                recommendation_score += price_change_percent * 50 # Small adjustments

        # 2. RSI Logic
        if pd.notna(rsi):
            if rsi < 30 and recommendation_score < 1.5:
                recommendation_score += 1
            elif rsi > 70 and recommendation_score > -1.5:
                recommendation_score -= 1

        # 3. MACD Logic
        if pd.notna(macd_diff):
            if macd_diff > 0:
                recommendation_score += 0.5
            elif macd_diff < 0:
                recommendation_score -= 0.5

        # 4. Sentiment Logic
        if news_sentiment == "positive":
            recommendation_score += 1
        elif news_sentiment == "negative":
            recommendation_score -= 1

        # 5. Volatility Penalty
        if volatility > 0.6: # High volatility dampens the score
            recommendation_score *= 0.7

        # Final Verdict
        if recommendation_score >= 2.5:
            return "Strong Buy"
        elif recommendation_score >= 1.0:
            return "Buy"
        elif recommendation_score <= -2.5:
            return "Strong Sell"
        elif recommendation_score <= -1.0:
            return "Sell"
        else:
            return "Hold"