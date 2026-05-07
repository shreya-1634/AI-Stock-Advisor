# your_project/app.py
import plotly.graph_objects as go
from core.feature_engineer import FeatureEngineer
import streamlit as st
import pandas as pd
import time
import os
import json
from typing import Optional

# Import custom modules from your project structure
from auths.auth import AuthManager
from core.data_fetcher import DataFetcher
from core.visualization import Visualization
from core.news_analyzer import NewsAnalyzer
from core.predictor import Predictor
from core.trading_engine import TradingEngine
from utils.session_utils import SessionManager
from db.user_manager import UserManager
from utils.formatting import Formatting
from utils.currency_converter import CurrencyConverter

# Suppress TensorFlow Logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Initialize Managers
auth_manager = AuthManager()
data_fetcher = DataFetcher()
visualization = Visualization()
news_analyzer = NewsAnalyzer()
predictor = Predictor()
trading_engine = TradingEngine()
user_db = UserManager()
session_manager = SessionManager()
converter = CurrencyConverter() # Initialize the currency converter
feature_engineer = FeatureEngineer(data_fetcher, news_analyzer)

def load_css(file_name="styles.css"):
    css_path = os.path.join("static", file_name)
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(layout="wide", page_title="AI Stock Advisor")
load_css()

def load_static_config(file_name="config.json"):
    config_path = os.path.join("static", file_name)
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            st.error(f"Error decoding {file_name}: {e}")
    return {}

static_ui_config = load_static_config()
app_name = static_ui_config.get("app_info", {}).get("app_name", "AI Stock Advisor")

def auth_sidebar_ui():
    st.sidebar.title("Account Access")
    if 'auth_page_selection' not in st.session_state:
        st.session_state['auth_page_selection'] = 'Login'
    auth_page_options = ["Login", "Sign Up", "Reset Password"]
    st.session_state['auth_page_selection'] = st.sidebar.radio(
        "Go to", auth_page_options, key="auth_page_radio", 
        index=auth_page_options.index(st.session_state['auth_page_selection'])
    )
    if st.session_state['auth_page_selection'] == "Login":
        auth_manager.login_ui()
    elif st.session_state['auth_page_selection'] == "Sign Up":
        auth_manager.signup_ui()
    elif st.session_state['auth_page_selection'] == "Reset Password":
        auth_manager.reset_password_ui()
    if session_manager.is_logged_in():
        st.rerun()

def main_app_ui():
    user_email = session_manager.get_current_user_email()
    user_role = session_manager.get_current_user_role()

    st.sidebar.title(f"Welcome, {user_email}!")
    st.sidebar.write(f"Role: **Admin (Unlocked)**") # Reflected as unlocked!
    if st.sidebar.button("Logout", key="sidebar_logout_button"):
        session_manager.logout_user()
        st.rerun()

    st.title(app_name)
    st.markdown("---")

    # --- Updated 3-Column Layout for Ticker, Period, and Currency ---
    col_ticker, col_period, col_currency = st.columns([0.4, 0.3, 0.3])
    
    with col_ticker:
        ticker_symbol = st.text_input("Enter Stock Ticker Symbol (e.g., AAPL):", "AAPL", key="ticker_input").upper().strip()
    with col_period:
        period_options = {
            "1 Day": "1d", "5 Days": "5d", "1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo",
            "1 Year": "1y", "2 Years": "2y", "5 Years": "5y", "10 Years": "10y", "Year To Date": "ytd", "Max": "max"
        }
        selected_period_label = st.selectbox("Select Period", list(period_options.keys()), index=5, key="period_selector")
        historical_period = period_options[selected_period_label]
    with col_currency:
        target_currency = st.selectbox("Select Currency", converter.supported_currencies, index=0)

    if st.button("Analyze Stock", use_container_width=True, key="analyze_button"):
        if not ticker_symbol:
            st.warning("Please enter a ticker symbol.")
            return

        st.subheader(f"Analysis for {ticker_symbol}")

        with st.spinner(f"Fetching historical data for the last {selected_period_label}..."):
            df = data_fetcher.fetch_historical_data(ticker_symbol, period=historical_period)
            if df.empty:
                st.error(f"Could not fetch data for {ticker_symbol}. Please check the ticker symbol or try again later.")
                user_db.log_activity(user_email, "data_fetch_failed", f"Ticker: {ticker_symbol}, Period: {historical_period}")
                return
            user_db.log_activity(user_email, "data_fetch_success", f"Ticker: {ticker_symbol}, Period: {historical_period}")
        
        # --- Company Fundamentals (Interactive & Currency-Aware) ---
        st.markdown("### Company Fundamentals")
        with st.spinner("Fetching financial metrics..."):
            fundamentals = data_fetcher.get_company_fundamentals(ticker_symbol)
            if fundamentals:
                # 1. Extract raw data (Finnhub market cap is usually in millions)
                raw_high = fundamentals.get('52WeekHigh')
                raw_low = fundamentals.get('52WeekLow')
                raw_mkt_cap = fundamentals.get('marketCapitalization')
                raw_pe = fundamentals.get('peAnnual', 'N/A')

                # 2. Convert currencies if needed
                if target_currency != "USD":
                    disp_high = converter.convert(raw_high, target_currency) if raw_high else None
                    disp_low = converter.convert(raw_low, target_currency) if raw_low else None
                    disp_mkt_cap = converter.convert(raw_mkt_cap, target_currency) if raw_mkt_cap else None
                else:
                    disp_high, disp_low, disp_mkt_cap = raw_high, raw_low, raw_mkt_cap

                # 3. Format the strings safely
                str_high = f"{disp_high:,.2f} {target_currency}" if disp_high else "N/A"
                str_low = f"{disp_low:,.2f} {target_currency}" if disp_low else "N/A"
                str_mkt_cap = f"{(disp_mkt_cap / 1000):,.2f}B {target_currency}" if disp_mkt_cap else "N/A"
                str_pe = f"{raw_pe:.2f}" if isinstance(raw_pe, (int, float)) else "N/A"

                # 4. Render with interactive tooltips!
                f_col1, f_col2, f_col3, f_col4 = st.columns(4)
                
                f_col1.metric(
                    label="52 Week High", 
                    value=str_high, 
                    help="The highest price the stock has traded at in the last 12 months."
                )
                f_col2.metric(
                    label="52 Week Low", 
                    value=str_low, 
                    help="The lowest price the stock has traded at in the last 12 months."
                )
                f_col3.metric(
                    label="Market Cap", 
                    value=str_mkt_cap, 
                    help="Total dollar market value of a company's outstanding shares of stock."
                )
                f_col4.metric(
                    label="P/E Ratio (Annual)", 
                    value=str_pe, 
                    help="Price-to-Earnings Ratio. A high P/E could mean the stock is overvalued, or that investors expect high growth in the future."
                )
            else:
                st.info("Fundamental data not available for this ticker.")
                
        st.markdown("---")
        
        st.write("### Latest Price Information")
        
        # --- Handle Currency Conversion & Date Extraction ---
        current_open = df['Open'].iloc[-1]
        current_close = df['Close'].iloc[-1]
        
        # Extract the exact date of this last row of data
        last_trading_date = df.index[-1].strftime('%B %d, %Y')

        if target_currency != "USD":
            display_open = converter.convert(current_open, target_currency)
            display_close = converter.convert(current_close, target_currency)
            if display_open is None or display_close is None:
                display_open, display_close = current_open, current_close
                st.warning("Currency conversion API unavailable. Displaying in USD.")
                target_currency = "USD"
        else:
            display_open = current_open
            display_close = current_close

        col_open, col_close = st.columns(2)
        with col_open:
            # Add the exact date to the label so the user knows exactly what they are looking at
            st.metric(label=f"Open Price ({last_trading_date})", value=f"{display_open:,.2f} {target_currency}")
        with col_close:
            st.metric(label=f"Close/Current Price ({last_trading_date})", value=f"{display_close:,.2f} {target_currency}")

        with st.spinner("Calculating indicators..."):  
            # 1. Safely calculate and merge RSI
            rsi_data = data_fetcher.calculate_rsi(df)
            if isinstance(rsi_data, pd.DataFrame):
                df['RSI'] = rsi_data.iloc[:, 0]  
            else:
                df['RSI'] = rsi_data             

            # 2. Safely calculate and merge MACD
            macd_data = data_fetcher.calculate_macd(df)
            if isinstance(macd_data, pd.DataFrame):
                for col in macd_data.columns:
                    df[col] = macd_data[col]

       # --- Interactive Plotly Chart (Fully Unlocked) ---
        st.markdown("### Candlestick Chart")
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Price"
        )])

        fig.update_layout(
            title=f"{ticker_symbol} Price Movement",
            yaxis_title=f"Stock Price ({target_currency})",
            xaxis_title="Date",
            template="plotly_dark", 
            xaxis_rangeslider_visible=False, 
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- Live News (Fully Unlocked) ---
        st.markdown("### Latest News")
        with st.spinner("Fetching live news..."):
            news_articles = news_analyzer.get_news_headlines(ticker_symbol)
            st.session_state['news_sentiment'] = 'neutral'
            if news_articles:
                for i, article in enumerate(news_articles):
                    st.markdown(f"**{i+1}. [{article.get('title', 'No Title')}]({article.get('url', '#')})**")
                    st.write(article.get('description', 'No description available.'))
                    
                    sentiment = article.get('sentiment', 'N/A')
                    st.write(f"Sentiment: **{sentiment.capitalize()}**")
                    if sentiment == 'positive': st.session_state['news_sentiment'] = 'positive'
                    elif sentiment == 'negative': st.session_state['news_sentiment'] = 'negative'
                    
                    published_at = article.get('publishedAt')
                    formatted_date = Formatting.format_date(pd.to_datetime(published_at), date_format="%Y-%m-%d %H:%M") if published_at and published_at != 'N/A' else 'N/A'
                    st.write(f"Source: {article.get('source', 'N/A')} | Published: {formatted_date}")
                    st.markdown("---")
            else:
                st.info(f"No recent news found for {ticker_symbol}.")

        # --- Price Predictions (Fully Unlocked) ---
        st.markdown("### Future Price Prediction")
        
        # Add a slider for the user to choose how many days to predict (1 to 10)
        prediction_days = st.slider("Select number of days to predict:", min_value=1, max_value=10, value=3, key="pred_slider")
        
        predicted_prices_df = pd.DataFrame()
        with st.spinner(f"Predicting future prices for the next {prediction_days} days..."):
            predictor.load_model()
            if predictor.model:
                # 1. Run the prediction
                predicted_prices_df = predictor.predict_prices(ticker_symbol, df, feature_engineer, num_predictions=prediction_days)
                
                if not predicted_prices_df.empty:
                    # 2. Convert currency if necessary
                    if target_currency != "USD":
                        predicted_prices_df = predicted_prices_df.applymap(
                            lambda x: converter.convert(x, target_currency) if x is not None else x
                        )
                    
                    # 3. Display the results
                    st.write(f"Predicted OHLC prices for the next {prediction_days} trading days ({target_currency}):")
                    st.dataframe(predicted_prices_df.style.format(formatter="{:.2f}"), use_container_width=True)
                    
                    # 4. Plot the chart
                    st.plotly_chart(visualization.plot_prediction_chart(df, predicted_prices_df), use_container_width=True)
                    
                    user_db.log_activity(user_email, "prediction_success", f"Ticker: {ticker_symbol}")
                else:
                    st.warning("Could not generate price prediction. Ensure model is trained and data is sufficient.")
                    user_db.log_activity(user_email, "prediction_failed", f"Ticker: {ticker_symbol} - No prediction data.")
            else:
                st.warning("Prediction model not available. Please ensure it is trained and loaded correctly.")
                
        # --- Volatility (Fully Unlocked) ---
        st.markdown("### Market Volatility")
        current_volatility = 0.0
        with st.spinner("Calculating market volatility..."):
            current_volatility = trading_engine.calculate_volatility(df['Close'])
            st.info(f"Current Annualized Volatility (last 20 days): **{current_volatility:.2f}%**")

        # --- Recommendations (Fully Unlocked) ---
        st.markdown("### Recommendation")
        with st.spinner("Generating recommendation..."):
            if not predicted_prices_df.empty and not df.empty:
                current_price = df['Close'].iloc[-1]
                predicted_close_price = predicted_prices_df['Predicted Close'].iloc[0]
                recommendation = trading_engine.generate_recommendation(
                    predicted_close_price=predicted_close_price,
                    current_close_price=current_price,
                    volatility=current_volatility,
                    rsi=df['RSI'].iloc[-1] if not df['RSI'].isnull().all() else 50,
                    macd_diff=df['MACD_Diff'].iloc[-1] if 'MACD_Diff' in df.columns and not df['MACD_Diff'].isnull().all() else 0,
                    news_sentiment=st.session_state.get('news_sentiment', 'neutral')
                )
                
                if recommendation in ["Buy", "Strong Buy"]:
                    st.success(f"**Recommendation: {recommendation}** - Strong indicators for potential growth.")
                elif recommendation in ["Sell", "Strong Sell"]:
                    st.error(f"**Recommendation: {recommendation}** - Indicators suggest potential decline.")
                else:
                    st.warning(f"**Recommendation: {recommendation}** - Market conditions are uncertain or balanced, consider holding.")
                
                user_db.log_activity(user_email, "recommendation_given", f"Ticker: {ticker_symbol}, Rec: {recommendation}") # Fixed _log
            else:
                st.warning("Cannot generate recommendation without prediction data.")

if __name__ == "__main__":
    if not session_manager.is_logged_in():
        auth_sidebar_ui()
    else:
        main_app_ui()