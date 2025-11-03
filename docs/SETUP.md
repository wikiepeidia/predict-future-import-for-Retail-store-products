# 🔧 Setup Guide - Hướng Dẫn Cài Đặt

## 📋 Yêu Cầu Hệ Thống

### Phần Cứng
- **RAM**: Tối thiểu 4GB (Khuyến nghị 8GB+)
- **CPU**: Intel i3+ hoặc AMD equivalent
- **GPU**: Không bắt buộc (nhưng tăng tốc training)
- **Disk**: 2GB dung lượng trống

### Phần Mềm
- **Python**: 3.8, 3.9, 3.10, hoặc 3.11
- **pip**: 20.0+
- **Git**: (Tùy chọn) để clone repo

---

## 🚀 Cài Đặt

### Bước 1: Clone hoặc Download Project

**Option A: Sử dụng Git**
```bash
git clone https://github.com/your-repo/predict-future-import.git
cd predict-future-import
```

**Option B: Download ZIP**
1. Download ZIP từ GitHub
2. Giải nén vào thư mục
3. Mở terminal/cmd trong thư mục đó

---

### Bước 2: Tạo Virtual Environment (Khuyến nghị)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Bạn sẽ thấy `(venv)` xuất hiện ở đầu dòng lệnh.

---

### Bước 3: Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies chính:**
- `tensorflow>=2.10.0` - Deep Learning framework
- `flask>=2.3.0` - Web framework
- `opencv-python>=4.8.0` - Image processing
- `pillow>=10.0.0` - Image manipulation
- `pandas>=2.0.0` - Data processing
- `numpy>=1.24.0` - Numerical computing
- `scikit-learn>=1.3.0` - Machine learning utilities

**Nếu gặp lỗi:**

1. **Lỗi TensorFlow trên Windows:**
   ```bash
   pip install tensorflow-cpu  # Nếu không có GPU
   ```

2. **Lỗi OpenCV:**
   ```bash
   pip install opencv-python-headless
   ```

3. **Lỗi memory:**
   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

---

### Bước 4: Chuẩn Bị Dữ Liệu

#### 4.1. Kiểm tra Product Catalogs
```bash
# Kiểm tra file có tồn tại
ls data/product_catalogs.json  # Linux/Mac
dir data\product_catalogs.json  # Windows
```

File này chứa danh mục sản phẩm của 2 cửa hàng (Quán Sơn, Quán Tùng).

#### 4.2. Tạo Dataset Mẫu
```bash
python data/generate_dataset.py
```

Lệnh này tạo file `data/DATASET-tung1000.csv` với 1000 bản ghi hóa đơn mẫu.

---

### Bước 5: Khởi Tạo Models

#### Option A: Chạy ngay với Pre-trained Weights (nếu có)

Nếu folder `saved_models/` đã có file `.h5`:
```bash
python app.py
```

#### Option B: Train Models từ đầu

```bash
python train_models.py
```

**Quá trình training:**
1. LSTM Model: ~3-5 phút (50 epochs)
2. CNN Model: Khởi tạo architecture (~30 giây)

**Output:**
```
saved_models/
  ├── cnn_invoice_detector.h5
  ├── lstm_text_recognizer.h5
  └── lstm_text_recognizer_scaler.pkl
```

---

### Bước 6: Kiểm Tra Models

```bash
python test.py
```

**Kết quả mong đợi:**
```
🧪 TESTING DEEP LEARNING MODELS
============================================================
📦 Testing CNN Model...
   ✅ CNN Model built successfully
   Architecture: MobileNetV2 + Custom Head
   Total parameters: 2,859,XXX

📦 Testing LSTM Model...
   ✅ LSTM Model built successfully
   Architecture: Stacked LSTM with Attention
   Total parameters: 123,XXX

🔍 Testing CNN Prediction...
   ✅ CNN Prediction successful
   Products detected: 5
   Confidence: 87%

📊 Testing LSTM Prediction...
   ✅ LSTM Prediction successful
   Predicted quantity: 450 products
   Trend: increasing
   Confidence: 82%

✅ ALL TESTS COMPLETED
```

---

### Bước 7: Chạy Ứng Dụng

```bash
python app.py
```

**Output:**
```
======================================================================
INVOICE FORECAST SYSTEM - DEEP LEARNING DEMO
======================================================================
Model 1: CNN - Image Detection (Hoa don giay -> Hoa don dien tu)
Model 2: LSTM - Quantity Forecasting (Y1 + x2 + x3 -> Y2 TEXT)
======================================================================
Server: http://localhost:5000
======================================================================
```

Mở trình duyệt: **http://localhost:5000**

---

## 🔧 Cấu Hình

### Thay Đổi Port

**Trong `config.py`:**
```python
FLASK_PORT = 8080  # Thay đổi từ 5000
```

Hoặc trực tiếp trong `app.py`:
```python
app.run(debug=False, port=8080, host='127.0.0.1')
```

### Thay Đổi Model Parameters

**Trong `config.py`:**
```python
# Image settings
IMG_HEIGHT = 256  # Thay đổi từ 224
IMG_WIDTH = 256

# LSTM settings
LSTM_SEQUENCE_LENGTH = 15  # Thay đổi từ 10
LSTM_NUM_FEATURES = 5

# Training settings
EPOCHS = 100  # Thay đổi từ 50
BATCH_SIZE = 64  # Thay đổi từ 32
```

**Sau đó train lại:**
```bash
python train_models.py
```

### Thay Đổi Product Catalogs

Chỉnh sửa `data/product_catalogs.json`:
```json
{
  "son": [
    {
      "id": "SON001",
      "name": "Sản phẩm mới",
      "price": 50000
    }
  ],
  "tung": [...]
}
```

---

## 🐛 Xử Lý Lỗi Thường Gặp

### 1. Lỗi: "ModuleNotFoundError: No module named 'tensorflow'"

**Nguyên nhân:** Chưa cài TensorFlow

**Giải pháp:**
```bash
pip install tensorflow
# Hoặc nếu không có GPU:
pip install tensorflow-cpu
```

---

### 2. Lỗi: "OSError: [WinError 126] The specified module could not be found"

**Nguyên nhân:** Thiếu Visual C++ Redistributable (Windows)

**Giải pháp:**
1. Download [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Cài đặt
3. Khởi động lại terminal

---

### 3. Lỗi: "Failed to load model weights"

**Nguyên nhân:** Weights file bị corrupt hoặc sai version

**Giải pháp:**
```bash
# Xóa weights cũ
rm saved_models/*.h5  # Linux/Mac
del saved_models\*.h5  # Windows

# Train lại
python train_models.py
```

---

### 4. Lỗi: "CUDA out of memory" (GPU)

**Nguyên nhân:** GPU không đủ VRAM

**Giải pháp:**
```python
# Trong config.py, giảm batch size
BATCH_SIZE = 16  # Thay vì 32
```

Hoặc chuyển sang CPU:
```bash
pip uninstall tensorflow
pip install tensorflow-cpu
```

---

### 5. Lỗi: "Port 5000 already in use"

**Nguyên nhân:** Port đã bị chiếm bởi ứng dụng khác

**Giải pháp:**
```python
# Trong app.py, đổi port
app.run(debug=False, port=8080, host='127.0.0.1')
```

---

### 6. Lỗi: "No invoice history" khi forecast

**Nguyên nhân:** Chưa upload hóa đơn qua Model 1

**Giải pháp:**
1. Upload ít nhất 10 ảnh hóa đơn qua `/api/model1/detect`
2. Hoặc nhập dữ liệu manual trong `/api/model2/forecast`

---

## 📊 Kiểm Tra Cài Đặt

### Quick Health Check

```bash
python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}')"
python -c "import flask; print(f'Flask: {flask.__version__}')"
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
```

**Output mong đợi:**
```
TensorFlow: 2.15.0
Flask: 2.3.3
OpenCV: 4.8.1
```

---

## 🎓 Nâng Cao

### Chạy với Production Server

**Sử dụng Gunicorn (Linux/Mac):**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Sử dụng Waitress (Windows):**
```bash
pip install waitress
waitress-serve --port=5000 app:app
```

### Docker Deployment

```bash
# Build image
docker build -t invoice-prediction .

# Run container
docker run -p 5000:5000 invoice-prediction
```

### Enable Debug Mode

**Chỉ dùng trong development:**
```python
# Trong app.py
app.run(debug=True, port=5000)
```

---

## ✅ Hoàn Tất

Sau khi hoàn thành setup:
1. ✅ Dependencies đã cài
2. ✅ Dataset đã tạo
3. ✅ Models đã train hoặc load
4. ✅ App chạy thành công
5. ✅ Tests pass

**Next steps:**
- Đọc [API_GUIDE.md](API_GUIDE.md) để sử dụng API
- Đọc [MODEL_DOCS.md](MODEL_DOCS.md) để hiểu architecture
- Upload hóa đơn thật để test

---

## 💬 Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra [Common Errors](#-xử-lý-lỗi-thường-gặp)
2. Xem logs trong terminal
3. Mở issue trên GitHub
