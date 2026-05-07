import tensorflow as tf
import numpy as np
import pandas as pd
import os
import joblib
from datetime import timedelta

# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

class Predictor:
    def __init__(self):
        self.model_dir = "data/model"
        # UPDATED: Using .keras instead of .h5 for better stability
        self.model_path = os.path.join(self.model_dir, "lstm_model.keras") 
        self.scaler_path = os.path.join(self.model_dir, "scaler.pkl")
        self.model = None
        self.scaler = None
        self.look_back = 60

    def load_model(self):
        """Loads the pre-trained multimodal model and scaler."""
        if self.model is None and os.path.exists(self.model_path):
            try:
                # FIX: compile=False skips the problematic "mse" deserialization
                self.model = tf.keras.models.load_model(self.model_path, compile=False)
                print("Model loaded successfully.")
            except Exception as e:
                print(f"Error loading model: {e}")
        
        if self.scaler is None and os.path.exists(self.scaler_path):
            self.scaler = joblib.load(self.scaler_path)

    def predict_prices(self, ticker, df, feature_engineer, num_predictions=3):
        self.load_model()
        if self.model is None or self.scaler is None:
            return pd.DataFrame()

        try:
            matrix = feature_engineer.build_intelligence_matrix(ticker, df)
            if len(matrix) < self.look_back:
                return pd.DataFrame()

            scaled_data = self.scaler.transform(matrix.values[-self.look_back:])
            current_batch = scaled_data.reshape(1, self.look_back, scaled_data.shape[1])
            
            predictions = []
            for _ in range(num_predictions):
                next_pred = self.model.predict(current_batch, verbose=0)
                predictions.append(next_pred[0])
                
                new_row = scaled_data[-1].copy() 
                new_row[0] = next_pred[0, 0] # Predicted Open
                new_row[3] = next_pred[0, 1] # Predicted Close
                
                new_row_reshaped = new_row.reshape(1, 1, scaled_data.shape[1])
                current_batch = np.append(current_batch[:, 1:, :], new_row_reshaped, axis=1)

            dummy = np.zeros((num_predictions, scaled_data.shape[1]))
            dummy[:, 0] = [p[0] for p in predictions]
            dummy[:, 3] = [p[1] for p in predictions]
            
            real_preds = self.scaler.inverse_transform(dummy)

            last_date = df.index[-1]
            future_dates = []
            while len(future_dates) < num_predictions:
                last_date += timedelta(days=1)
                if last_date.weekday() < 5: future_dates.append(last_date)

            preds_df = pd.DataFrame({
                'Predicted Open': real_preds[:, 0],
                'Predicted Close': real_preds[:, 3]
            }, index=future_dates)

            avg_swing = (df['High'].tail(14) - df['Low'].tail(14)).mean()
            preds_df['Predicted High'] = preds_df[['Predicted Open', 'Predicted Close']].max(axis=1) + (avg_swing * 0.5)
            preds_df['Predicted Low'] = preds_df[['Predicted Open', 'Predicted Close']].min(axis=1) - (avg_swing * 0.5)

            return preds_df[['Predicted Open', 'Predicted High', 'Predicted Low', 'Predicted Close']]

        except Exception as e:
            print(f"Prediction Error: {e}")
            return pd.DataFrame()