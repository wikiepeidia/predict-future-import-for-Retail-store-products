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
from models.lstm_model import ImportForecastLSTM, generate_invoice_based_data




def train_cnn_model():
    """Train CNN model with invoice images from dataset_product.csv"""
    print("\n" + "="*60)
    print("Training CNN Model for Invoice OCR")
    print("="*60)
    
    # Step 1: Load images from the dataset structure
    print("\n1. Loading invoice images from dataset...")
    
    train_metadata = 'data/generated_invoices/train_metadata.json'
    valid_metadata = 'data/generated_invoices/valid_metadata.json'
    
    if not os.path.exists(train_metadata):
        print("    Training images not found! Please run:")
        print("      python data/generate_balanced_dataset.py")
        raise FileNotFoundError("Train images not found. Generate them first!")
    
    print(f"    Found training images: {train_metadata}")
    if os.path.exists(valid_metadata):
        print(f"    Found validation images: {valid_metadata}")
    
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
    print(f"   Optimizer: Adam (lr=0.01, clipnorm=1.0)")
    
    # Step 3: Load and preprocess images
    print("\n4. Loading training images from dataset...")
    import json
    from tensorflow.keras.preprocessing import image as keras_image
    
    # Load training metadata
    with open(train_metadata, 'r', encoding='utf-8') as f:
        train_data = json.load(f)
    
    print(f"   Loading {len(train_data)} training images from dataset_product.csv...")
    
    X_train = []
    y_features_train = []
    y_types_train = []
    
    # Store types for one-hot encoding
    store_types = list(set([d['store_name'] for d in train_data]))
    store_type_map = {name: idx for idx, name in enumerate(store_types)}
    
    print(f"   Detected {len(store_types)} store types")
    
    for i, data in enumerate(train_data):
        # Load image
        img = keras_image.load_img(data['image_path'], target_size=(model.img_height, model.img_width))
        img_array = keras_image.img_to_array(img) / 255.0  # Normalize
        X_train.append(img_array)
        
        # Create feature vector
        feature_vec = np.zeros(128)
        feature_vec[0] = min(data['total_amount'] / 1000000.0, 1.0)  # Normalize total
        feature_vec[1] = data['num_products'] / 20.0  # Normalize count
        y_features_train.append(feature_vec)
        
        # One-hot encode store type
        type_vec = np.zeros(10)
        store_idx = store_type_map[data['store_name']]
        type_vec[store_idx] = 1.0
        y_types_train.append(type_vec)
        
        if (i + 1) % 100 == 0:
            print(f"      Loaded {i + 1}/{len(train_data)} images...")
    
    X_train = np.array(X_train)
    y_features_train = np.array(y_features_train)
    y_types_train = np.array(y_types_train)
    
    print(f"    Training data ready: {X_train.shape}")
    
    # Load validation data if available
    X_val, y_features_val, y_types_val = None, None, None
    if os.path.exists(valid_metadata):
        print("\n   Loading validation images...")
        with open(valid_metadata, 'r', encoding='utf-8') as f:
            valid_data = json.load(f)
        
        print(f"   Loading {len(valid_data)} validation images...")
        
        X_val = []
        y_features_val = []
        y_types_val = []
        
        for i, data in enumerate(valid_data):
            img = keras_image.load_img(data['image_path'], target_size=(model.img_height, model.img_width))
            img_array = keras_image.img_to_array(img) / 255.0
            X_val.append(img_array)
            
            feature_vec = np.zeros(128)
            feature_vec[0] = min(data['total_amount'] / 1000000.0, 1.0)
            feature_vec[1] = data['num_products'] / 20.0
            y_features_val.append(feature_vec)
            
            type_vec = np.zeros(10)
            store_idx = store_type_map.get(data['store_name'], 0)
            type_vec[store_idx] = 1.0
            y_types_val.append(type_vec)
        
        X_val = np.array(X_val)
        y_features_val = np.array(y_features_val)
        y_types_val = np.array(y_types_val)
        print(f"   ✅ Validation data ready: {X_val.shape}")
    
    # Step 4: Train model (48 epochs with batch size 12)
    print("\n5. Training model (48 epochs with batch size 12)...")
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6)
    ]
    
    # Use validation data if available, otherwise use validation_split
    if X_val is not None:
        history = model.model.fit(
            X_train,
            {'invoice_features': y_features_train, 'invoice_type': y_types_train},
            validation_data=(X_val, {'invoice_features': y_features_val, 'invoice_type': y_types_val}),
            epochs=80,  # Increased from 48 to 80 for better convergence
            batch_size=12,
            callbacks=callbacks,
            verbose=1
        )
    else:
        history = model.model.fit(
            X_train,
            {'invoice_features': y_features_train, 'invoice_type': y_types_train},
            epochs=80,  # Increased from 48 to 80 for better convergence
            batch_size=12,
            validation_split=0.2,
            callbacks=callbacks,
            verbose=1
        )
    
    print(f"    Training complete!")
    
    # Step 5: Save model
    print("\n6. Saving model...")
    save_path = 'saved_models/cnn_invoice_detector.weights.h5'
    os.makedirs('saved_models', exist_ok=True)
    model.save_model(save_path)
    print(f"   Saved to: {save_path}")
    
    # Save training history for evaluation
    import json
    history_dict = {k: [float(v) for v in history.history[k]] for k in history.history.keys()}
    with open('saved_models/cnn_training_history.json', 'w') as f:
        json.dump(history_dict, f, indent=2)
    print(f"   Training history saved for evaluation")
    
    print("\n" + "="*60)
    print("CNN Model Training Complete!")
    print("="*60)
    print(f"\nModel trained on {len(X_train)} synthetic invoice images")
    print(f"From dataset_product.csv (single unified dataset)")
    
    return model, history


def main():
    """Main training pipeline"""
    print("\n")
    print("=" + "="*58 + "=")
    print(" "*10 + "DEEP LEARNING MODEL TRAINING" + " "*20)
    print(" "*10 + "Retail Management" + " "*21)
    print("=" + "="*58 + "=")
    print("\n")
    
    # Create directory
    os.makedirs('saved_models', exist_ok=True)
    
    try:
        
        
        # Train CNN model (with generated images from dataset_product.csv)
        print("\n[CNN] Training invoice detection model...")
        cnn_model, cnn_history = train_cnn_model()
        
        print("\n" + "="*60)
        print("[OK] CNN MODEL TRAINED SUCCESSFULLY!")
        print("="*60)
        
        print("\n CNN Model:")
        print("   - Trained on synthetic invoice images")
        print("   - Generated from dataset_product.csv")
        print("   - Date range: October 1-November 1, 2025")
        print("   - Saved to: saved_models/cnn_invoice_detector.weights.h5")
        
        
        
    except Exception as e:
        print(f"\n[X] Error during training: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
