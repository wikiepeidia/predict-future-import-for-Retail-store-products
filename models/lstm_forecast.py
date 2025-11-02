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
            df: Pandas DataFrame with numeric features
                Can be either:
                - OLD format: quantity, price, sales, stock, demand
                - NEW format: quantity, price, total_amount, num_products, max_product_qty
        
        Returns:
            Normalized array
        """
        # 🔥 FIX: Select only NUMERIC columns, exclude strings like invoice_id, store_name
        if isinstance(df, pd.DataFrame):
            # Get only numeric columns
            numeric_df = df.select_dtypes(include=[np.number])
            
            # CRITICAL: Ensure we ALWAYS have exactly 5 features in the correct order
            expected_features = ['quantity', 'price', 'total_amount', 'num_products', 'max_product_qty']
            
            # Create a new DataFrame with exactly 5 columns
            result_df = pd.DataFrame()
            
            for feature in expected_features:
                if feature in numeric_df.columns:
                    result_df[feature] = numeric_df[feature]
                else:
                    # Fill missing features with calculated or default values
                    if feature == 'total_amount' and 'quantity' in numeric_df.columns and 'price' in numeric_df.columns:
                        result_df[feature] = numeric_df['quantity'] * numeric_df['price']
                    elif feature == 'num_products':
                        result_df[feature] = 1  # Default to 1 product
                    elif feature == 'max_product_qty' and 'quantity' in numeric_df.columns:
                        result_df[feature] = numeric_df['quantity']  # Use quantity as proxy
                    elif feature == 'quantity':
                        result_df[feature] = 100  # Default quantity
                    elif feature == 'price':
                        result_df[feature] = 50000  # Default price
                    else:
                        result_df[feature] = 0  # Last resort default
            
            data = result_df.values
        else:
            data = df
        
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
            historical_data: DataFrame, dict, or list of dicts with historical data
        
        Returns:
            Dictionary with prediction results
        """
        try:
            # Convert to DataFrame based on input type
            if isinstance(historical_data, list):
                # List of dictionaries
                if not historical_data:
                    return {'success': False, 'message': 'No historical data provided'}
                df = pd.DataFrame(historical_data)
            elif isinstance(historical_data, dict):
                # Single dictionary
                df = pd.DataFrame([historical_data])
            else:
                # Already a DataFrame
                df = historical_data.copy()
            
            # 🔥 CRITICAL: Ensure df has the 5 required features BEFORE padding
            # This creates missing columns with defaults
            required_features = ['quantity', 'price', 'total_amount', 'num_products', 'max_product_qty']
            for feature in required_features:
                if feature not in df.columns:
                    if feature == 'total_amount' and 'quantity' in df.columns and 'price' in df.columns:
                        df[feature] = df['quantity'] * df['price']
                    elif feature == 'num_products':
                        df[feature] = 1
                    elif feature == 'max_product_qty' and 'quantity' in df.columns:
                        df[feature] = df['quantity']
                    elif feature == 'quantity':
                        df[feature] = 100
                    elif feature == 'price':
                        df[feature] = 50000
                    else:
                        df[feature] = 0
            
            # Ensure minimum data points
            if len(df) < self.lookback:
                # Pad with mean values if insufficient data
                mean_values = df.mean(numeric_only=True)
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
        """Save trained model weights and scaler"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save model weights only
        self.model.save_weights(path)
        
        # Save scaler
        scaler_path = path.replace('.h5', '_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        print(f"Model weights saved to {path}")
        print(f"Scaler saved to {scaler_path}")
    
    def load_model(self, path):
        """Load pre-trained model weights and scaler"""
        # Build model first
        self.build_model()
        # Load weights
        self.model.load_weights(path)
        
        # Load scaler
        scaler_path = path.replace('.h5', '_scaler.pkl')
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
        
        print(f"Model weights loaded from {path}")


def generate_sample_data(n_samples=500):
    """
    DEPRECATED: Old function using synthetic sine waves
    Use generate_invoice_based_data() instead for real invoice data
    """
    print("⚠️  WARNING: Using synthetic sine wave data (not realistic!)")
    print("   Consider using generate_invoice_based_data() instead")
    
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


def generate_invoice_based_data(invoice_json_path='data/invoices/train.json'):
    """
    🔥 IMPROVED: Generate time-series from ACTUAL invoice data
    This fixes the critical data mismatch issue!
    
    Args:
        invoice_json_path: Path to invoice JSON file (train/valid/test)
    
    Returns:
        DataFrame with daily aggregated invoice features
    """
    import json
    from datetime import datetime
    
    print(f"[*] Loading invoice data from: {invoice_json_path}")
    
    try:
        with open(invoice_json_path, 'r', encoding='utf-8') as f:
            invoices = json.load(f)
    except FileNotFoundError:
        print(f"[X] Invoice file not found: {invoice_json_path}")
        print("   Falling back to synthetic data...")
        return generate_sample_data()
    
    print(f"   Loaded {len(invoices)} invoices")
    
    # Extract features from each invoice
    records = []
    for inv in invoices:
        # Parse date
        date = datetime.fromisoformat(inv['date'])
        
        # Calculate totals
        total_quantity = sum(p['quantity'] for p in inv['products'])
        total_amount = inv['total_amount']
        num_products = len(inv['products'])
        avg_price = total_amount / total_quantity if total_quantity > 0 else 0
        
        # Get max quantity product (most important item)
        max_qty_product = max(inv['products'], key=lambda p: p['quantity'])
        
        records.append({
            'date': date,
            'quantity': total_quantity,
            'price': avg_price,
            'num_products': num_products,
            'total_amount': total_amount,
            'max_product_qty': max_qty_product['quantity'],
            'store_type': inv.get('store_type', 'unknown')
        })
    
    # Create DataFrame and sort by date
    df = pd.DataFrame(records)
    df = df.sort_values('date').reset_index(drop=True)
    
    # Group by date (in case multiple invoices per day)
    df_daily = df.groupby('date').agg({
        'quantity': 'sum',
        'price': 'mean',
        'num_products': 'sum',
        'total_amount': 'sum',
        'max_product_qty': 'max'
    }).reset_index()
    
    # Calculate demand indicator (quantity growth rate)
    df_daily['quantity_change'] = df_daily['quantity'].pct_change().fillna(0)
    
    # Add seasonal features
    df_daily['day_of_week'] = df_daily['date'].dt.dayofweek
    df_daily['is_weekend'] = (df_daily['day_of_week'] >= 5).astype(int)
    df_daily['month'] = df_daily['date'].dt.month
    
    print(f"[OK] Generated {len(df_daily)} daily records")
    print(f"   Date range: {df_daily['date'].min()} to {df_daily['date'].max()}")
    print(f"   Avg daily quantity: {df_daily['quantity'].mean():.1f}")
    print(f"   Features: {list(df_daily.columns)}")
    
    return df_daily


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
