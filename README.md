# Inventory Import Forecast - Deep Learning Demo

[![GitHub repo size](https://img.shields.io/github/repo-size/wikiepeidia/predict-future-import-for-Retail-store-products)](https://github.com/wikiepeidia/predict-future-import-for-Retail-store-products)
[![GitHub last commit](https://img.shields.io/github/last-commit/wikiepeidia/predict-future-import-for-Retail-store-products)](https://github.com/wikiepeidia/predict-future-import-for-Retail-store-products/commits)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

A **simplified deep learning demonstration project** for retail inventory management. This project showcases two neural network models working together to:

1. **Extract product data from invoice images** using CNN (Convolutional Neural Network)
2. **Forecast future import quantities** using LSTM (Long Short-Term Memory)

**Target Audience:** Deep Learning Course Exam / Portfolio Project (Focus on ML models, NOT frontend complexity)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Windows users:** Also install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)

### 2. Train Models

```bash
python train_models.py
```

### 3. Verify Installation

```bash
python verify_installation.py
```

### 4. Run Application

```bash
python app.py
```

Open browser: `http://localhost:5000`

📖 **Detailed guide:** See [QUICKSTART.md](QUICKSTART.md)

---

## 🧠 Model Architecture

### Model 1: CNN for Invoice OCR

- **Architecture:** 4-layer CNN with BatchNorm and Dropout
- **Input:** Invoice images (224x224x3)
- **Output:** Extracted text and structured invoice data
- **Technology:** TensorFlow/Keras + Tesseract OCR
- **Features:**
  - Image preprocessing (denoising, thresholding)
  - Text extraction via OCR
  - Invoice parsing (number, date, quantities, amounts)

### Model 2: LSTM for Forecasting

- **Architecture:** 3-layer LSTM with Dense layers
- **Input:** 30 timesteps × 5 features
- **Output:** Predicted import quantity
- **Technology:** TensorFlow/Keras
- **Features:**
  - Time-series analysis
  - Trend detection
  - Confidence scoring
  - ~2.5% MAPE on test data

**Features used:**

- Historical import quantities
- Unit prices
- Sales data
- Stock levels
- Demand indicators

---

## 📊 Data Pipeline

```
┌─────────────────────────┐
│   Invoice Image (JPG)   │
└───────────┬─────────────┘
            │
            ▼
    ┌──────────────┐
    │  CNN Model   │  ← Image OCR
    │  (Tesseract) │
    └──────┬───────┘
           │
           ▼
┌──────────────────────┐
│ Structured Data      │
│ (quantities, dates)  │
└──────────┬───────────┘
           │
           │ + Historical Data
           ▼
    ┌──────────────┐
    │  LSTM Model  │  ← Time-series
    │  (Forecast)  │     Forecasting
    └──────┬───────┘
           │
           ▼
┌──────────────────────┐
│ Predicted Quantity   │
│ + Confidence Score   │
└──────────────────────┘
```

---

## 🗂️ Project Structure

```
├── app.py                    # Flask app with real models
├── train_models.py           # Training script
├── verify_installation.py    # Installation checker
├── requirements.txt          # Dependencies
│
├── models/
│   ├── cnn_invoice_ocr.py   # CNN implementation
│   ├── lstm_forecast.py     # LSTM implementation
│   └── cnn_model.py         # MobileNetV2 transfer learning
│
├── saved_models/            # Trained model weights (.weights.h5)
│   ├── cnn_invoice_detector.weights.h5
│   └── lstm_text_recognizer.weights.h5
│
├── ui/templates/
│   └── index.html           # Web interface
├── static/
│   └── style.css
│
└── GUIDES/
    ├── PROJECT_OUTLINE.md
    ├── QUICKSTART.md
    └── SIMPLIFICATION_SUMMARY.md
```

---

## 🎯 API Endpoints

### POST `/api/model1/predict`

**LSTM Forecasting from Text Input**

Request:

```json
{
  "text": "100\n120\n135\n150"
}
```

Response:

```json
{
  "output1": "Invoice quantity extracted: 505 units (4 items)",
  "output2": "Predicted next import: 165 units",
  "confidence": 0.89,
  "trend": "increasing",
  "model_used": "LSTM Neural Network"
}
```

### POST `/api/model2/recognize`

**CNN OCR from Image**

Request: `multipart/form-data` with image file

Response:

```json
{
  "recognized_text": "Invoice #12345\nQuantity: 150...",
  "invoice_number": "12345",
  "total_quantity": 150,
  "total_amount": 4500000,
  "confidence": 0.85,
  "model_used": "CNN + Tesseract OCR"
}
```

---

## 📈 Model Performance

### LSTM Model (Trained on 500 samples)

- **Test MAE:** ~0.05
- **Test MAPE:** ~2.5%
- **Training:** 70% train, 10% val, 20% test
- **Epochs:** 50 (with early stopping)

### CNN Model

- **OCR Accuracy:** Depends on image quality
- **Preprocessing:** Denoising + Thresholding
- **Classification:** 10 invoice categories

---

## 💡 Use Cases

1. **Automated Invoice Processing**
   - Scan paper invoices
   - Extract product quantities
   - Update inventory system

2. **Smart Inventory Forecasting**
   - Analyze historical import patterns
   - Predict future demand
   - Optimize stock levels

3. **Retail Analytics**
   - Track product trends
   - Identify seasonal patterns
   - Reduce overstock/stockouts

---

## 🔧 Requirements

- Python 3.8+
- TensorFlow 2.13+
- OpenCV 4.8+
- Tesseract OCR (for Windows/Linux)
- 2GB+ RAM for model training

---

## 📚 For Deep Learning Exam

### Key Concepts Demonstrated

1. **CNN Architecture** - Convolutional layers, pooling, dropout
2. **LSTM Architecture** - Recurrent layers, time-series processing
3. **Data Pipeline** - Preprocessing, normalization, augmentation
4. **Training Strategy** - Train/val/test split, early stopping
5. **Model Integration** - Two models working together
6. **Real-world Application** - Practical business problem

### Exam Presentation Tips

- ✓ Explain why CNN for images (spatial features)
- ✓ Explain why LSTM for time-series (temporal dependencies)
- ✓ Show model architecture diagrams
- ✓ Demonstrate live predictions
- ✓ Discuss performance metrics (MAE, MAPE)
- ✓ Mention overfitting prevention (dropout, BatchNorm)

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file

---

## 🤝 Contributing

This is an educational project. Feel free to:

- Add more sophisticated models
- Improve OCR accuracy
- Add more features (product recognition, etc.)
- Create better visualizations

---

## ⚠️ Notes

- **Focus:** This project prioritizes ML model demonstration over UI/UX
- **Data:** Uses synthetic data for demonstration (replace with real data)
- **OCR:** Requires Tesseract installation for CNN model
- **Production:** Not production-ready (authentication, database, etc. not included)

---

**Made with ❤️ for Deep Learning Education**
