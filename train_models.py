# -*- coding: utf-8 -*-
"""
Training Script for Deep Learning Models
Train both CNN and LSTM models
"""
import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.cnn_invoice_ocr import InvoiceOCRModel
from models.lstm_forecast import ImportForecastLSTM, generate_sample_data


def train_lstm_model():
    """Train LSTM forecasting model"""
    print("="*60)
    print("Training LSTM Model for Import Quantity Forecasting")
    print("="*60)
    
    # Generate sample data
    print("\n1. Generating sample time-series data...")
    df = generate_sample_data(n_samples=500)
    print(f"   Generated {len(df)} data points")
    print(f"   Columns: {list(df.columns)}")
    
    # Initialize model
    print("\n2. Initializing LSTM model...")
    model = ImportForecastLSTM(lookback=30, features=5)
    
    # Preprocess data
    print("\n3. Preprocessing data...")
    normalized_data = model.preprocess_data(df.drop('date', axis=1), fit_scaler=True)
    print(f"   Normalized data shape: {normalized_data.shape}")
    
    # Create sequences
    print("\n4. Creating time-series sequences...")
    X, y = model.prepare_sequences(normalized_data)
    print(f"   X shape: {X.shape}, y shape: {y.shape}")
    
    # Split data (70% train, 10% val, 20% test)
    print("\n5. Splitting data (70% train, 10% val, 20% test)...")
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, shuffle=False)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.67, shuffle=False)
    
    print(f"   Train: {X_train.shape[0]} samples")
    print(f"   Val:   {X_val.shape[0]} samples")
    print(f"   Test:  {X_test.shape[0]} samples")
    
    # Train model
    print("\n6. Training model...")
    print("   This may take a few minutes...\n")
    
    history = model.train(
        train_data=(X_train, y_train),
        val_data=(X_val, y_val),
        epochs=50,
        batch_size=32
    )
    
    # Evaluate on test set
    print("\n7. Evaluating on test set...")
    test_loss, test_mae, test_mape = model.model.evaluate(X_test, y_test, verbose=0)
    print(f"   Test Loss (MSE): {test_loss:.4f}")
    print(f"   Test MAE: {test_mae:.4f}")
    print(f"   Test MAPE: {test_mape:.2f}%")
    
    # Save model
    print("\n8. Saving model...")
    save_path = 'models/saved/lstm_forecast_model.h5'
    model.save_model(save_path)
    
    # Test prediction
    print("\n9. Testing prediction...")
    test_df = df.tail(50).drop('date', axis=1).copy()
    result = model.predict_next_quantity(test_df)
    
    if result['success']:
        print(f"   ✓ Predicted quantity: {result['predicted_quantity']:.2f}")
        print(f"   ✓ Confidence: {result['confidence']:.2%}")
        print(f"   ✓ Trend: {result['trend']}")
    else:
        print(f"   ✗ Prediction failed: {result['message']}")
    
    print("\n" + "="*60)
    print("LSTM Model Training Complete!")
    print("="*60)
    
    return model, history


def train_cnn_model():
    """Train CNN model (or just initialize for OCR)"""
    print("\n" + "="*60)
    print("Initializing CNN Model for Invoice OCR")
    print("="*60)
    
    print("\nNote: CNN model uses pre-trained Tesseract OCR + custom architecture")
    print("For full training, you would need a labeled dataset of invoice images.")
    
    # Initialize model
    print("\n1. Building CNN architecture...")
    model = InvoiceOCRModel()
    
    print("\n2. Model architecture:")
    model.model.summary()
    
    # Save initial model
    print("\n3. Saving initial model...")
    save_path = 'models/saved/cnn_invoice_model.h5'
    model.save_model(save_path)
    
    print("\n" + "="*60)
    print("CNN Model Initialized!")
    print("="*60)
    print("\nTo train the CNN model:")
    print("1. Collect labeled invoice images")
    print("2. Prepare training dataset")
    print("3. Use model.train(train_data, val_data)")
    
    return model


def main():
    """Main training pipeline"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "DEEP LEARNING MODEL TRAINING" + " "*20 + "║")
    print("║" + " "*10 + "Retail Inventory Management" + " "*21 + "║")
    print("╚" + "="*58 + "╝")
    print("\n")
    
    # Create directories
    os.makedirs('models/saved', exist_ok=True)
    
    try:
        # Train LSTM model
        lstm_model, lstm_history = train_lstm_model()
        
        # Initialize CNN model
        cnn_model = train_cnn_model()
        
        print("\n" + "="*60)
        print("✓ ALL MODELS READY!")
        print("="*60)
        print("\nModel files saved to: models/saved/")
        print("- lstm_forecast_model.h5")
        print("- lstm_forecast_model_scaler.pkl")
        print("- cnn_invoice_model.h5")
        
        print("\nYou can now run the Flask app with:")
        print("  python app.py")
        
    except Exception as e:
        print(f"\n✗ Error during training: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
