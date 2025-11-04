# Training Configuration Summary

## 📊 **THE 3 DATASETS**

### 1. QUANTUNG.csv (Warehouse Data - LSTM)

```
Purpose: LSTM forecasting for import quantity prediction
Records: 959 products
Type: Retail warehouse
Columns:
  - Tên sản phẩm (Product name)
  - Loại sản phẩm (Category)
  - Mã SKU (SKU code)
  - LC_CN1_Tồn kho ban đầu (Initial stock)
  - PL_Giá bán lẻ (Retail price)
  - PL_Giá nhập (Import price - calculated with 35% margin)
Price Range: 5,000 - 350,000,000 VND
Average Price: 1,043,054 VND
```

### 2. QUANSON.csv (Warehouse Data - LSTM)

```
Purpose: LSTM forecasting for import quantity prediction
Records: 14,142 products  
Type: Wholesale warehouse
Columns:
  - Tên sản phẩm (Product name)
  - Loại sản phẩm (Category)
  - Mã SKU (SKU code)
  - LC_CN1_Tồn kho ban đầu (Initial stock)
  - PL_Giá bán lẻ (Retail price)
  - PL_Giá nhập (Import price)
Price Range: 0 - 4,950,000 VND
Average Price: 117,460 VND
```

### 3. HOADON (Invoice Images - CNN)

```
Purpose: CNN invoice detection and OCR
Format: PNG images (800x1000 pixels)
Total Images: 320 images
  - QUANSON invoices: 220 images (generated_invoices_quanson/)
  - QUANTUNG invoices: 100 images (generated_invoices_quantung/)
  
Split:
  - Training: ~256 images (80%)
  - Testing: ~64 images (20%)
  
Features per invoice:
  - Store name (Kho Quân Sơn / Kho Quân Tùng)
  - Invoice ID
  - Date
  - Products list (3-10 products per invoice)
  - Quantities
  - Prices
  - Total amount
```

---

## 🎯 **TRAINING CONFIGURATION**

### LSTM Model (Import Forecasting)

```python
Architecture:
  - Input: (30 timesteps, 5 features)
  - LSTM Layer 1: 128 units + Dropout(0.3) + BatchNorm
  - LSTM Layer 2: 64 units + Dropout(0.3) + BatchNorm
  - LSTM Layer 3: 32 units + Dropout(0.3)
  - Dense: 64 units (ReLU) + Dropout(0.2)
  - Dense: 32 units (ReLU)
  - Output: 1 unit (ReLU - positive predictions)

Training Parameters:
  ✅ Learning Rate: 0.01
  ✅ Optimizer: Adam with gradient clipping (clipnorm=1.0)
  ✅ Loss: Huber (robust to outliers)
  ✅ Metrics: MAE (NO MAPE - prevents explosion)
  ✅ Epochs: 50
  ✅ Batch Size: 32
  ✅ Data Preprocessing: Log transformation (log1p) for wide price ranges
  
Input Features:
  1. quantity (stock quantity)
  2. price (product price)
  3. total_amount (quantity × price)
  4. num_products (product count)
  5. max_product_qty (max quantity in batch)

Data Source:
  - Combined: QUANTUNG (959) + QUANSON (14,142) = 15,101 products
  - Time sequences: 30-day lookback window
  - Train/Val/Test: 70% / 10% / 20%
```

### CNN Model (Invoice Detection)

```python
Architecture:
  - Base: MobileNetV2 (transfer learning)
  - Input: (224, 224, 3) RGB images
  - GlobalAveragePooling2D
  - Dense: 256 units (ReLU) + Dropout(0.5)
  - Output 1: 128-dim invoice features
  - Output 2: 10-class invoice type (softmax)

Training Parameters:
  ✅ Learning Rate: 0.01
  ✅ Optimizer: Adam with gradient clipping (clipnorm=1.0)
  ✅ Loss: 
      - Invoice features: Huber (robust)
      - Invoice type: Categorical crossentropy
  ✅ Metrics:
      - Invoice features: MAE
      - Invoice type: Accuracy
  ✅ Epochs: 50
  ✅ Batch Size: 16
  ✅ Callbacks:
      - EarlyStopping (patience=10)
      - ReduceLROnPlateau (factor=0.5, patience=5)

Data Source:
  - HOADON images: 320 total
    * QUANSON: 220 images
    * QUANTUNG: 100 images
  - Split: 80% train / 20% validation
  - Augmentation: Noise, rotation, realistic formatting
```

---

## 🚀 **TRAINING WORKFLOW**

### Step 1: Data Loading

```python
# LSTM: Load CSV datasets
QUANTUNG = pd.read_csv('data/QUANTUNG.csv')  # 959 products
QUANSON = pd.read_csv('data/QUANSON.csv')    # 14,142 products
combined_data = concat([QUANTUNG, QUANSON])  # 15,101 products

# CNN: Load invoice images
HOADON_quanson = load_images('data/generated_invoices_quanson/')   # 220 images
HOADON_quantung = load_images('data/generated_invoices_quantung/') # 100 images
combined_images = HOADON_quanson + HOADON_quantung                  # 320 images
```

### Step 2: Preprocessing

```python
# LSTM: Feature extraction & log transformation
features = ['quantity', 'price', 'total_amount', 'num_products', 'max_product_qty']
data = log1p(data + epsilon)  # Handle wide price ranges (5K - 150K)
normalized = scaler.fit_transform(data)
sequences = create_sequences(normalized, lookback=30)

# CNN: Image preprocessing
images = resize_to_224x224(images)
images = images / 255.0  # Normalize to [0, 1]
```

### Step 3: Training

```bash
python train_models.py
```

This trains:

1. **LSTM Model** on 15,101 products (QUANTUNG + QUANSON)
2. **CNN Model** on 320 invoice images (HOADON)

### Step 4: Evaluation

```python
# LSTM Metrics
- Huber Loss (train & validation)
- MAE (train & validation)
- Prediction confidence
- Trend analysis (increasing/decreasing/stable)

# CNN Metrics  
- Invoice features MAE
- Invoice type accuracy
- Classification report
```

---

## 📈 **IMPROVEMENTS IMPLEMENTED**

### MAPE Explosion Fix

- ❌ Removed MAPE metric (caused explosion to 1,000,000+)
- ✅ Using MAE only (stable, interpretable)
- ✅ Huber loss for robustness to outliers

### Wide Price Range Handling

- ✅ Log transformation (log1p) before normalization
- ✅ Prevents gradient issues with 5K-150K price ranges
- ✅ Inverse transformation (expm1) for predictions

### Gradient Stability

- ✅ Gradient clipping (clipnorm=1.0)
- ✅ Batch normalization in LSTM
- ✅ Dropout regularization (0.2-0.5)
- ✅ Learning rate: 0.01 (increased for faster convergence)

### Data Quality

- ✅ QUANTUNG import prices calculated with 35% margin formula
- ✅ Prices formatted with dots (12.000, 44.000)
- ✅ Vietnamese product names preserved
- ✅ Realistic invoice images with noise and rotation

---

## ✅ **READY TO TRAIN**

Run:

```bash
python train_models.py
```

Expected output:

- LSTM model trained on 15,101 products
- CNN model trained on 320 invoice images
- Models saved to `saved_models/`
- Training history and metrics displayed
- No MAPE explosions!
- Stable MAE metrics

Training time: ~10-15 minutes (depending on hardware)
