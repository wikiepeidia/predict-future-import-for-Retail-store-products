# 🚀 Quick Start Guide

## Installation & Setup

### Step 1: Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

**Note for Windows users:** You'll also need to install Tesseract OCR for the CNN model:
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR`
3. Add to system PATH

### Step 2: Train the Models

```bash
# Train both CNN and LSTM models
python train_models.py
```

This will:
- ✓ Generate sample time-series data (500 samples)
- ✓ Train LSTM model for quantity forecasting
- ✓ Initialize CNN model architecture
- ✓ Save models to `models/saved/`

**Expected output:**
```
Training LSTM Model...
  Train: 329 samples
  Val:   47 samples
  Test:  94 samples
  
Test MAE: ~0.05
Test MAPE: ~2.5%

✓ Models saved successfully!
```

### Step 3: Run the Application

```bash
# Start Flask server
python app.py
```

Open browser: `http://localhost:5000`

---

## 🧪 Testing the Models

### Model 1: LSTM Forecasting (Text Input)
1. Navigate to "Model 2: LSTM" section
2. Enter invoice data (one number per line):
   ```
   100
   120
   135
   150
   ```
3. Click "Predict Import Quantity"
4. View prediction with confidence score

### Model 2: CNN OCR (Image Upload)
1. Navigate to "Model 1: CNN" section
2. Upload an invoice image (JPG/PNG)
3. Click "Extract Text"
4. View extracted text and parsed data

---

## 📊 Model Architecture

### LSTM Model
```
Input: (30 timesteps, 5 features)
  ↓
LSTM(128) → Dropout → BatchNorm
  ↓
LSTM(64) → Dropout → BatchNorm
  ↓
LSTM(32) → Dropout
  ↓
Dense(64) → Dense(32) → Dense(1)
  ↓
Output: Predicted quantity
```

**Features used:**
- Quantity (historical imports)
- Price
- Sales
- Stock levels
- Demand indicator

### CNN Model
```
Input: (224x224x3) RGB Image
  ↓
Conv2D(32) → BatchNorm → MaxPool → Dropout
  ↓
Conv2D(64) → BatchNorm → MaxPool → Dropout
  ↓
Conv2D(128) → BatchNorm → MaxPool → Dropout
  ↓
Conv2D(256) → BatchNorm → MaxPool → Dropout
  ↓
Flatten → Dense(512) → Dense(256)
  ↓
Output: Invoice classification (10 classes)
```

**OCR Pipeline:**
1. Image preprocessing (grayscale, denoising, thresholding)
2. Tesseract OCR text extraction
3. Text parsing for invoice details
4. CNN classification (optional)

---

## 🗂️ Project Structure

```
├── app.py                    # Flask application (updated with real models)
├── train_models.py           # Training script
├── requirements.txt          # Python dependencies
│
├── models/
│   ├── __init__.py
│   ├── cnn_invoice_ocr.py   # CNN model for OCR
│   ├── lstm_forecast.py     # LSTM model for forecasting
│   └── saved/               # Trained model files
│       ├── lstm_forecast_model.h5
│       ├── lstm_forecast_model_scaler.pkl
│       └── cnn_invoice_model.h5
│
├── ui/templates/
│   └── index.html           # Web interface
├── static/
│   └── style.css            # Styling
│
└── GUIDES/
    ├── PROJECT_OUTLINE.md
    └── SIMPLIFICATION_SUMMARY.md
```

---

## 🎯 For Deep Learning Exam

### Key Points to Present:

1. **Two-Model Pipeline**
   - CNN for invoice OCR (Computer Vision)
   - LSTM for time-series forecasting (Recurrent NN)

2. **Data Strategy**
   - Training: 70%
   - Validation: 10%
   - Testing: 20%

3. **Model Performance**
   - LSTM: ~2.5% MAPE on test set
   - CNN: Uses pre-trained Tesseract + custom architecture

4. **Real-World Application**
   - Automates invoice processing
   - Predicts inventory needs
   - Reduces manual data entry

---

## 🔧 Troubleshooting

### Import Errors
```bash
# If you see "Module not found"
pip install --upgrade -r requirements.txt
```

### Tesseract Not Found
```python
# Edit models/cnn_invoice_ocr.py, line 15
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Model Training Slow
- Reduce epochs in `train_models.py` (line 72): `epochs=20`
- Reduce data samples (line 17): `n_samples=200`

---

## 📈 Next Steps

1. **Collect Real Data**
   - Gather actual invoice images
   - Label invoice types and fields
   - Record historical import quantities

2. **Fine-tune Models**
   - Train CNN on labeled invoice dataset
   - Adjust LSTM hyperparameters
   - Experiment with different architectures

3. **Deploy**
   - Add authentication
   - Database integration
   - Production server (Gunicorn/uWSGI)

---

## ✅ Checklist

- [ ] Dependencies installed
- [ ] Tesseract OCR installed (for Windows)
- [ ] Models trained (`python train_models.py`)
- [ ] Flask app running (`python app.py`)
- [ ] Both models tested via web interface
- [ ] Model architecture understood
- [ ] Ready for exam presentation!

---

**Happy Learning! 🎓**
