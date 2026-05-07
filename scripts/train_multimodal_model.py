import sys
import os
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping

# 1. FIX: Add Project Root to Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.data_fetcher import DataFetcher
from core.news_analyzer import NewsAnalyzer
from core.feature_engineer import FeatureEngineer

# --- Configuration ---
# A diverse list teaches the AI how different 'sectors' behave
TICKERS = ["AAPL", "MSFT", "NVDA", "JPM", "TSLA", "WMT", "XOM", "AMZN" , "ADANIENT.NS" , 'RELIANCE.NS'] 
LOOKBACK = 60
MODEL_DIR = "data/model"
os.makedirs(MODEL_DIR, exist_ok=True)

def train_multimodal():
    fetcher = DataFetcher()
    analyzer = NewsAnalyzer()
    engineer = FeatureEngineer(fetcher, analyzer)
    
    all_sequences = []
    all_targets = []
    global_matrix_list = []

    print(f"🚀 Phase 1: Gathering Market Intelligence from {len(TICKERS)} sectors...")
    
    for ticker in TICKERS:
        try:
            # Use 2 years to get enough 'cycles' of news and price swings
            df = fetcher.fetch_historical_data(ticker, period="2y")
            if df.empty or len(df) < LOOKBACK: continue
            
            matrix = engineer.build_intelligence_matrix(ticker, df)
            global_matrix_list.append(matrix)
            print(f"   ✅ Processed {ticker}")
        except Exception as e:
            print(f"   ❌ Failed {ticker}: {e}")

    # Create a Global Scaler based on the entire market basket
    full_df = pd.concat(global_matrix_list)
    scaler = StandardScaler()
    scaler.fit(full_df)
    
    # Convert each stock into AI-ready sequences
    for matrix in global_matrix_list:
        scaled_matrix = scaler.transform(matrix)
        for i in range(LOOKBACK, len(scaled_matrix)):
            all_sequences.append(scaled_matrix[i-LOOKBACK:i])
            # We predict Open (0) and Close (3)
            all_targets.append(scaled_matrix[i, [0, 3]])

    X, y = np.array(all_sequences), np.array(all_targets)
    
    print(f"🧠 Phase 2: Training Universal AI on {X.shape[0]} data points...")

    # Upgraded Architecture for better pattern recognition
    model = Sequential([
        Input(shape=(LOOKBACK, X.shape[2])),
        LSTM(128, return_sequences=True),
        Dropout(0.3),
        LSTM(64, return_sequences=False),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dense(16, activation='relu'),
        Dense(2) # Output: Predicted Open, Predicted Close
    ])

    model.compile(optimizer='adam', loss='mse')
    
    # Early stopping prevents the 'same value' bug by stopping when the AI stops learning
    early_stop = EarlyStopping(monitor='loss', patience=5, restore_best_weights=True)

    model.fit(X, y, epochs=30, batch_size=64, callbacks=[early_stop], verbose=1)

    # 3. Save the Universal Brain
    model.save(os.path.join(MODEL_DIR, "lstm_model.keras"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))
    
    print("\n✅ SUCCESS: Universal Multimodal Model is now live!")
    print("This model can now generalize to any ticker you search.")

if __name__ == "__main__":
    train_multimodal()