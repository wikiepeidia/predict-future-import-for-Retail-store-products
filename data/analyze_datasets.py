# -*- coding: utf-8 -*-
"""
Quick analysis to determine best approach for LSTM training
"""
import pandas as pd
import numpy as np

print("="*70)
print("DATASET ANALYSIS - Determining Best Training Approach")
print("="*70)

# Load datasets
print("\n1. Loading datasets...")
quantung = pd.read_csv('data/QUANTUNG.csv')
quanson = pd.read_csv('data/QUANSON.csv')

print(f"\n✅ QUANTUNG: {len(quantung)} products")
print(f"   Columns: {list(quantung.columns)}")
print(f"   Sample data types: {quantung.dtypes.to_dict()}")

print(f"\n✅ QUANSON: {len(quanson)} products")
print(f"   Columns: {list(quanson.columns)}")
print(f"   Sample data types: {quanson.dtypes.to_dict()}")

# Check product overlap
print("\n" + "="*70)
print("2. PRODUCT OVERLAP ANALYSIS")
print("="*70)

# Use product name or SKU for matching
quantung_products = set(quantung['Mã SKU'].dropna())
quanson_products = set(quanson['Mã SKU'].dropna())

overlap = quantung_products & quanson_products
only_quantung = quantung_products - quanson_products
only_quanson = quanson_products - quantung_products

overlap_percentage = (len(overlap) / max(len(quantung_products), len(quanson_products))) * 100

print(f"\n📊 Overlap Statistics:")
print(f"   QUANTUNG unique products: {len(quantung_products)}")
print(f"   QUANSON unique products: {len(quanson_products)}")
print(f"   Common products (overlap): {len(overlap)}")
print(f"   Only in QUANTUNG: {len(only_quantung)}")
print(f"   Only in QUANSON: {len(only_quanson)}")
print(f"   Overlap percentage: {overlap_percentage:.1f}%")

# Check numeric features
print("\n" + "="*70)
print("3. NUMERIC FEATURES ANALYSIS")
print("="*70)

# Clean and convert price columns
def clean_price(val):
    if pd.isna(val):
        return 0
    if isinstance(val, str):
        return float(val.replace('.', '').replace(',', ''))
    return float(val)

print("\n📈 QUANTUNG Features:")
quantung_clean = quantung.copy()
quantung_clean['LC_CN1_Tồn kho ban đầu'] = quantung_clean['LC_CN1_Tồn kho ban đầu'].apply(clean_price)
quantung_clean['PL_Giá bán lẻ'] = quantung_clean['PL_Giá bán lẻ'].apply(clean_price)
quantung_clean['PL_Giá nhập'] = quantung_clean['PL_Giá nhập'].apply(clean_price)

print(f"   - Quantity (Tồn kho): {quantung_clean['LC_CN1_Tồn kho ban đầu'].describe()}")
print(f"   - Retail Price: {quantung_clean['PL_Giá bán lẻ'].describe()}")
print(f"   - Import Price: {quantung_clean['PL_Giá nhập'].describe()}")

print("\n📈 QUANSON Features:")
quanson_clean = quanson.copy()
quanson_clean['LC_CN1_Tồn kho ban đầu'] = quanson_clean['LC_CN1_Tồn kho ban đầu'].apply(clean_price)
quanson_clean['PL_Giá bán lẻ'] = quanson_clean['PL_Giá bán lẻ'].apply(clean_price)
quanson_clean['PL_Giá nhập'] = quanson_clean['PL_Giá nhập'].apply(clean_price)

print(f"   - Quantity (Tồn kho): {quanson_clean['LC_CN1_Tồn kho ban đầu'].describe()}")
print(f"   - Retail Price: {quanson_clean['PL_Giá bán lẻ'].describe()}")
print(f"   - Import Price: {quanson_clean['PL_Giá nhập'].describe()}")

# Recommendation
print("\n" + "="*70)
print("4. RECOMMENDATION")
print("="*70)

if overlap_percentage >= 70:
    approach = "Option 2: MERGE DATASETS (Smart Data Alignment)"
    reason = f"High overlap ({overlap_percentage:.1f}%) allows effective merging"
    print(f"\n✅ {approach}")
    print(f"   Reason: {reason}")
    print(f"   Benefits:")
    print(f"   - Combine {len(quantung)} + {len(quanson)} = ~{len(quantung) + len(quanson)} records")
    print(f"   - Richer feature set (both warehouses)")
    print(f"   - Better pattern learning")
    print(f"\n   Implementation:")
    print(f"   1. Merge on common SKU codes ({len(overlap)} products)")
    print(f"   2. Create warehouse feature (QUANTUNG=0, QUANSON=1)")
    print(f"   3. Fill missing values with 0 or interpolation")
    print(f"   4. Train single LSTM on combined data")
    
elif overlap_percentage >= 30:
    approach = "Option 3: MULTI-INPUT LSTM (Most Powerful)"
    reason = f"Medium overlap ({overlap_percentage:.1f}%) - best with separate branches"
    print(f"\n✅ {approach}")
    print(f"   Reason: {reason}")
    print(f"   Benefits:")
    print(f"   - Use ALL data from both warehouses")
    print(f"   - Learn warehouse-specific patterns")
    print(f"   - Combine insights for better predictions")
    print(f"\n   Implementation:")
    print(f"   1. Train 2 LSTM branches (QUANTUNG + QUANSON)")
    print(f"   2. Concatenate features")
    print(f"   3. Final prediction layer combines both")
    
else:
    approach = "Option 1: SEPARATE MODELS"
    reason = f"Low overlap ({overlap_percentage:.1f}%) - treat as independent"
    print(f"\n✅ {approach}")
    print(f"   Reason: {reason}")
    print(f"   Benefits:")
    print(f"   - Specialized models for each warehouse")
    print(f"   - No data contamination")
    print(f"   - Ensemble prediction for robustness")
    print(f"\n   Implementation:")
    print(f"   1. Train model_quantung on {len(quantung)} products")
    print(f"   2. Train model_quanson on {len(quanson)} products")
    print(f"   3. Use weighted average for final prediction")

print("\n" + "="*70)
print("5. NEXT STEPS")
print("="*70)
print("\n📌 Waiting for HOADON.csv to:")
print("   - Analyze sales patterns")
print("   - Check product overlap with warehouses")
print("   - Determine final architecture")
print("\n📌 Current datasets ready for training!")
print(f"   - Total products: {len(quantung_products | quanson_products)}")
print(f"   - Total records: {len(quantung) + len(quanson)}")

print("\n" + "="*70)
