# -*- coding: utf-8 -*-
"""
Fix QUANTUNG dataset - Calculate import prices from retail prices
Formula: Giá bán = Giá nhập + Giá nhập × 35%
        → Giá bán = Giá nhập × 1.35
        → Giá nhập = Giá bán / 1.35
"""
import pandas as pd
import numpy as np

def clean_price(val):
    """Convert price string to float"""
    if pd.isna(val):
        return 0
    if isinstance(val, str):
        # Remove dots and commas
        return float(val.replace('.', '').replace(',', ''))
    return float(val)

def round_to_thousands(value):
    """
    Round to nearest thousand and format with dots
    Examples:
    12283 -> 12.000
    13845 -> 14.000
    282948 -> 283.000
    """
    if value == 0:
        return 0
    
    # Round to nearest thousand
    rounded = round(value / 1000) * 1000
    
    return int(rounded)

def format_price(value):
    """
    Format price with dot separator for thousands
    12000 -> "12.000"
    283000 -> "283.000"
    """
    if value == 0:
        return 0
    
    # Format with thousand separator using dot
    formatted = f"{int(value):,}".replace(',', '.')
    return formatted

print("="*70)
print("FIXING QUANTUNG DATASET")
print("="*70)

# Load dataset
print("\n1. Loading QUANTUNG.csv...")
df = pd.read_csv('data/QUANTUNG.csv')
print(f"   ✅ Loaded {len(df)} products")

# Clean price columns
print("\n2. Cleaning price data...")
df['PL_Giá bán lẻ_clean'] = df['PL_Giá bán lẻ'].apply(clean_price)
df['PL_Giá nhập_clean'] = df['PL_Giá nhập'].apply(clean_price)

print(f"   ✅ Cleaned prices")
print(f"   Original import prices (all zeros): {df['PL_Giá nhập_clean'].sum()}")

# Calculate import price from retail price
print("\n3. Calculating import prices...")
print("   Formula: Giá nhập = Giá bán / 1.35")

# Giá bán = Giá nhập × 1.35
# → Giá nhập = Giá bán / 1.35
df['PL_Giá nhập_calculated'] = df['PL_Giá bán lẻ_clean'] / 1.35

print(f"   ✅ Calculated raw import prices")

# Round to nearest thousand
print("\n4. Rounding to nearest thousand...")
df['PL_Giá nhập_rounded'] = df['PL_Giá nhập_calculated'].apply(round_to_thousands)

# Show examples
print("\n   Examples:")
for i in range(min(10, len(df))):
    retail = df.iloc[i]['PL_Giá bán lẻ_clean']
    raw_import = df.iloc[i]['PL_Giá nhập_calculated']
    rounded_import = df.iloc[i]['PL_Giá nhập_rounded']
    product = df.iloc[i]['Tên sản phẩm'][:30]
    
    print(f"   {product:30s} | Retail: {retail:>10,.0f} | Import (raw): {raw_import:>10,.0f} | Import (rounded): {rounded_import:>10,.0f}")

# Format with dots
print("\n5. Formatting prices with dot separators...")
df['PL_Giá nhập'] = df['PL_Giá nhập_rounded'].apply(format_price)
df['PL_Giá bán lẻ'] = df['PL_Giá bán lẻ_clean'].apply(format_price)

# Drop temporary columns
df = df.drop(columns=['PL_Giá bán lẻ_clean', 'PL_Giá nhập_clean', 
                      'PL_Giá nhập_calculated', 'PL_Giá nhập_rounded'])

# Save fixed dataset
print("\n6. Saving fixed dataset...")
output_path = 'data/QUANTUNG_FIXED.csv'
df.to_csv(output_path, index=False, encoding='utf-8')

print(f"   ✅ Saved to: {output_path}")

# Verify
print("\n7. Verification:")
df_verify = pd.read_csv(output_path)
print(f"   Total products: {len(df_verify)}")
print(f"   Sample data:")
print(df_verify[['Tên sản phẩm', 'PL_Giá bán lẻ', 'PL_Giá nhập']].head(10))

# Statistics
print("\n8. Statistics:")
retail_prices = df_verify['PL_Giá bán lẻ'].apply(clean_price)
import_prices = df_verify['PL_Giá nhập'].apply(clean_price)

print(f"   Retail prices  - Min: {retail_prices.min():,.0f}, Max: {retail_prices.max():,.0f}, Avg: {retail_prices.mean():,.0f}")
print(f"   Import prices  - Min: {import_prices.min():,.0f}, Max: {import_prices.max():,.0f}, Avg: {import_prices.mean():,.0f}")

# Verify formula
margin = ((retail_prices - import_prices) / import_prices * 100).mean()
print(f"   Average margin: {margin:.1f}% (should be ~35%)")

print("\n" + "="*70)
print("✅ DATASET FIXED SUCCESSFULLY!")
print("="*70)
print(f"\n📁 Original: data/QUANTUNG.csv")
print(f"📁 Fixed:    {output_path}")
print(f"\nYou can now replace the original file with the fixed version:")
print(f"   mv {output_path} data/QUANTUNG.csv")
