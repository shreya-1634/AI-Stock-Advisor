# your_project/tests/test_predictor.py

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from sklearn.preprocessing import MinMaxScaler
import os

from core.predictor import Predictor

# --- Fixtures ---

@pytest.fixture
def dummy_historical_df():
    """Provides a dummy DataFrame resembling historical stock data with Open and Close."""
    dates = pd.date_range(start='2023-01-01', periods=100)
    data = {
        'Open': np.linspace(100, 150, 100),
        'Close': np.linspace(100, 150, 100) + 2 # Close is slightly higher than Open
    }
    return pd.DataFrame(data, index=dates)

@pytest.fixture
def mock_keras_model():
    """Mocks a Keras Sequential model for multivariate predictions."""
    model = MagicMock()
    # Mocking a prediction output of 5 days, 2 features (Open, Close)
    model.predict.return_value = np.random.rand(1, 5, 2) 
    return model

@pytest.fixture
def mock_min_max_scaler():
    """Mocks a MinMaxScaler instance to handle 2D inputs."""
    scaler = MagicMock(spec=MinMaxScaler)
    # Mock fit_transform and transform for 2 features
    scaler.fit_transform.return_value = np.random.rand(100, 2)
    scaler.transform.return_value = np.random.rand(60, 2)
    # Mock inverse_transform to return dummy actual price data for 5 days
    scaler.inverse_transform.return_value = np.array([[120.0, 122.0]] * 5) 
    return scaler

@pytest.fixture
def predictor_instance(mock_keras_model, mock_min_max_scaler):
    """Initializes the Predictor with mocked model and scaler."""
    with patch('tensorflow.keras.models.load_model', return_value=mock_keras_model), \
         patch('sklearn.preprocessing.MinMaxScaler', return_value=mock_min_max_scaler), \
         patch('joblib.load', return_value=mock_min_max_scaler):
        
        predictor = Predictor()
        predictor.model = mock_keras_model
        predictor.scaler = mock_min_max_scaler
        yield predictor

# --- Test Cases ---

def test_preprocess_data_for_prediction(predictor_instance, dummy_historical_df, mock_min_max_scaler):
    """Tests if historical data is correctly reshaped for the LSTM/GAN model."""
    processed_data = predictor_instance.preprocess_data_for_prediction(dummy_historical_df)
    
    assert processed_data is not None
    # Ensure it returns: Batch size 1, 60 days lookback, 2 features (Open, Close)
    assert processed_data.shape == (1, predictor_instance.look_back, 2) 

def test_predict_prices_success(predictor_instance, dummy_historical_df, mock_keras_model, mock_min_max_scaler):
    """Tests successful price prediction when the model is properly loaded."""
    with patch.object(predictor_instance, 'preprocess_data_for_prediction', return_value=np.random.rand(1, predictor_instance.look_back, 2)):
        predicted_df = predictor_instance.predict_prices(dummy_historical_df, num_predictions=5)
        
        assert not predicted_df.empty
        assert len(predicted_df) == 5
        assert 'Predicted Open' in predicted_df.columns
        assert 'Predicted Close' in predicted_df.columns
        
        # Verify the mocked methods were actually called
        mock_keras_model.predict.assert_called() 
        mock_min_max_scaler.inverse_transform.assert_called()

def test_predict_prices_no_model(predictor_instance):
    """Tests the fallback placeholder logic if the .h5 model fails to load."""
    predictor_instance.model = None 
    
    # Provide exactly 5 days of data so the fallback logic can calculate recent changes
    dummy_short_df = pd.DataFrame(
        {'Open': [100, 101, 102, 103, 104], 'Close': [102, 103, 104, 105, 106]},
        index=pd.date_range(start='2023-01-01', periods=5)
    )
    
    predicted_df = predictor_instance.predict_prices(dummy_short_df, num_predictions=5)
    
    assert not predicted_df.empty
    assert len(predicted_df) == 5
    assert 'Predicted Open' in predicted_df.columns
    assert 'Predicted Close' in predicted_df.columns

def test_predict_prices_not_enough_data(predictor_instance):
    """Tests how the engine handles having almost no historical data."""
    predictor_instance.model = None
    
    # Provide only 3 days of data (fallback logic requires at least 5)
    short_df = pd.DataFrame(
        {'Open': np.random.rand(3), 'Close': np.random.rand(3)}, 
        index=pd.date_range(start='2023-01-01', periods=3)
    )
    predicted_df = predictor_instance.predict_prices(short_df)
    
    # Should safely return an empty DataFrame rather than crashing
    assert predicted_df.empty