# 🏪 Dự Đoán Nhập Hàng Thông Minh

**Hệ thống AI dự đoán số lượng nhập hàng cho cửa hàng bán lẻ sử dụng Deep Learning**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.10+-orange.svg)](https://tensorflow.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Tổng Quan

Dự án sử dụng 2 mô hình Deep Learning:
- **Model 1 (CNN)**: Nhận diện hóa đơn giấy → Chuyển thành dữ liệu điện tử
- **Model 2 (LSTM)**: Phân tích lịch sử → Dự đoán số lượng nhập hàng

## 🗂️ Cấu Trúc Thư Mục

```
predict-future-import-for-Retail-store-products/
├── app.py                    # Flask web application
├── config.py                 # Cấu hình tập trung
├── train_models.py           # Script huấn luyện
├── test.py                   # Script kiểm tra
│
├── models/                   # Deep Learning Models
│   ├── cnn_model.py         # CNN Invoice Detector
│   ├── lstm_model.py        # LSTM Forecaster
│   └── saved/               # Trained weights
│
├── utils/                    # Utilities
│   ├── data_processor.py    # Data processing
│   └── invoice_processor.py # Invoice handling
│
├── data/                     # Data files
│   ├── product_catalogs.json
│   └── generate_dataset.py
│
├── ui/templates/             # Web UI
├── static/                   # CSS, JS
└── docs/                     # Documentation
    ├── SETUP.md             # Setup guide
    ├── API_GUIDE.md         # API documentation
    └── MODEL_DOCS.md        # Model details
```

## ⚡ Cài Đặt Nhanh

```bash
# 1. Cài đặt dependencies
pip install -r requirements.txt

# 2. Tạo dataset mẫu
python data/generate_dataset.py

# 3. Train models (optional)
python train_models.py

# 4. Chạy ứng dụng
python app.py
```

Mở trình duyệt: **http://localhost:5000**

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

Xem chi tiết: [docs/API_GUIDE.md](docs/API_GUIDE.md)

## 🧠 Kiến Trúc Models

### Model 1: CNN Invoice Detector
- **Base**: MobileNetV2 (Transfer Learning)
- **Input**: Image 224x224x3
- **Output**: Structured invoice data (JSON)

### Model 2: LSTM Forecaster
- **Architecture**: Stacked LSTM + Attention
- **Input**: Sequence of 10 invoices (10, 5)
- **Output**: Predicted quantity + recommendations

## 📚 Tài Liệu

- [SETUP.md](docs/SETUP.md) - Hướng dẫn cài đặt chi tiết
- [API_GUIDE.md](docs/API_GUIDE.md) - API documentation đầy đủ
- [MODEL_DOCS.md](docs/MODEL_DOCS.md) - Chi tiết kiến trúc models

## 🔧 Cấu Hình

Chỉnh sửa `config.py`:
```python
IMG_HEIGHT = 224
IMG_WIDTH = 224
LSTM_SEQUENCE_LENGTH = 10
EPOCHS = 50
BATCH_SIZE = 32
```

## 📊 Dataset

- **Product Catalogs**: 100+ sản phẩm từ 2 cửa hàng
- **Sample Dataset**: 1000 bản ghi hóa đơn

## 📝 License

MIT License - See [LICENSE](LICENSE)

## 👥 Authors

Deep Learning Project 2025
