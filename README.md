# 🏪 Dự Đoán Nhập Hàng Thông Minh

**Hệ thống AI dự đoán số lượng nhập hàng cho cửa hàng bán lẻ sử dụng Deep Learning**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.10+-orange.svg)](https://tensorflow.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Tổng Quan

Dự án sử dụng 2 mô hình Deep Learning:

- **Model 1 (CNN)**: Nhận diện hóa đơn giấy → Chuyển thành dữ liệu điện tử
- **Model 2 (LSTM)**: Phân tích lịch sử nhập/bán → Dự đoán số lượng nhập hàng

### 📊 Dataset

**Dataset chính: dataset_product.csv**

- 2000+ sản phẩm với thông tin:
  - Tên sản phẩm
  - Tồn kho ban đầu
  - Giá nhập
  - Giá bán lẻ

**Timescale datasets (Oct 1 - Nov 1, 2025):**

- **import_in_a_timescale.csv**: Số lượng nhập trong khoảng thời gian
- **sale_in_a_timescale.csv**: Số lượng bán trong khoảng thời gian

### 📊 Model Training

**Model 1 (CNN):**

- 400 synthetic invoice images từ dataset_product.csv
- Training: 70% (280 images)
- Validation: 20% (80 images)
- Testing: 10% (40 images)
- Date range: October 1 - November 1, 2025

**Model 2 (LSTM):**

- Training SEPARATE với dữ liệu timescale
- Features: import_qty, sale_qty, initial_stock, retail_price, turnover_rate
- Phân tích pattern giữa nhập và bán hàng
- Dự đoán số lượng nhập tối ưu

### ⚙️ Training Configuration

- **Epochs**: 48
- **Batch Size**: 12
- **Loss**: Huber (robust to outliers)
- **Metrics**: MAE (Mean Absolute Error)
- **Learning Rate**: 0.01 with adaptive reduction

## 🗂️ Cấu Trúc Thư Mục

```
predict-future-import-for-Retail-store-products/
├── app_new.py                # Flask web application (new clean version)
├── train_models.py           # CNN training script
├── train_lstm_separately.py  # LSTM training script (NEW!)
├── test.py                   # Testing script
│
├── models/                   # Deep Learning Models
│   ├── cnn_model.py         # CNN Invoice Detector
│   ├── lstm_model.py        # LSTM Forecaster
│   └── saved_models/        # Trained weights (.weights.h5)
│
├── data/                     # Data files
│   ├── dataset_product.csv          # Main product database
│   ├── import_in_a_timescale.csv   # Import data (Oct-Nov 2025)
│   ├── sale_in_a_timescale.csv     # Sales data (Oct-Nov 2025)
│   └── generate_balanced_dataset.py # Generate 400 invoice images
│
├── api/                      # API blueprints
│   ├── model1.py            # CNN endpoints
│   ├── model2.py            # LSTM endpoints
│   └── history.py           # History endpoints
│
├── services/                 # Business logic
│   └── model_loader.py      # Model initialization
│
├── utils/                    # Utilities
│   ├── data_processor.py    # Data processing
│   └── validators.py        # Input validation
│
└── ui/templates/             # Web UI
    ├── index.html           # Homepage
    └── dashboard.html       # Dashboard
```

## ⚡ Cài Đặt Nhanh

### Manual Steps

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate invoice images (400 images from dataset_product.csv)
python data/generate_balanced_dataset.py

# 3. Train CNN model (invoice detection)
python train_models.py

# 4. Train LSTM model separately (import forecasting)
python train_lstm_separately.py

# 5. Run Flask app
python app_new.py
```

Mở trình duyệt: **<http://localhost:5000>**

## 🎯 API Sử Dụng

### 1. Nhận diện hóa đơn (CNN)

```python
import requests

url = "http://localhost:5000/api/model1/detect"
files = {'image': open('invoice.jpg', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

### 2. Dự đoán số lượng (LSTM)

```python
url = "http://localhost:5000/api/model2/forecast"
response = requests.post(url, json={})
print(response.json())
```

## 🧠 Kiến Trúc Models

### Model 1: CNN Invoice Detector

- **Base**: MobileNetV2 (Transfer Learning)
- **Input**: Image 224x224x3
- **Output**: Structured invoice data (JSON)
- **Training Data**: 400 synthetic invoices from dataset_product.csv
- **Date Range**: October 1 - November 1, 2025

### Model 2: LSTM Forecaster

- **Architecture**: Stacked LSTM + Attention
- **Input**: Timescale features (10 sequences, 5 features)
- **Features**:
  1. import_qty (nhập trong timescale)
  2. sale_qty (bán trong timescale)
  3. initial_stock (tồn kho ban đầu)
  4. retail_price (giá bán)
  5. turnover_rate (tỷ lệ luân chuyển)
- **Output**: Predicted import quantity + confidence + trend
- **Training**: Separate script using timescale datasets

## 🔧 Cấu Hình

Chỉnh sửa `core/config.py`:

```python
IMG_HEIGHT = 224
IMG_WIDTH = 224
LSTM_SEQUENCE_LENGTH = 10
LSTM_NUM_FEATURES = 5
EPOCHS = 48
BATCH_SIZE = 12
```

## 📝 License

MIT License - See [LICENSE](LICENSE)

## 👥 Authors

Deep Learning Project 2025
