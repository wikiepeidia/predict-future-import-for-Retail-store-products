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
from models.lstm_forecast import ImportForecastLSTM, generate_sample_data, generate_invoice_based_data


def train_lstm_model():
    """Train LSTM forecasting model"""
    print("="*60)
    print("Training LSTM Model for Import Quantity Forecasting")
    print("="*60)
    
    # Generate sample data
    print("\n1. Loading REAL invoice data (not synthetic!)...")
    try:
        df = generate_invoice_based_data('data/invoices/train.json')
        print(f"   [OK] Loaded {len(df)} real invoice records")
    except Exception as e:
        print(f"   [!] Failed to load invoice data: {e}")
        print(f"   Falling back to synthetic data...")
        df = generate_sample_data(n_samples=500)
    
    print(f"   Columns: {list(df.columns)}")
    
    # Initialize model
    print("\n2. Initializing LSTM model...")
    model = ImportForecastLSTM(lookback=30, features=5)
    
    # Preprocess data - SELECT EXACTLY 5 FEATURES
    print("\n3. Preprocessing data...")
    # 🔥 FIX: Select the 5 most important features for forecasting
    feature_columns = ['quantity', 'price', 'total_amount', 'num_products', 'max_product_qty']
    
    # Check if we have all required columns
    available_features = [col for col in feature_columns if col in df.columns]
    
    if len(available_features) < 5:
        print(f"   ⚠️  Warning: Only {len(available_features)} features available: {available_features}")
        print(f"   Available columns: {list(df.columns)}")
        # Fallback: use whatever numeric columns we have
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        feature_columns = [col for col in numeric_cols if col != 'date'][:5]
        print(f"   Using fallback features: {feature_columns}")
    
    df_features = df[feature_columns]
    normalized_data = model.preprocess_data(df_features, fit_scaler=True)
    print(f"   Selected features: {feature_columns}")
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
    # Save ONLY to saved_models/ (used by collab.py)
    save_path = 'saved_models/lstm_text_recognizer.weights.h5'
    os.makedirs('saved_models', exist_ok=True)
    model.save_model(save_path)
    print(f"   Saved to: {save_path}")
    
    # Test prediction
    print("\n9. Testing prediction...")
    test_df = df.tail(50).drop('date', axis=1).copy()
    result = model.predict_next_quantity(test_df)
    
    if result['success']:
        print(f"   [OK] Predicted quantity: {result['predicted_quantity']:.2f}")
        print(f"   [OK] Confidence: {result['confidence']:.2%}")
        print(f"   [OK] Trend: {result['trend']}")
    else:
        print(f"   [X] Prediction failed: {result['message']}")
    
    print("\n" + "="*60)
    print("LSTM Model Training Complete!")
    print("="*60)
    
    return model, history


def train_cnn_model():
    """Train CNN model (or just initialize for OCR)"""
    print("\n" + "="*60)
    print("Initializing CNN Model for Invoice OCR")
    print("="*60)
    
    print("\nNote: CNN model uses MobileNetV2 transfer learning + custom architecture")
    print("For full training, you would need a labeled dataset of invoice images.")
    
    # Initialize model
    print("\n1. Building CNN architecture...")
    model = InvoiceOCRModel()
    
    print("\n2. Model architecture:")
    model.model.summary()
    
    # Save initial model
    print("\n3. Saving initial model...")
    # Save ONLY to saved_models/ (used by collab.py)
    save_path = 'saved_models/cnn_invoice_detector.weights.h5'
    os.makedirs('saved_models', exist_ok=True)
    model.save_model(save_path)
    print(f"   Saved to: {save_path}")
    
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
    print("=" + "="*58 + "=")
    print(" "*10 + "DEEP LEARNING MODEL TRAINING" + " "*20)
    print(" "*10 + "Retail Inventory Management" + " "*21)
    print("=" + "="*58 + "=")
    print("\n")
    
    # Create directory
    os.makedirs('saved_models', exist_ok=True)
    
    try:
        # Train LSTM model
        lstm_model, lstm_history = train_lstm_model()
        
        # Initialize CNN model
        cnn_model = train_cnn_model()
        
        print("\n" + "="*60)
        print("[OK] ALL MODELS READY!")
        print("="*60)
        print("\nModel files saved to: saved_models/")
        print("- lstm_text_recognizer.weights.h5  (LSTM forecasting model)")
        print("- cnn_invoice_detector.weights.h5  (CNN invoice detector)")
        print("- lstm_text_recognizer_scaler.pkl  (data scaler)")
        print("- cnn_invoice_detector.h5  (CNN OCR model)")
        
        print("\nYou can now run the Flask app with:")
        print("  python app.py")
        print("  python collab.py  (for Google Colab)")
        
    except Exception as e:
        print(f"\n[X] Error during training: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
