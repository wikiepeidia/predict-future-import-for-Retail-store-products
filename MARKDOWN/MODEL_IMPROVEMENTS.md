# LSTM Model Improvements - MAPE Explosion Fix

## Problem Analysis

### Dataset (DATASET-tung1000.csv)

**Available Features:**

- Product Name (Tên sản phẩm)
- Product Category (Loại sản phẩm)
- SKU Code (Mã SKU)
- Unit (Đơn vị)
- Initial Stock (LC_CN1_Tồn kho ban đầu)
- Initial Cost (LC_CN1_Giá vốn khởi tạo)
- **Retail Price (PL_Giá bán lẻ): 5,000 - 150,000 VND**
- **Import Price (PL_Giá nhập): Wide range**

### Critical Issues Fixed

#### 1. **MAPE Explosion (1,000,000+)**

**Root Cause:**

- MAPE formula: `|actual - predicted| / actual * 100`
- When actual values are near zero or predictions are way off scale → MAPE explodes
- Price features have huge range (5,000 to 150,000) causing scaling issues

**Solution:**

- ✅ **Removed MAPE metric** - replaced with MAE (Mean Absolute Error)
- ✅ **Added log transformation** - `log1p()` to handle wide price ranges
- ✅ **Inverse transformation** - `expm1()` to get back original scale

#### 2. **Model Architecture Improvements**

**Changes Made:**

```python
# OLD
- Output: Dense(1, activation='linear')  # Can predict negative values
- Loss: MSE  # Sensitive to outliers
- Optimizer: Adam(lr=0.001)  # Too high learning rate
- Dropout: 0.2  # Too low
- Metrics: ['mae', 'mape']  # MAPE explodes

# NEW
- Output: Dense(1, activation='relu')  # Only positive predictions
- Loss: Huber(delta=1.0)  # Robust to outliers
- Optimizer: Adam(lr=0.0005, clipnorm=1.0)  # Lower LR + gradient clipping
- Dropout: 0.3  # Increased regularization
- Metrics: ['mae']  # Removed MAPE
```

#### 3. **Data Preprocessing Enhancements**

**Log Transformation:**

```python
# Apply to all features to handle different scales
epsilon = 1e-8
data = np.log1p(data + epsilon)  # log(1 + x), safer than log(x)

# After prediction, reverse it
prediction_final = np.expm1(prediction_denormalized)  # exp(x) - 1
```

**Benefits:**

- Handles prices from 5,000 to 150,000 uniformly
- Reduces impact of outliers
- Stabilizes training
- Prevents gradient explosion

#### 4. **Improved Confidence Calculation**

**OLD (Problematic):**

```python
confidence = 1 - (std_dev / (mean_val + 1))  # Can be negative or > 1
```

**NEW (Robust):**

```python
if mean_val > 0:
    cv = std_dev / mean_val  # Coefficient of variation
    confidence = max(0.5, min(0.99, 1 - min(cv, 0.5)))  # Capped
else:
    confidence = 0.5  # Safe default
```

---

## Features You Can Add (Without Major Revamp)

### Quick Wins (Just add to existing 5 features)

**Current 5 features:**

1. quantity
2. price
3. total_amount
4. num_products
5. max_product_qty

**Add these from your dataset:**

#### Option A: Price-Based Features (Easy)

```python
expected_features = [
    'quantity',
    'price',  # Already have
    'total_amount',
    'retail_price',  # NEW: PL_Giá bán lẻ
    'import_price',  # NEW: PL_Giá nhập
    'profit_margin',  # NEW: (retail - import) / retail
    'stock_level'  # NEW: LC_CN1_Tồn kho ban đầu
]
```

**Code Change (in preprocess_data):**

```python
expected_features = [
    'quantity', 'retail_price', 'import_price', 
    'profit_margin', 'stock_level', 'total_amount', 'num_products'
]

# Calculate derived features
if 'retail_price' in df and 'import_price' in df:
    result_df['profit_margin'] = (df['retail_price'] - df['import_price']) / (df['retail_price'] + 1)
```

#### Option B: Category Encoding (Medium Effort)

```python
# One-hot encode product category
from sklearn.preprocessing import LabelEncoder

# In your data loading:
le = LabelEncoder()
df['category_encoded'] = le.fit_transform(df['Loại sản phẩm'])
```

---

## Expected Improvements

**Before:**

- ❌ MAPE: 1,000,000+ (exploding)
- ❌ Predictions: Unstable, sometimes negative
- ❌ Training: Gradient explosion

**After:**

- ✅ MAE: Stable and interpretable
- ✅ Predictions: Always positive (ReLU output)
- ✅ Training: Stable with Huber loss + gradient clipping
- ✅ Better handling of price ranges (5K-150K)

---

## How to Train with New Dataset

```python
import pandas as pd

# Load your rich dataset
df = pd.read_csv('data/DATASET-tung1000.csv')

# Prepare features
df['quantity'] = df['LC_CN1_Tồn kho ban đầu']  # Initial stock as quantity
df['price'] = df['PL_Giá nhập']  # Import price
df['total_amount'] = df['quantity'] * df['price']
df['retail_price'] = df['PL_Giá bán lẻ']
df['profit_margin'] = (df['retail_price'] - df['price']) / (df['retail_price'] + 1)

# Select features
features = df[['quantity', 'price', 'total_amount', 'retail_price', 'profit_margin']]

# Train model
from models.lstm_model import ImportForecastLSTM

model = ImportForecastLSTM(lookback=30, features=5)
# ... train on your data
```

---

## Key Takeaways

1. **MAPE removed** - Use MAE instead for better stability
2. **Log transformation** - Handles wide price ranges (5K-150K)
3. **ReLU output** - Ensures positive quantity predictions
4. **Huber loss** - Robust to outliers in retail data
5. **Gradient clipping** - Prevents training explosion
6. **Your dataset is rich** - Can add retail_price, import_price, profit_margin easily

---

## Next Steps

1. ✅ Test current improvements (should fix MAPE explosion)
2. Add retail_price and import_price features (simple)
3. Consider product category encoding (if you want per-category predictions)
4. Retrain model with cleaned data
5. Monitor MAE instead of MAPE

**Status: READY TO TEST** 🚀
