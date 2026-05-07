# core/api_manager.py

import requests
import os
import streamlit as st
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class APIManager:
    def __init__(self):
        # Safely fetch API keys, preventing crashes if st.secrets is unavailable outside Streamlit
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.exchange_rate_api_key = os.getenv("EXCHANGE_RATE_API_KEY")
        
        try:
            if hasattr(st, "secrets"):
                self.news_api_key = st.secrets.get("NEWS_API_KEY", self.news_api_key)
                self.alpha_vantage_api_key = st.secrets.get("ALPHA_VANTAGE_API_KEY", self.alpha_vantage_api_key)
                self.exchange_rate_api_key = st.secrets.get("EXCHANGE_RATE_API_KEY", self.exchange_rate_api_key)
        except Exception:
            pass

    def fetch_news_articles(self, query: str, limit: int = 10) -> list:
        """
        Fetches news articles related to a ticker symbol using Finnhub.io.
        """
        if not self.news_api_key:
            print("Error: News API key not set. Cannot fetch news.")
            return []

        import datetime
        # Finnhub requires a date range. We'll pull news from the last 7 days.
        today = datetime.date.today().strftime('%Y-%m-%d')
        last_week = (datetime.date.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')

        url = f"https://finnhub.io/api/v1/company-news?symbol={query}&from={last_week}&to={today}&token={self.news_api_key}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Finnhub returns a list of dictionaries directly
            articles = data[:limit]
            
            formatted_articles = []
            for article in articles:
                # Map Finnhub's keys to match what our news_analyzer expects
                formatted_articles.append({
                    'title': article.get('headline', 'No Title'),
                    'description': article.get('summary', 'No description available.'),
                    'url': article.get('url', '#'),
                    'source': {'name': article.get('source', 'Finnhub')},
                    # Finnhub returns unix timestamps, so we convert them to readable dates
                    'publishedAt': datetime.datetime.fromtimestamp(article.get('datetime', 0)).strftime('%Y-%m-%d %H:%M:%S') if article.get('datetime') else 'N/A'
                })
                
            return formatted_articles
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news from Finnhub for '{query}': {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred while fetching news: {e}")
            return []
        
    def fetch_company_fundamentals(self, ticker: str) -> dict:
        """Fetches basic company financial fundamentals from Finnhub."""
        if not self.news_api_key: # Reusing the Finnhub key we stored here
            return {}
            
        url = f"https://finnhub.io/api/v1/stock/metric?symbol={ticker}&metric=all&token={self.news_api_key}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('metric', {})
        except Exception as e:
            print(f"Error fetching fundamentals: {e}")
            return {}

    def fetch_alpha_vantage_data(self, symbol: str, function: str, outputsize: str = 'compact') -> Dict[str, Any]:
        if not self.alpha_vantage_api_key:
            print("Error: Alpha Vantage API key not set. Cannot fetch data.")
            return {}

        url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&outputsize={outputsize}&apikey={self.alpha_vantage_api_key}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Alpha Vantage data for '{symbol}': {e}")
            return {}
        except Exception as e:
            print(f"An unexpected error occurred while fetching Alpha Vantage data: {e}")
            return {}

    def fetch_exchange_rates(self, base_currency: str = "USD") -> Optional[Dict[str, float]]:
        if not self.exchange_rate_api_key:
            print("WARNING: EXCHANGE_RATE_API_KEY not set. Currency conversion disabled.")
            return None

        url = f"https://v6.exchangerate-api.com/v6/{self.exchange_rate_api_key}/latest/{base_currency}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['result'] == 'success':
                return data['conversion_rates']
            else:
                print(f"API Error fetching exchange rates: {data.get('error-type', 'Unknown error')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching exchange rates: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None