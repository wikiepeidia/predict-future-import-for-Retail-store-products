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

## Project Flow

```
INPUT 1: Invoice Image (Paper or Digital)
    ↓
[MODEL 1: CNN - Invoice Detection]
    ↓
Extracted Items (Normalized Invoice Data)
    ↓
    + INPUT 2: Inventory Snapshot
    ↓
[MODEL 2: LSTM - Quantity Forecasting]
    ↓
OUTPUT: Predicted Import Quantities per SKU
```

---

## Features

### Model 1: Invoice Detection (CNN)

- **Input:** Invoice image (JPG, PNG, PDF)
- **Output:** Structured product data with:
  - SKU (Stock Keeping Unit)
  - Product name
  - Quantity ordered
  - Unit price
- **Architecture:** Convolutional Neural Network for image feature extraction + OCR-style text recognition

### Model 2: Quantity Forecasting (LSTM)

- **Input 1:** Normalized invoice (from Model 1)
- **Input 2:** Current inventory levels + historical sales
- **Output:** Recommended import quantities for next period
- **Architecture:** LSTM for time-series pattern recognition

---

## Project Structure

```
predict-future-import-for-Retail-store-products/
├── app.py                          # Flask web app (simplified)
├── PROJECT_OUTLINE.md              # Detailed project documentation
├── README.md                        # This file
├── core/
│   ├── config.py                  # Configuration settings
│   ├── database.py                # (Optional) Database utilities
│   ├── utils.py                   # Helper functions
│   └── __pycache__/
├── ui/
│   └── templates/
│       └── index.html             # Single page for invoice upload & forecast
├── static/
│   ├── style.css                  # Basic styling
│   └── script.js                  # Frontend logic
├── uploads/                        # Invoice image uploads (created at runtime)
└── images/                        # Project documentation images
```

---

## Getting Started

### Prerequisites

- Python 3.8+
- Flask
- (Optional) TensorFlow/Keras for actual model inference

### Installation

```bash
# Clone repository
git clone <repository-url>
cd predict-future-import-for-Retail-store-products

# Install dependencies
pip install flask werkzeug

# (Optional) For deep learning models
pip install tensorflow keras numpy pandas
```

### Running the App

```bash
# Start Flask development server
python app.py

# Open browser to http://localhost:5000
```

### Using the Demo

1. **Upload Invoice Image**
   - Click or drag-drop a scanned invoice image (JPG/PNG/PDF)
   - Model 1 (CNN) extracts product items
   - Results display in a table

2. **Forecast Imports**
   - Click "Forecast" button to predict quantities
   - Model 2 (LSTM) generates recommendations
   - View predicted quantities per SKU

---

## API Endpoints

### 1. Upload Invoice (Model 1)

```
POST /api/upload_invoice

Input:
- File: invoice_image (multipart form data)

Output:
{
  "success": true,
  "invoice_data": {
    "items": [
      {"sku": "MILK_A", "product_name": "Milk Brand A", "quantity": 10, "unit_price": 20000},
      ...
    ]
  }
}
```

### 2. Forecast Imports (Model 2)

```
POST /api/forecast_imports

Input:
{
  "invoice_data": {...},
  "inventory_snapshot": {...}
}

Output:
{
  "forecasts": [
    {
      "sku": "MILK_A",
      "predicted_quantity": 12,
      "recommendation": "Order 12 units"
    },
    ...
  ]
}
```

---

## Dataset

### Data Split

- **Training:** 70%
- **Validation:** 10%
- **Testing:** 20%

### Data Sources (Example)

- Store Son historical invoices
- Store Tùng historical invoices
- Structured import/sales records

---

## Model Architecture Details

### Model 1: CNN (Invoice Detection)

```
Input Layer (Image) → Conv2D → ReLU → MaxPool → 
Conv2D → ReLU → MaxPool → Flatten → Dense → Output (Item Detection)
```

### Model 2: LSTM (Quantity Forecasting)

```
Input: [Normalized Invoice + Inventory History]
    ↓
LSTM(units=128) → LSTM(units=64) → Dense(32) → Dense(output_dim)
    ↓
Output: Predicted Quantities
```

---

## What's NOT Included (By Design)

❌ User authentication/login system  
❌ Multi-user support  
❌ Complex admin dashboards  
❌ Database persistence (demo-only)  
❌ Production deployment configuration  
❌ Heavy frontend frameworks  

**Why?** This is a *focused deep learning demo*, not a production application. The emphasis is on ML models, not infrastructure.

---

## Future Enhancements

- ✅ Integrate real trained CNN model  
- ✅ Integrate real trained LSTM model  
- ✅ Add model confidence scores  
- ✅ Support batch invoice processing  
- ✅ Export forecast as CSV/Excel  
- ✅ Add model performance metrics visualization  

---

## Exam Presentation Tips

### What to Highlight

1. **Two-Model Pipeline:** Show the flow from invoice image → structured data → forecast
2. **Model Architectures:** Explain CNN for image feature extraction, LSTM for time-series
3. **Dataset Strategy:** 70/10/20 split for train/val/test
4. **Real-World Application:** Retail inventory optimization

### Demo Flow

1. Upload sample invoice image → Show Model 1 output (extracted items)
2. Click forecast → Show Model 2 output (predicted quantities)
3. Explain the business value and model decisions

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## TODO

FIX CSS

---

**Last Updated:** October 2025  
**Status:** Deep Learning Exam Demo ✅
