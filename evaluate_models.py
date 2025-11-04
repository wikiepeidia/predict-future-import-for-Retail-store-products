# -*- coding: utf-8 -*-
"""
Model Evaluation with Matplotlib Visualizations
Generate charts to evaluate LSTM and CNN model performance
"""
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

from pathlib import Path


def plot_lstm_training_history(history_path='saved_models/lstm_training_history.json'):
    """
    Plot LSTM training history (loss and MAE)
    
    Args:
        history_path: Path to saved training history JSON
    """
    if not os.path.exists(history_path):
        print(f"❌ History file not found: {history_path}")
        return
    
    print(f"\n📊 Plotting LSTM training history...")
    
    with open(history_path, 'r') as f:
        history = json.load(f)
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Plot 1: Loss
    ax1.plot(history['loss'], label='Training Loss', linewidth=2)
    ax1.plot(history['val_loss'], label='Validation Loss', linewidth=2)
    ax1.set_title('LSTM Model Loss (Huber)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Epoch', fontsize=12)
    ax1.set_ylabel('Loss', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: MAE
    ax2.plot(history['mae'], label='Training MAE', linewidth=2)
    ax2.plot(history['val_mae'], label='Validation MAE', linewidth=2)
    ax2.set_title('LSTM Model MAE', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Epoch', fontsize=12)
    ax2.set_ylabel('Mean Absolute Error', fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_path = 'evaluation/lstm_training_history.png'
    os.makedirs('evaluation', exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved to: {output_path}")
    plt.close()


def plot_cnn_training_history(history_path='saved_models/cnn_training_history.json'):
    """
    Plot CNN training history
    
    Args:
        history_path: Path to saved training history JSON
    """
    if not os.path.exists(history_path):
        print(f"❌ History file not found: {history_path}")
        return
    
    print(f"\n📊 Plotting CNN training history...")
    
    with open(history_path, 'r') as f:
        history = json.load(f)
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Plot 1: Total Loss
    ax1.plot(history['loss'], label='Training Loss', linewidth=2)
    ax1.plot(history['val_loss'], label='Validation Loss', linewidth=2)
    ax1.set_title('CNN Model Total Loss', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Epoch', fontsize=12)
    ax1.set_ylabel('Loss', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Feature Loss
    if 'invoice_features_loss' in history:
        ax2.plot(history['invoice_features_loss'], label='Training Feature Loss', linewidth=2)
        ax2.plot(history['val_invoice_features_loss'], label='Validation Feature Loss', linewidth=2)
        ax2.set_title('CNN Invoice Features Loss', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Epoch', fontsize=12)
        ax2.set_ylabel('Loss', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_path = 'evaluation/cnn_training_history.png'
    os.makedirs('evaluation', exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved to: {output_path}")
    plt.close()


def plot_dataset_distribution():
    """
    Plot dataset distribution (QUANSON vs QUANTUNG across train/valid/test)
    """
    print(f"\n📊 Plotting dataset distribution...")
    
    base_dir = Path('data/generated_invoices')
    
    # Count images by warehouse and split
    distribution = {
        'train': {'QUANSON': 0, 'QUANTUNG': 0},
        'valid': {'QUANSON': 0, 'QUANTUNG': 0},
        'test': {'QUANSON': 0, 'QUANTUNG': 0}
    }
    
    for split in ['train', 'valid', 'test']:
        metadata_path = base_dir / f"{split}_metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in data:
                warehouse = item.get('warehouse', 'UNKNOWN')
                if warehouse in distribution[split]:
                    distribution[split][warehouse] += 1
    
    # Create stacked bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    splits = list(distribution.keys())
    quanson_counts = [distribution[s]['QUANSON'] for s in splits]
    quantung_counts = [distribution[s]['QUANTUNG'] for s in splits]
    
    x = np.arange(len(splits))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, quanson_counts, width, label='QUANSON (Minimart)', color='#2E86AB')
    bars2 = ax.bar(x + width/2, quantung_counts, width, label='QUANTUNG (Souvenir)', color='#A23B72')
    
    ax.set_xlabel('Dataset Split', fontsize=12)
    ax.set_ylabel('Number of Images', fontsize=12)
    ax.set_title('Dataset Distribution:', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([s.capitalize() for s in splits])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    output_path = 'evaluation/dataset_distribution.png'
    os.makedirs('evaluation', exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved to: {output_path}")
    plt.close()


def plot_scenario_comparison():
    """
    Plot comparison of high demand (QUANSON) vs low demand (QUANTUNG) scenarios
    """
    print(f"\n📊 Plotting scenario comparison...")
    
    base_dir = Path('data/generated_invoices')
    train_metadata = base_dir / 'train_metadata.json'
    
    if not train_metadata.exists():
        print(f"   ⚠️  Training metadata not found")
        return
    
    with open(train_metadata, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Analyze by warehouse
    quanson_products = []
    quantung_products = []
    
    for item in data:
        if item.get('warehouse') == 'QUANSON':
            quanson_products.append(item['num_products'])
        elif item.get('warehouse') == 'QUANTUNG':
            quantung_products.append(item['num_products'])
    
    # Create comparison plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Histogram comparison
    ax1.hist(quanson_products, bins=15, alpha=0.7, label='QUANSON (Minimart)', color='#2E86AB', edgecolor='black')
    ax1.hist(quantung_products, bins=15, alpha=0.7, label='QUANTUNG (Souvenir)', color='#A23B72', edgecolor='black')
    ax1.set_xlabel('Number of Products per Invoice', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.set_title('Product Count Distribution', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Box plot comparison
    ax2.boxplot([quanson_products, quantung_products], 
                labels=['QUANSON\n(High Demand)', 'QUANTUNG\n(Low Demand)'],
                patch_artist=True,
                boxprops=dict(facecolor='lightblue', alpha=0.7),
                medianprops=dict(color='red', linewidth=2))
    ax2.set_ylabel('Number of Products per Invoice', fontsize=12)
    ax2.set_title('Scenario Comparison: Products per Invoice', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add statistics
    quanson_avg = np.mean(quanson_products)
    quantung_avg = np.mean(quantung_products)
    
    ax2.text(1, max(quanson_products) * 0.95, f'Avg: {quanson_avg:.1f}', 
            ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax2.text(2, max(quantung_products) * 0.95, f'Avg: {quantung_avg:.1f}', 
            ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    output_path = 'evaluation/scenario_comparison.png'
    os.makedirs('evaluation', exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"   ✅ Saved to: {output_path}")
    plt.close()


def generate_all_evaluations():
    """Generate all evaluation charts"""
    print("="*70)
    print("  MODEL EVALUATION - GENERATING CHARTS")
    print("="*70)
    
    plot_dataset_distribution()
    plot_scenario_comparison()
    plot_lstm_training_history()
    plot_cnn_training_history()
    
    print("\n" + "="*70)
    print("  EVALUATION COMPLETE!")
    print("="*70)
    print("\nGenerated charts:")
    print("  📊 evaluation/dataset_distribution.png")
    print("  📊 evaluation/scenario_comparison.png")
    print("  📊 evaluation/lstm_training_history.png")
    print("  📊 evaluation/cnn_training_history.png")
    print()


if __name__ == '__main__':
    generate_all_evaluations()
