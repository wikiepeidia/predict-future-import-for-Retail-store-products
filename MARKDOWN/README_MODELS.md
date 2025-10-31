# Deep Learning Invoice Forecast System

## 🎯 Project Overview

Hệ thống dự đoán nhập hàng cho cửa hàng bán lẻ sử dụng Deep Learning với 2 model:

### **Model 1: CNN (Convolutional Neural Network)**
- **Input (x1):** Hóa đơn giấy (Invoice Image - JPG/PNG/PDF)
- **Output (Y1):** Hóa đơn điện tử nhập hàng (Structured Electronic Data)
- **Architecture:** MobileNetV2 + Custom Detection Head
- **Task:** Image Detection → OCR → Data Extraction

### **Model 2: LSTM (Long Short-Term Memory)**
- **Input:** Y1 (từ Model 1) + x2 (Hóa đơn nhập hàng) + x3 (Hóa đơn nhập hàng)
- **Output (Y2 TEXT):** Dự đoán số lượng để tiếp (Quantity Forecast)
- **Architecture:** Stacked LSTM with Attention Mechanism
- **Task:** Time Series Forecasting

---

## 📊 Dataset

### 3 Dataset Sources:
1. **Danh sách sản phẩm quán Sơn** (Product catalog - Son)
2. **Danh sách sản phẩm quán Tùng** (Product catalog - Tung)
3. **Hóa đơn điện tử quán Tùng** (Electronic invoices - Tung)

### Data Split:
- **70% Training**
- **10% Validation**
- **20% Testing**

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Dataset

```bash
cd data
python generate_dataset.py
```

This will create:
- `data/invoices/train.json` (70%)
- `data/invoices/valid.json` (10%)
- `data/invoices/test.json` (20%)
- `data/images/*.png` (Invoice images)
- `data/product_catalogs.json`

### 3. Train Models

```bash
python train_models.py
```

This will train both CNN and LSTM models and save them to `saved_models/`.

### 4. Run Application

```bash
python app.py
```

Access at: http://localhost:5000

---

## 📁 Project Structure

```
├── app.py                      # Flask application (Main entry point)
├── train_models.py             # Training script for both models
├── requirements.txt            # Python dependencies
│
├── models/                     # Deep Learning Models
│   ├── __init__.py
│   ├── cnn_model.py           # Model 1: CNN Invoice Detector
│   └── lstm_model.py          # Model 2: LSTM Quantity Forecaster
│
├── data/                       # Dataset
│   ├── generate_dataset.py    # Dataset generator script
│   ├── invoices/              # Generated invoices (JSON)
│   │   ├── train.json
│   │   ├── valid.json
│   │   └── test.json
│   ├── images/                # Invoice images (PNG)
│   └── product_catalogs.json  # Product lists
│
├── saved_models/              # Trained models
│   ├── cnn_invoice_detector.h5
│   └── lstm_text_recognizer.h5
│
├── ui/templates/              # Web Interface
│   └── index.html
│
├── static/                    # CSS/JS
│   ├── style.css
│   └── script.js
│
└── uploads/                   # Uploaded invoice images
```

---

## 🔌 API Endpoints

### Model 1: CNN Invoice Detection
```
POST /api/model1/detect
Content-Type: multipart/form-data

Form Data:
- image: (file) Invoice image

Response:
{
  "success": true,
  "model": "CNN (Model 1)",
  "output": "Y1 - Hóa đơn điện tử nhập hàng",
  "data": {
    "invoice_id": "INV_12345",
    "store_name": "Quán Sơn",
    "products": [...],
    "total_amount": 500000,
    "confidence": 0.92
  }
}
```

### Model 2: LSTM Quantity Forecasting
```
POST /api/model2/forecast

Response:
{
  "success": true,
  "model": "LSTM (Model 2)",
  "output": "Y2 TEXT - Dự đoán số lượng",
  "data": {
    "predicted_quantity": 350,
    "recommendation_text": "Dự đoán số lượng nhập hàng kỳ tiếp: 350 sản phẩm...",
    "confidence": 0.85,
    "trend": "increasing"
  },
  "history_count": 15
}
```

### Other Endpoints
```
GET  /api/models/info      # Model information
GET  /api/history          # Invoice history
POST /api/history/clear    # Clear history
```

---

## 🧠 Model Architecture Details

### CNN Model (Model 1)

```python
Input: (224, 224, 3) RGB Image
    ↓
MobileNetV2 (Pretrained, Frozen)
    ↓
GlobalAveragePooling2D
    ↓
Dense(512, ReLU) + Dropout(0.3)
    ↓
Dense(256, ReLU) + Dropout(0.2)
    ↓
Dense(128, ReLU) [Features]
    ↓
Dense(10, Softmax) [Invoice Type Classification]
```

### LSTM Model (Model 2)

```python
Input: (sequence_length=10, features=5)
    ↓
LSTM(128, return_sequences=True) + Dropout(0.3)
    ↓
LSTM(64, return_sequences=True) + Dropout(0.2)
    ↓
Attention Mechanism
    ↓
Dense(32, ReLU) + Dropout(0.1)
    ↓
Dense(1, Linear) [Predicted Quantity]
```

---

## 📝 Usage Example

### Python API

```python
from models.cnn_model import CNNInvoiceDetector
from models.lstm_model import LSTMTextRecognizer

# Model 1: Detect invoice
cnn = CNNInvoiceDetector()
cnn.build_model()
invoice_data = cnn.predict_invoice_data('path/to/invoice.png')

# Model 2: Forecast quantity
lstm = LSTMTextRecognizer()
lstm.build_model()
prediction = lstm.predict_quantity([invoice_data])

print(f"Predicted: {prediction['predicted_quantity']} units")
print(prediction['recommendation_text'])
```

---

## 🎓 For Deep Learning Exam

### Key Points to Highlight:

1. **Two-Model Pipeline**
   - CNN for computer vision (image → data)
   - LSTM for time-series forecasting (history → future)

2. **Transfer Learning**
   - Using pretrained MobileNetV2 for efficient feature extraction
   - Fine-tuning on invoice-specific task

3. **Attention Mechanism**
   - LSTM with attention for better long-term dependencies
   - Focuses on relevant historical patterns

4. **Real-World Application**
   - Practical retail inventory management problem
   - End-to-end solution from image to forecast

5. **Dataset Strategy**
   - Proper 70/10/20 split
   - Multiple data sources (2 stores)
   - Time-series structure for LSTM training

---

## 📚 References

- **CNN Architecture:** MobileNetV2 - [Paper](https://arxiv.org/abs/1801.04381)
- **LSTM:** [Understanding LSTM Networks](http://colah.github.io/posts/2015-08-Understanding-LSTMs/)
- **Attention Mechanism:** [Attention is All You Need](https://arxiv.org/abs/1706.03762)

---

## 👥 Author

Deep Learning Course Project - October 2025

## 📄 License

MIT License
