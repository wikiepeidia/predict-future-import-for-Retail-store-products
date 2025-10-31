# 📝 Quick Reference Card

## Installation (Choose One Method)

### Method 1: Automated Setup (Windows)
```bash
# Run setup script
setup.bat
# or
.\setup.ps1
```

### Method 2: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train models
python train_models.py

# 3. Verify
python verify_installation.py

# 4. Run app
python app.py
```

---

## Project Files

```
📁 Project Root
├── 🚀 app.py                    # Main Flask application
├── 🎓 train_models.py           # Model training script
├── ✅ verify_installation.py    # Installation checker
├── 📦 requirements.txt          # Dependencies
│
├── 📁 models/
│   ├── cnn_invoice_ocr.py      # CNN implementation
│   ├── lstm_forecast.py        # LSTM implementation
│   └── 📁 saved/               # Trained models (.h5)
│
├── 📁 GUIDES/
│   ├── 📖 QUICKSTART.md            # Getting started
│   ├── 📖 MODEL_DOCUMENTATION.md   # Technical docs
│   ├── 📖 EXAM_PRESENTATION_GUIDE.md # Exam prep
│   └── 📖 PROJECT_OUTLINE.md       # Architecture
│
└── 📁 ui/templates/
    └── index.html              # Web interface
```

---

## Model Architectures

### CNN (Invoice OCR)
```
Input: 224×224×3
Conv2D(32) → Conv2D(64) → Conv2D(128) → Conv2D(256)
Dense(512) → Dense(256) → Dense(10)
Parameters: ~8.5M
```

### LSTM (Forecasting)
```
Input: 30×5
LSTM(128) → LSTM(64) → LSTM(32)
Dense(64) → Dense(32) → Dense(1)
Parameters: ~125K
```

---

## Key Metrics

| Metric | Value | Meaning |
|--------|-------|---------|
| MAE | 0.05 | Mean Absolute Error |
| MAPE | 2.5% | Percentage Error |
| MSE | 0.003 | Mean Squared Error |

---

## API Endpoints

### LSTM Prediction
```http
POST /api/model1/predict
Content-Type: application/json

{
  "text": "100\n120\n135\n150"
}
```

### CNN OCR
```http
POST /api/model2/recognize
Content-Type: multipart/form-data

image: <file>
```

---

## Common Commands

```bash
# Check Python version
python --version

# Install specific package
pip install tensorflow

# List installed packages
pip list

# Run with specific port
python app.py --port 8000

# Check model files exist
dir models\saved

# View model summary
python -c "from models.lstm_forecast import ImportForecastLSTM; m=ImportForecastLSTM(); m.model.summary()"
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Import errors | `pip install -r requirements.txt` |
| Tesseract not found | Install from https://github.com/UB-Mannheim/tesseract/wiki |
| Models not found | Run `python train_models.py` |
| Port already in use | Change port in `app.py` line 220 |
| CUDA errors | Use CPU version: `pip install tensorflow-cpu` |

---

## Important Code Snippets

### Load LSTM Model
```python
from models.lstm_forecast import ImportForecastLSTM
model = ImportForecastLSTM(model_path='models/saved/lstm_forecast_model.h5')
```

### Load CNN Model
```python
from models.cnn_invoice_ocr import InvoiceOCRModel
model = InvoiceOCRModel(model_path='models/saved/cnn_invoice_model.h5')
```

### Make Prediction
```python
import pandas as pd
data = pd.DataFrame({'quantity': [100,120,135], 'price': [50,50,50], ...})
result = model.predict_next_quantity(data)
print(result['predicted_quantity'])
```

---

## Exam Talking Points

### CNN
- ✓ Convolutional layers for spatial features
- ✓ Pooling for dimensionality reduction
- ✓ Dropout prevents overfitting
- ✓ BatchNorm stabilizes training

### LSTM
- ✓ Memory cells for long-term dependencies
- ✓ Gates control information flow
- ✓ Handles sequential data
- ✓ Prevents vanishing gradients

### Training
- ✓ 70/10/20 split (train/val/test)
- ✓ Early stopping prevents overfitting
- ✓ Learning rate reduction for convergence
- ✓ Metrics: MAE, MAPE, MSE

---

## File Sizes

| File | Size |
|------|------|
| lstm_forecast_model.h5 | ~500 KB |
| cnn_invoice_model.h5 | ~32 MB |
| lstm scaler | ~2 KB |

---

## Dependencies

**Core:**
- tensorflow >= 2.13.0
- keras >= 2.13.0
- numpy >= 1.24.0
- pandas >= 2.0.0

**Optional:**
- opencv-python (image processing)
- pytesseract (OCR)

---

## URLs

- **App:** http://localhost:5000
- **GitHub:** https://github.com/wikiepeidia/predict-future-import-for-Retail-store-products
- **Tesseract:** https://github.com/UB-Mannheim/tesseract/wiki

---

## Quick Test

```bash
# 1. Verify everything works
python verify_installation.py

# 2. Start app
python app.py

# 3. Open browser
start http://localhost:5000

# 4. Test LSTM (in UI)
Enter: 100, 120, 135, 150
Click: Predict Import Quantity

# 5. Test CNN (in UI)
Upload: sample invoice image
Click: Extract Text
```

---

**Keep this card handy during your exam! 📌**
