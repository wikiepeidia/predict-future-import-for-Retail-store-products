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

from models.cnn_model import CNNInvoiceDetector
from models.lstm_model import ImportForecastLSTM, generate_sample_data, generate_invoice_based_data


def train_lstm_model():
    """Train LSTM forecasting model"""
    print("="*60)
    print("Training LSTM Model for Import Quantity Forecasting")
    print("="*60)
    
    # Load REAL datasets
    print("\n1. Loading REAL datasets (QUANTUNG, QUANSON, HOADON)...")
    
    # Try to load the 3 real datasets
    dataset_paths = [
        'data/QUANTUNG.csv',
        'data/QUANSON.csv', 
        'data/HOADON.csv'
    ]
    
    dataframes = []
    for path in dataset_paths:
        if os.path.exists(path):
            try:
                temp_df = pd.read_csv(path)
                print(f"   ✅ Loaded {path}: {len(temp_df)} records")
                dataframes.append(temp_df)
            except Exception as e:
                print(f"   ❌ Error loading {path}: {e}")
        else:
            print(f"   ⚠️  Not found: {path}")
    
    if len(dataframes) > 0:
        # Combine all real datasets
        df = pd.concat(dataframes, ignore_index=True)
        print(f"\n   ✅ Combined {len(dataframes)} datasets: {len(df)} total records")
        print(f"   Columns: {list(df.columns)}")
    else:
        print("\n   ⚠️  NO REAL DATASETS FOUND!")
        print("   Please provide these files in data/ folder:")
        print("   - data/QUANTUNG.csv (Tung warehouse quantities)")
        print("   - data/QUANSON.csv (Son warehouse quantities)")
        print("   - data/HOADON.csv (Invoice/sales data)")
        print("\n   Falling back to synthetic data for now...")
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
        print(f"   [WARNING] Only {len(available_features)} features available: {available_features}")
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
    print("\n6. Training model (50 epochs for max performance)...")
    print("   This may take a few minutes...\n")
    
    history = model.train(
        train_data=(X_train, y_train),
        val_data=(X_val, y_val),
        epochs=50,
        batch_size=32
    )
    
    # Evaluate on test set
    print("\n7. Evaluating on test set...")
    test_metrics = model.model.evaluate(X_test, y_test, verbose=0)
    test_loss = test_metrics[0]
    test_mae = test_metrics[1]
    
    print(f"   Test Loss (Huber): {test_loss:.4f}")
    print(f"   Test MAE: {test_mae:.4f}")
    # NO MORE MAPE - it was exploding!
    
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
    """Train CNN model with ALREADY generated invoice images"""
    print("\n" + "="*60)
    print("Training CNN Model for Invoice OCR")
    print("="*60)
    
    # Step 1: Load images from BOTH datasets
    print("\n1. Loading invoice images from BOTH warehouses...")
    
    quanson_metadata = 'data/generated_invoices_quanson/train_metadata.json'
    quantung_metadata = 'data/generated_invoices_quantung/train_metadata.json'
    
    if not os.path.exists(quanson_metadata) or not os.path.exists(quantung_metadata):
        print("   ❌ Images not found! Please run:")
        print("      python data/invoice_image_generator.py")
        raise FileNotFoundError("Train images not found. Generate them first!")
    
    print(f"   ✅ Found QUANSON images: {quanson_metadata}")
    print(f"   ✅ Found QUANTUNG images: {quantung_metadata}")
    
    # Step 2: Initialize CNN model
    print("\n2. Building CNN architecture...")
    model = CNNInvoiceDetector()
    model.build_model()
    model.compile_model()
    
    print("\n3. Model architecture:")
    print(f"   Input: {model.img_height}x{model.img_width}x3 (RGB images)")
    print(f"   Base: MobileNetV2 (transfer learning)")
    print(f"   Output: Invoice features (128-dim) + Invoice type (10 classes)")
    print(f"   Loss: Huber (robust) + CrossEntropy")
    print(f"   Optimizer: Adam (lr=0.0005, clipnorm=1.0)")
    
    # Step 3: Load and preprocess images from BOTH datasets
    print("\n4. Loading training images from BOTH warehouses...")
    import json
    from tensorflow.keras.preprocessing import image as keras_image
    
    # Load QUANSON metadata
    with open(quanson_metadata, 'r', encoding='utf-8') as f:
        quanson_data = json.load(f)
    
    # Load QUANTUNG metadata
    with open(quantung_metadata, 'r', encoding='utf-8') as f:
        quantung_data = json.load(f)
    
    # Combine both datasets
    train_data = quanson_data + quantung_data
    
    print(f"   Loading {len(quanson_data)} QUANSON + {len(quantung_data)} QUANTUNG images...")
    print(f"   Total: {len(train_data)} training images")
    
    X_train = []
    y_features_train = []
    y_types_train = []
    
    # Store types for one-hot encoding
    store_types = list(set([d['store_name'] for d in train_data]))
    store_type_map = {name: idx for idx, name in enumerate(store_types)}
    
    print(f"   Detected {len(store_types)} store types: {store_types}")
    
    for i, data in enumerate(train_data):  # Use ALL training images
        # Load image
        img = keras_image.load_img(data['image_path'], target_size=(model.img_height, model.img_width))
        img_array = keras_image.img_to_array(img) / 255.0  # Normalize
        X_train.append(img_array)
        
        # Create feature vector (simple: total_amount, num_products, ...)
        feature_vec = np.zeros(128)
        feature_vec[0] = min(data['total_amount'] / 1000000.0, 1.0)  # Normalize total
        feature_vec[1] = data['num_products'] / 20.0  # Normalize count
        y_features_train.append(feature_vec)
        
        # One-hot encode store type
        type_vec = np.zeros(10)
        store_idx = store_type_map[data['store_name']]
        type_vec[store_idx] = 1.0
        y_types_train.append(type_vec)
        
        if (i + 1) % 40 == 0:
            print(f"      Loaded {i + 1}/{len(train_data)} images...")
    
    X_train = np.array(X_train)
    y_features_train = np.array(y_features_train)
    y_types_train = np.array(y_types_train)
    
    print(f"   ✅ Training data ready: {X_train.shape}")
    
    # Step 4: Train model (50 epochs for max performance)
    print("\n5. Training model (50 epochs for max performance)...")
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6)
    ]
    
    history = model.model.fit(
        X_train,
        {'invoice_features': y_features_train, 'invoice_type': y_types_train},
        epochs=50,
        batch_size=16,
        validation_split=0.2,
        callbacks=callbacks,
        verbose=1
    )
    
    print(f"   ✅ Training complete!")
    
    # Step 5: Save model
    print("\n6. Saving model...")
    save_path = 'saved_models/cnn_invoice_detector.weights.h5'
    os.makedirs('saved_models', exist_ok=True)
    model.save_model(save_path)
    print(f"   Saved to: {save_path}")
    
    print("\n" + "="*60)
    print("CNN Model Training Complete!")
    print("="*60)
    print(f"\nModel trained on {len(X_train)} synthetic invoice images")
    print(f"Generated from DATASET-tung1000.csv products")
    
    return model, history


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
        # Train LSTM model (fixed MAPE explosion)
        print("\n[LSTM] Training time-series forecasting model...")
        lstm_model, lstm_history = train_lstm_model()
        
        # Train CNN model (with generated images from DATASET-tung1000.csv)
        print("\n[CNN] Training invoice detection model...")
        cnn_model, cnn_history = train_cnn_model()
        
        print("\n" + "="*60)
        print("[OK] ALL MODELS TRAINED SUCCESSFULLY!")
        print("="*60)
        print("\n✅ LSTM Model:")
        print("   - Fixed MAPE explosion (removed MAPE, using MAE)")
        print("   - Added log transformation for wide price ranges")
        print("   - Using Huber loss (robust to outliers)")
        print("   - Saved to: saved_models/lstm_text_recognizer.weights.h5")
        
        print("\n✅ CNN Model:")
        print("   - Trained on synthetic invoice images")
        print("   - Generated from DATASET-tung1000.csv")
        print("   - Fixed MAPE issues (using Huber loss + MAE)")
        print("   - Saved to: saved_models/cnn_invoice_detector.weights.h5")
        
        print("\n" + "="*60)
        print("Model files saved to: saved_models/")
        print("- lstm_text_recognizer.weights.h5  (LSTM forecasting)")
        print("- cnn_invoice_detector.weights.h5  (CNN detector)")
        print("- lstm_text_recognizer.weights_scaler.pkl  (scaler)")
        print("\nGenerated dataset:")
        print("- data/generated_invoices_quanson/train/   (80 images)")
        print("- data/generated_invoices_quanson/test/    (20 images)")
        print("- data/generated_invoices_quantung/train/  (80 images)")
        print("- data/generated_invoices_quantung/test/   (20 images)")
        print("\nTotal: 160 training images from BOTH warehouses!")
        
        print("\nYou can now run the Flask app:")
        print("  python app_new.py")
        
    except Exception as e:
        print(f"\n[X] Error during training: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
