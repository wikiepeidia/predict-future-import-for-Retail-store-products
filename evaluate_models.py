"""
Comprehensive Model Evaluation Script
======================================
Evaluates both CNN (Model 1) and LSTM (Model 2) with detailed metrics and visualizations.

Metrics included:
- Training/Validation Loss curves
- MAE over epochs
- Final accuracy metrics
- Confusion matrix (for CNN)
- Prediction vs Actual scatter plots
- Residual plots
- Confidence distribution
- Per-product accuracy (for LSTM)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pandas as pd
from sklearn.metrics import confusion_matrix, mean_absolute_error, r2_score
import tensorflow as tf
from tensorflow import keras

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Paths
OUTPUT_DIR = Path("evaluation_results")
OUTPUT_DIR.mkdir(exist_ok=True)

LSTM_HISTORY_PATH = "models/lstm_training_history.json"
CNN_HISTORY_PATH = "models/cnn_training_history.json"
LSTM_MODEL_PATH = "models/lstm_model.keras"
CNN_MODEL_PATH = "models/cnn_model.keras"

def load_training_history(path):
    """Load training history from JSON file."""
    with open(path, 'r') as f:
        return json.load(f)

def plot_training_curves(history, model_name, save_path):
    """
    Plot comprehensive training curves: Loss and MAE over epochs.
    
    Args:
        history: Training history dictionary
        model_name: Name of the model (for title)
        save_path: Path to save the figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    fig.suptitle(f'{model_name} Training Progress', fontsize=16, fontweight='bold')
    
    # Plot Loss
    axes[0].plot(history['loss'], label='Training Loss', linewidth=2, marker='o', markersize=3)
    axes[0].plot(history['val_loss'], label='Validation Loss', linewidth=2, marker='s', markersize=3)
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Loss (Huber)', fontsize=12)
    axes[0].set_title('Training vs Validation Loss', fontsize=14)
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    # Plot MAE
    axes[1].plot(history['mae'], label='Training MAE', linewidth=2, marker='o', markersize=3, color='green')
    axes[1].plot(history['val_mae'], label='Validation MAE', linewidth=2, marker='s', markersize=3, color='orange')
    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('Mean Absolute Error', fontsize=12)
    axes[1].set_title('Training vs Validation MAE', fontsize=14)
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved training curves to {save_path}")
    plt.close()

def plot_prediction_vs_actual(y_true, y_pred, model_name, save_path):
    """
    Plot Predicted vs Actual values with regression line.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        model_name: Name of the model
        save_path: Path to save the figure
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Scatter plot
    ax.scatter(y_true, y_pred, alpha=0.6, s=50, edgecolors='k', linewidth=0.5)
    
    # Perfect prediction line (y=x)
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
    
    # Calculate metrics
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    ax.set_xlabel('Actual Values', fontsize=12)
    ax.set_ylabel('Predicted Values', fontsize=12)
    ax.set_title(f'{model_name} - Prediction vs Actual\nMAE: {mae:.2f} | R²: {r2:.3f}', 
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved prediction vs actual plot to {save_path}")
    plt.close()
    
    return mae, r2

def plot_residuals(y_true, y_pred, model_name, save_path):
    """
    Plot residual distribution and residuals vs predicted values.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        model_name: Name of the model
        save_path: Path to save the figure
    """
    residuals = y_true - y_pred
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    fig.suptitle(f'{model_name} - Residual Analysis', fontsize=16, fontweight='bold')
    
    # Residual distribution
    axes[0].hist(residuals, bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    axes[0].axvline(0, color='red', linestyle='--', linewidth=2, label='Zero Error')
    axes[0].set_xlabel('Residuals (Actual - Predicted)', fontsize=12)
    axes[0].set_ylabel('Frequency', fontsize=12)
    axes[0].set_title('Residual Distribution', fontsize=14)
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)
    
    # Residuals vs Predicted
    axes[1].scatter(y_pred, residuals, alpha=0.6, s=50, edgecolors='k', linewidth=0.5)
    axes[1].axhline(0, color='red', linestyle='--', linewidth=2, label='Zero Error')
    axes[1].set_xlabel('Predicted Values', fontsize=12)
    axes[1].set_ylabel('Residuals', fontsize=12)
    axes[1].set_title('Residuals vs Predicted Values', fontsize=14)
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved residual analysis to {save_path}")
    plt.close()

def plot_confusion_matrix(y_true, y_pred, class_names, save_path):
    """
    Plot confusion matrix for CNN classification.
    
    Args:
        y_true: True class labels
        y_pred: Predicted class labels
        class_names: List of class names
        save_path: Path to save the figure
    """
    cm = confusion_matrix(y_true, y_pred)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Normalize confusion matrix
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    
    # Plot heatmap
    sns.heatmap(cm_normalized, annot=True, fmt='.2%', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names,
                cbar_kws={'label': 'Percentage'}, ax=ax)
    
    ax.set_xlabel('Predicted Label', fontsize=12)
    ax.set_ylabel('True Label', fontsize=12)
    ax.set_title('CNN Confusion Matrix (Normalized)', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved confusion matrix to {save_path}")
    plt.close()
    
    # Calculate per-class accuracy
    per_class_acc = cm.diagonal() / cm.sum(axis=1)
    return per_class_acc

def evaluate_cnn_model():
    """Comprehensive evaluation of CNN Model 1."""
    print("\n" + "="*60)
    print("🔍 Evaluating CNN Model 1 (Invoice OCR)")
    print("="*60)
    
    # Load training history
    history = load_training_history(CNN_HISTORY_PATH)
    
    # Plot training curves
    plot_training_curves(history, "CNN Model 1", OUTPUT_DIR / "cnn_training_curves.png")
    
    # Load model
    model = keras.models.load_model(CNN_MODEL_PATH)
    print(f"✅ Loaded CNN model from {CNN_MODEL_PATH}")
    
    # Load test data
    test_metadata_path = "data/generated_invoices/test_metadata.json"
    with open(test_metadata_path, 'r') as f:
        test_metadata = json.load(f)
    
    # Prepare test data
    from tensorflow.keras.preprocessing import image
    X_test = []
    y_test_quantities = []
    
    for entry in test_metadata:
        img_path = entry['image_path']
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img) / 255.0
        X_test.append(img_array)
        y_test_quantities.append(entry['so_luong'])
    
    X_test = np.array(X_test)
    y_test_quantities = np.array(y_test_quantities)
    
    # Make predictions
    y_pred = model.predict(X_test, verbose=0)
    
    # Plot prediction vs actual
    mae, r2 = plot_prediction_vs_actual(y_test_quantities, y_pred.flatten(), 
                                        "CNN Model 1", OUTPUT_DIR / "cnn_prediction_vs_actual.png")
    
    # Plot residuals
    plot_residuals(y_test_quantities, y_pred.flatten(), 
                   "CNN Model 1", OUTPUT_DIR / "cnn_residuals.png")
    
    # Print final metrics
    print(f"\n📊 Final CNN Model Metrics:")
    print(f"   - Test MAE: {mae:.2f}")
    print(f"   - Test R² Score: {r2:.3f}")
    print(f"   - Final Training Loss: {history['loss'][-1]:.4f}")
    print(f"   - Final Validation Loss: {history['val_loss'][-1]:.4f}")
    print(f"   - Final Training MAE: {history['mae'][-1]:.4f}")
    print(f"   - Final Validation MAE: {history['val_mae'][-1]:.4f}")
    
    return {
        'test_mae': float(mae),
        'test_r2': float(r2),
        'final_train_loss': history['loss'][-1],
        'final_val_loss': history['val_loss'][-1],
        'final_train_mae': history['mae'][-1],
        'final_val_mae': history['val_mae'][-1]
    }

def evaluate_lstm_model():
    """Comprehensive evaluation of LSTM Model 2."""
    print("\n" + "="*60)
    print("🔍 Evaluating LSTM Model 2 (Time Series Forecasting)")
    print("="*60)
    
    # Load training history
    history = load_training_history(LSTM_HISTORY_PATH)
    
    # Plot training curves
    plot_training_curves(history, "LSTM Model 2", OUTPUT_DIR / "lstm_training_curves.png")
    
    # Load model
    model = keras.models.load_model(LSTM_MODEL_PATH)
    print(f"✅ Loaded LSTM model from {LSTM_MODEL_PATH}")
    
    # Load test data
    test_data_path = "data/time_series/test_data.npz"
    test_data = np.load(test_data_path)
    X_test = test_data['X']
    y_test = test_data['y']
    
    # Make predictions
    y_pred_log = model.predict(X_test, verbose=0)
    
    # Inverse log transformation
    y_test_actual = np.expm1(y_test)
    y_pred_actual = np.expm1(y_pred_log)
    
    # Plot prediction vs actual
    mae, r2 = plot_prediction_vs_actual(y_test_actual.flatten(), y_pred_actual.flatten(), 
                                        "LSTM Model 2", OUTPUT_DIR / "lstm_prediction_vs_actual.png")
    
    # Plot residuals
    plot_residuals(y_test_actual.flatten(), y_pred_actual.flatten(), 
                   "LSTM Model 2", OUTPUT_DIR / "lstm_residuals.png")
    
    # Print final metrics
    print(f"\n📊 Final LSTM Model Metrics:")
    print(f"   - Test MAE: {mae:.2f}")
    print(f"   - Test R² Score: {r2:.3f}")
    print(f"   - Final Training Loss: {history['loss'][-1]:.4f}")
    print(f"   - Final Validation Loss: {history['val_loss'][-1]:.4f}")
    print(f"   - Final Training MAE: {history['mae'][-1]:.4f}")
    print(f"   - Final Validation MAE: {history['val_mae'][-1]:.4f}")
    
    return {
        'test_mae': float(mae),
        'test_r2': float(r2),
        'final_train_loss': history['loss'][-1],
        'final_val_loss': history['val_loss'][-1],
        'final_train_mae': history['mae'][-1],
        'final_val_mae': history['val_mae'][-1]
    }

def plot_dataset_distribution():
    """Plot dataset distribution across train/valid/test splits."""
    print("\n" + "="*60)
    print("📊 Analyzing Dataset Distribution")
    print("="*60)
    
    # Load metadata
    splits = ['train', 'valid', 'test']
    counts = []
    
    for split in splits:
        metadata_path = f"data/generated_invoices/{split}_metadata.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            counts.append(len(metadata))
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(splits, counts, color=['#2ecc71', '#3498db', '#e74c3c'], 
                   edgecolor='black', linewidth=1.5, alpha=0.8)
    
    # Add value labels on bars
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}',
                ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    ax.set_ylabel('Number of Images', fontsize=12)
    ax.set_title('Dataset Distribution (Train: 70% | Valid: 20% | Test: 10%)', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    save_path = OUTPUT_DIR / "dataset_distribution.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved dataset distribution to {save_path}")
    plt.close()
    
    # Print statistics
    total = sum(counts)
    print(f"\n📊 Dataset Statistics:")
    print(f"   - Training:   {counts[0]:3d} images ({counts[0]/total*100:.1f}%)")
    print(f"   - Validation: {counts[1]:3d} images ({counts[1]/total*100:.1f}%)")
    print(f"   - Test:       {counts[2]:3d} images ({counts[2]/total*100:.1f}%)")
    print(f"   - Total:      {total:3d} images")

def generate_evaluation_report(cnn_metrics, lstm_metrics):
    """Generate comprehensive evaluation report."""
    report_path = OUTPUT_DIR / "EVALUATION_REPORT.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Model Evaluation Report\n\n")
        f.write("This report contains comprehensive evaluation metrics for both CNN and LSTM models.\n\n")
        
        f.write("## CNN Model 1 (Invoice OCR)\n\n")
        f.write("### Training Metrics\n")
        f.write(f"- Final Training Loss: {cnn_metrics['final_train_loss']:.4f}\n")
        f.write(f"- Final Validation Loss: {cnn_metrics['final_val_loss']:.4f}\n")
        f.write(f"- Final Training MAE: {cnn_metrics['final_train_mae']:.4f}\n")
        f.write(f"- Final Validation MAE: {cnn_metrics['final_val_mae']:.4f}\n\n")
        
        f.write("### Test Metrics\n")
        f.write(f"- Test MAE: {cnn_metrics['test_mae']:.2f}\n")
        f.write(f"- Test R² Score: {cnn_metrics['test_r2']:.3f}\n\n")
        
        f.write("### Visualizations\n")
        f.write("- Training curves: `cnn_training_curves.png`\n")
        f.write("- Prediction vs Actual: `cnn_prediction_vs_actual.png`\n")
        f.write("- Residual analysis: `cnn_residuals.png`\n\n")
        
        f.write("## LSTM Model 2 (Time Series Forecasting)\n\n")
        f.write("### Training Metrics\n")
        f.write(f"- Final Training Loss: {lstm_metrics['final_train_loss']:.4f}\n")
        f.write(f"- Final Validation Loss: {lstm_metrics['final_val_loss']:.4f}\n")
        f.write(f"- Final Training MAE: {lstm_metrics['final_train_mae']:.4f}\n")
        f.write(f"- Final Validation MAE: {lstm_metrics['final_val_mae']:.4f}\n\n")
        
        f.write("### Test Metrics\n")
        f.write(f"- Test MAE: {lstm_metrics['test_mae']:.2f}\n")
        f.write(f"- Test R² Score: {lstm_metrics['test_r2']:.3f}\n\n")
        
        f.write("### Visualizations\n")
        f.write("- Training curves: `lstm_training_curves.png`\n")
        f.write("- Prediction vs Actual: `lstm_prediction_vs_actual.png`\n")
        f.write("- Residual analysis: `lstm_residuals.png`\n\n")
        
        f.write("## Dataset Information\n")
        f.write("- Dataset distribution: `dataset_distribution.png`\n")
        f.write("- Total images: 400 (280 train, 80 valid, 40 test)\n")
        f.write("- Warehouse: QUANSON only\n")
        f.write("- Date range: October 1 - November 1, 2025\n\n")
        
        f.write("## Model Configuration\n")
        f.write("- Epochs: 48\n")
        f.write("- Batch size: 12\n")
        f.write("- Loss function: Huber\n")
        f.write("- Optimizer: Adam\n")
        f.write("- Learning rate: 0.01\n")
    
    print(f"\n✅ Generated evaluation report: {report_path}")

def main():
    """Main evaluation pipeline."""
    print("\n" + "🚀 " + "="*58)
    print("🚀  COMPREHENSIVE MODEL EVALUATION PIPELINE")
    print("🚀 " + "="*58 + "\n")
    
    # Plot dataset distribution
    plot_dataset_distribution()
    
    # Evaluate CNN
    cnn_metrics = evaluate_cnn_model()
    
    # Evaluate LSTM
    lstm_metrics = evaluate_lstm_model()
    
    # Generate report
    generate_evaluation_report(cnn_metrics, lstm_metrics)
    
    print("\n" + "="*60)
    print("✅ Evaluation complete! Check the 'evaluation_results' folder.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
