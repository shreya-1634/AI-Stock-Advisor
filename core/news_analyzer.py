# core/news_analyzer.py

from core.api_manager import APIManager
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Safely download VADER lexicon
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except Exception: 
    print("VADER lexicon not found, attempting to download...")
    try:
        nltk.download('vader_lexicon')
    except Exception as e:
        print(f"Error downloading VADER lexicon: {e}")

class NewsAnalyzer:
    def __init__(self):
        self.api_manager = APIManager()
        self.sid = SentimentIntensityAnalyzer()

    def get_news_headlines(self, query: str, limit: int = 5) -> list:
        """Fetches news and calculates sentiment for each article."""
        articles = self.api_manager.fetch_news_articles(query, limit)
        
        processed_articles = []
        for article in articles:
            # Combine title and description for better sentiment analysis
            text_to_analyze = article.get('title', '') + " " + article.get('description', '')
            
            processed_articles.append({
                'title': article.get('title', 'No Title'),
                'description': article.get('description', 'No description available.'),
                'url': article.get('url', '#'),
                'source': article.get('source', {}).get('name', 'N/A'),
                'publishedAt': article.get('publishedAt', 'N/A'),
                'sentiment': self.analyze_sentiment(text_to_analyze)
            })
        return processed_articles

    def analyze_sentiment(self, text: str) -> str:
        """Analyzes sentiment returning positive, negative, or neutral."""
        if not text:
            return "neutral"
            
        scores = self.sid.polarity_scores(text)
        compound_score = scores['compound']
        
        if compound_score >= 0.05:
            return "positive"
        elif compound_score <= -0.05:
            return "negative"
        else:
            return "neutral"