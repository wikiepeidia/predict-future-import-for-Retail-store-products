"""
MODEL 2: LSTM - Text Recognition (Quantity Forecasting)
Input: Y1 (từ Model 1) + x2 (Hóa đơn nhập hàng) + x3 (Hóa đơn nhập hàng)
Output: Y2 TEXT - Dự đoán số lượng để tiếp

Architecture: LSTM for time-series forecasting using short-term memory
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class LSTMTextRecognizer:
    """
    LSTM Model for Text Recognition and Quantity Forecasting
    Uses historical invoice data to predict future import quantities
    """
    
    def __init__(self, sequence_length=10, num_features=5):
        """
        Args:
            sequence_length: Number of historical records to use (default: 10)
            num_features: Number of input features per record
        """
        self.sequence_length = sequence_length
        self.num_features = num_features
        self.model = None
        
    def build_model(self):
        """
        Build LSTM architecture for quantity forecasting
        Using stacked LSTM with attention mechanism
        """
        inputs = keras.Input(shape=(self.sequence_length, self.num_features))
        
        # First LSTM layer (returns sequences for stacking)
        x = layers.LSTM(128, return_sequences=True, name='lstm_1')(inputs)
        x = layers.Dropout(0.3)(x)
        
        # Second LSTM layer (returns sequences for attention)
        x = layers.LSTM(64, return_sequences=True, name='lstm_2')(x)
        x = layers.Dropout(0.2)(x)
        
        # Attention mechanism
        attention = layers.Dense(1, activation='tanh')(x)
        attention = layers.Flatten()(attention)
        attention = layers.Activation('softmax')(attention)
        attention = layers.RepeatVector(64)(attention)
        attention = layers.Permute([2, 1])(attention)
        
        # Apply attention
        x_attention = layers.Multiply()([x, attention])
        x_attention = layers.Lambda(lambda x: tf.reduce_sum(x, axis=1))(x_attention)
        
        # Dense layers for prediction
        x = layers.Dense(32, activation='relu')(x_attention)
        x = layers.Dropout(0.1)(x)
        
        # Output layer: Predicted quantity
        output = layers.Dense(1, activation='linear', name='quantity_prediction')(x)
        
        self.model = keras.Model(inputs=inputs, outputs=output)
        return self.model
    
    def compile_model(self):
        """Compile model with optimizer and loss"""
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae', 'mape']
        )
    
    def prepare_sequence_data(self, invoice_history):
        """
        Prepare sequential data for LSTM training
        Args:
            invoice_history: List of invoice dictionaries from Model 1 output
        Returns:
            X, y arrays for training
        """
        sequences = []
        targets = []
        
        # Sort by date
        sorted_history = sorted(invoice_history, key=lambda x: x.get('date', datetime.now()))
        
        # Create sliding windows
        for i in range(len(sorted_history) - self.sequence_length):
            # Extract features from sequence
            sequence = []
            for j in range(self.sequence_length):
                invoice = sorted_history[i + j]
                features = self._extract_features(invoice)
                sequence.append(features)
            
            # Target: next quantity
            target_invoice = sorted_history[i + self.sequence_length]
            target = self._get_total_quantity(target_invoice)
            
            sequences.append(sequence)
            targets.append(target)
        
        return np.array(sequences), np.array(targets)
    
    def _extract_features(self, invoice_data):
        """
        Extract features from invoice data (Y1 from Model 1)
        Returns: [total_quantity, total_amount, num_products, day_of_week, month]
        """
        total_quantity = self._get_total_quantity(invoice_data)
        total_amount = invoice_data.get('total_amount', 0)
        num_products = len(invoice_data.get('products', []))
        
        # Date features
        date = invoice_data.get('date', datetime.now())
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        day_of_week = date.weekday()  # 0-6
        month = date.month  # 1-12
        
        return [
            total_quantity / 1000.0,  # Normalized
            total_amount / 10000000.0,  # Normalized
            num_products / 10.0,  # Normalized
            day_of_week / 7.0,  # Normalized
            month / 12.0  # Normalized
        ]
    
    def _get_total_quantity(self, invoice_data):
        """Calculate total quantity from invoice"""
        products = invoice_data.get('products', [])
        return sum(p.get('quantity', 0) for p in products)
    
    def predict_quantity(self, recent_invoices):
        """
        Predict next import quantity based on recent invoices
        Y2 OUTPUT: TEXT prediction
        
        Args:
            recent_invoices: List of recent invoice data (Y1 from Model 1)
        Returns:
            Dictionary with prediction and recommendations
        """
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        # Prepare input sequence
        if len(recent_invoices) < self.sequence_length:
            # Pad with synthetic data if not enough history
            recent_invoices = self._pad_invoice_history(recent_invoices)
        
        # Take last sequence_length invoices
        recent_invoices = recent_invoices[-self.sequence_length:]
        
        # Extract features
        sequence = [self._extract_features(inv) for inv in recent_invoices]
        X = np.array([sequence])
        
        # Predict
        predicted_quantity = self.model.predict(X, verbose=0)[0][0]
        predicted_quantity = max(0, predicted_quantity * 1000)  # Denormalize and ensure positive
        
        # Generate recommendation text
        recommendation = self._generate_recommendation_text(
            predicted_quantity,
            recent_invoices
        )
        
        return {
            'predicted_quantity': int(predicted_quantity),
            'recommendation_text': recommendation,
            'confidence': self._calculate_confidence(recent_invoices),
            'historical_avg': self._calculate_avg_quantity(recent_invoices),
            'trend': self._analyze_trend(recent_invoices)
        }
    
    def _pad_invoice_history(self, invoices):
        """Pad invoice history with synthetic data if insufficient"""
        if not invoices:
            # Create dummy invoice
            invoices = [{
                'total_amount': 5000000,
                'products': [
                    {'quantity': 100, 'unit_price': 50000}
                ],
                'date': datetime.now() - timedelta(days=30)
            }]
        
        # Duplicate oldest invoice to fill sequence
        while len(invoices) < self.sequence_length:
            oldest = invoices[0].copy()
            oldest['date'] = oldest.get('date', datetime.now()) - timedelta(days=7)
            invoices.insert(0, oldest)
        
        return invoices
    
    def _generate_recommendation_text(self, predicted_qty, recent_invoices):
        """
        Generate Vietnamese recommendation text (Y2 TEXT)
        """
        avg_qty = self._calculate_avg_quantity(recent_invoices)
        trend = self._analyze_trend(recent_invoices)
        
        # Base recommendation
        text = f"Dự đoán số lượng nhập hàng kỳ tiếp: {int(predicted_qty)} sản phẩm\n\n"
        
        # Add trend analysis
        if trend == 'increasing':
            text += "📈 Xu hướng: TĂNG - Nhu cầu đang tăng lên theo thời gian\n"
            text += f"Khuyến nghị: Nên nhập nhiều hơn mức trung bình ({int(avg_qty)} sp)\n"
        elif trend == 'decreasing':
            text += "📉 Xu hướng: GIẢM - Nhu cầu đang giảm\n"
            text += f"Khuyến nghị: Cân nhắc giảm lượng nhập so với mức trung bình ({int(avg_qty)} sp)\n"
        else:
            text += "➡️ Xu hướng: ổn định\n"
            text += f"Khuyến nghị: Duy trì mức trung bình ({int(avg_qty)} sp)\n"
        
        # Add product breakdown
        if recent_invoices:
            latest = recent_invoices[-1]
            top_products = sorted(
                latest.get('products', []),
                key=lambda x: x.get('quantity', 0),
                reverse=True
            )[:3]
            
            if top_products:
                text += "\n🏆 Top sản phẩm cần nhập:\n"
                for i, prod in enumerate(top_products, 1):
                    text += f"{i}. {prod.get('product_name', 'Unknown')}: ~{prod.get('quantity', 0)} sp\n"
        
        return text
    
    def _calculate_confidence(self, invoices):
        """Calculate prediction confidence based on data quality"""
        if len(invoices) >= self.sequence_length:
            return 0.85 + (len(invoices) - self.sequence_length) * 0.01
        else:
            return 0.60 + len(invoices) * 0.02
    
    def _calculate_avg_quantity(self, invoices):
        """Calculate average quantity from invoice history"""
        if not invoices:
            return 0
        total = sum(self._get_total_quantity(inv) for inv in invoices)
        return total / len(invoices)
    
    def _analyze_trend(self, invoices):
        """Analyze trend from invoice history"""
        if len(invoices) < 3:
            return 'stable'
        
        quantities = [self._get_total_quantity(inv) for inv in invoices]
        
        # Simple linear regression
        x = np.arange(len(quantities))
        slope = np.polyfit(x, quantities, 1)[0]
        
        if slope > 10:
            return 'increasing'
        elif slope < -10:
            return 'decreasing'
        else:
            return 'stable'
    
    def save_model(self, path='saved_models/lstm_text_recognizer.h5'):
        """Save trained model"""
        if self.model:
            self.model.save(path)
            print(f"Model saved to {path}")
    
    def load_model(self, path='saved_models/lstm_text_recognizer.h5'):
        """Load trained model"""
        self.model = keras.models.load_model(path)
        print(f"Model loaded from {path}")


# Example usage
if __name__ == "__main__":
    # Initialize model
    lstm = LSTMTextRecognizer(sequence_length=10, num_features=5)
    lstm.build_model()
    lstm.compile_model()
    
    print("LSTM Model Summary:")
    lstm.model.summary()
    
    print("\nModel 2 (LSTM) ready for training!")
    print("Input: Y1 (từ Model 1) + x2 + x3 (Hóa đơn nhập hàng)")
    print("Output: Y2 TEXT - Dự đoán số lượng để tiếp")
