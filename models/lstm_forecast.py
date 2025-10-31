# -*- coding: utf-8 -*-
"""
LSTM Model for Time-Series Forecasting of Import Quantities
Predicts future import quantities based on historical data
"""
import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler
import pickle


class ImportForecastLSTM:
    """LSTM Model for Import Quantity Forecasting"""
    
    def __init__(self, lookback=30, features=5, model_path=None):
        """
        Initialize LSTM model
        
        Args:
            lookback: Number of past time steps to consider
            features: Number of features per time step
            model_path: Path to load pre-trained model
        """
        self.lookback = lookback
        self.features = features
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.build_model()
    
    def build_model(self):
        """Build LSTM architecture for time-series forecasting"""
        model = models.Sequential([
            # Input layer
            layers.Input(shape=(self.lookback, self.features)),
            
            # LSTM Layer 1
            layers.LSTM(128, return_sequences=True, activation='tanh'),
            layers.Dropout(0.2),
            layers.BatchNormalization(),
            
            # LSTM Layer 2
            layers.LSTM(64, return_sequences=True, activation='tanh'),
            layers.Dropout(0.2),
            layers.BatchNormalization(),
            
            # LSTM Layer 3
            layers.LSTM(32, return_sequences=False, activation='tanh'),
            layers.Dropout(0.2),
            
            # Dense layers
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            
            # Output layer (predicting single quantity value)
            layers.Dense(1, activation='linear')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae', 'mape']
        )
        
        self.model = model
        return model
    
    def prepare_sequences(self, data):
        """
        Prepare time-series sequences for LSTM
        
        Args:
            data: Array of shape (n_samples, n_features)
        
        Returns:
            X, y: Sequences and targets
        """
        X, y = [], []
        
        for i in range(len(data) - self.lookback):
            X.append(data[i:i + self.lookback])
            y.append(data[i + self.lookback, 0])  # Predict first feature (quantity)
        
        return np.array(X), np.array(y)
    
    def preprocess_data(self, df, fit_scaler=True):
        """
        Preprocess dataframe for LSTM
        
        Args:
            df: Pandas DataFrame with columns:
                - quantity: import quantity
                - price: unit price
                - sales: historical sales
                - stock: current stock level
                - demand: demand indicator
        
        Returns:
            Normalized array
        """
        # Select features
        feature_cols = ['quantity', 'price', 'sales', 'stock', 'demand']
        available_cols = [col for col in feature_cols if col in df.columns]
        
        if not available_cols:
            raise ValueError(f"DataFrame must contain at least one of {feature_cols}")
        
        data = df[available_cols].values
        
        # Normalize data
        if fit_scaler:
            normalized_data = self.scaler.fit_transform(data)
        else:
            normalized_data = self.scaler.transform(data)
        
        return normalized_data
    
    def predict_next_quantity(self, historical_data):
        """
        Predict next import quantity based on historical data
        
        Args:
            historical_data: DataFrame or dict with historical data
        
        Returns:
            Dictionary with prediction results
        """
        try:
            # Convert to DataFrame if dict
            if isinstance(historical_data, dict):
                df = pd.DataFrame(historical_data)
            else:
                df = historical_data.copy()
            
            # Ensure minimum data points
            if len(df) < self.lookback:
                # Pad with mean values if insufficient data
                mean_values = df.mean()
                padding_rows = self.lookback - len(df)
                padding_df = pd.DataFrame([mean_values] * padding_rows)
                df = pd.concat([padding_df, df], ignore_index=True)
            
            # Preprocess
            normalized_data = self.preprocess_data(df, fit_scaler=False)
            
            # Take last 'lookback' time steps
            X = normalized_data[-self.lookback:].reshape(1, self.lookback, -1)
            
            # Predict
            prediction_normalized = self.model.predict(X, verbose=0)[0][0]
            
            # Denormalize prediction
            # Create array with same shape as original features
            temp = np.zeros((1, normalized_data.shape[1]))
            temp[0, 0] = prediction_normalized
            prediction_denormalized = self.scaler.inverse_transform(temp)[0, 0]
            
            # Calculate confidence based on recent trend
            recent_quantities = df['quantity'].tail(5).values
            std_dev = np.std(recent_quantities)
            mean_val = np.mean(recent_quantities)
            
            # Confidence: higher when std_dev is lower relative to mean
            confidence = max(0.5, min(0.99, 1 - (std_dev / (mean_val + 1))))
            
            return {
                'success': True,
                'predicted_quantity': float(max(0, prediction_denormalized)),  # Ensure non-negative
                'confidence': float(confidence),
                'trend': 'increasing' if prediction_denormalized > mean_val else 'decreasing',
                'historical_mean': float(mean_val),
                'historical_std': float(std_dev)
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Prediction error: {str(e)}',
                'predicted_quantity': 0,
                'confidence': 0.0
            }
    
    def train(self, train_data, val_data, epochs=100, batch_size=32):
        """
        Train the LSTM model
        
        Args:
            train_data: Tuple of (X_train, y_train)
            val_data: Tuple of (X_val, y_val)
            epochs: Number of training epochs
            batch_size: Batch size
        
        Returns:
            Training history
        """
        if self.model is None:
            self.build_model()
        
        X_train, y_train = train_data
        X_val, y_val = val_data
        
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=7,
                min_lr=1e-7,
                verbose=1
            )
        ]
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def save_model(self, path='models/saved/lstm_forecast_model.h5'):
        """Save trained model and scaler"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save model
        self.model.save(path)
        
        # Save scaler
        scaler_path = path.replace('.h5', '_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        print(f"Model saved to {path}")
        print(f"Scaler saved to {scaler_path}")
    
    def load_model(self, path):
        """Load pre-trained model and scaler"""
        self.model = keras.models.load_model(path)
        
        # Load scaler
        scaler_path = path.replace('.h5', '_scaler.pkl')
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
        
        print(f"Model loaded from {path}")


def generate_sample_data(n_samples=500):
    """Generate sample time-series data for demonstration"""
    np.random.seed(42)
    
    # Generate time-based features
    dates = pd.date_range(start='2023-01-01', periods=n_samples, freq='D')
    
    # Simulate quantity with trend and seasonality
    trend = np.linspace(100, 200, n_samples)
    seasonality = 30 * np.sin(np.linspace(0, 8*np.pi, n_samples))
    noise = np.random.normal(0, 10, n_samples)
    quantity = trend + seasonality + noise
    
    # Generate related features
    price = 50 + np.random.normal(0, 5, n_samples)
    sales = quantity * 0.9 + np.random.normal(0, 10, n_samples)
    stock = quantity * 1.2 + np.random.normal(0, 15, n_samples)
    demand = sales / (stock + 1)  # Demand indicator
    
    df = pd.DataFrame({
        'date': dates,
        'quantity': np.maximum(0, quantity),
        'price': np.maximum(10, price),
        'sales': np.maximum(0, sales),
        'stock': np.maximum(0, stock),
        'demand': np.maximum(0, demand)
    })
    
    return df


if __name__ == "__main__":
    # Example usage
    print("LSTM Import Forecast Model initialized")
    model = ImportForecastLSTM(lookback=30, features=5)
    print(f"Model summary:")
    model.model.summary()
    
    # Generate sample data
    print("\nGenerating sample data...")
    sample_data = generate_sample_data(500)
    print(f"Sample data shape: {sample_data.shape}")
    print(sample_data.head())
