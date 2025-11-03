# 📚 API Documentation - Invoice Prediction System

## Base URL
```
http://localhost:5000
```

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Homepage - Web UI |
| POST | `/api/model1/detect` | Nhận diện hóa đơn bằng CNN |
| POST | `/api/model2/forecast` | Dự đoán số lượng nhập hàng |
| GET | `/api/history` | Xem lịch sử hóa đơn |
| POST | `/api/history/clear` | Xóa lịch sử |
| GET | `/api/models/info` | Thông tin models |

---

## 1. Invoice Detection (Model 1 - CNN)

### POST `/api/model1/detect`

Nhận diện hóa đơn giấy và chuyển thành dữ liệu điện tử.

**Request:**
```http
POST /api/model1/detect
Content-Type: multipart/form-data

Body:
  image: <file> (PNG, JPG, JPEG, PDF)
```

**Python Example:**
```python
import requests

url = "http://localhost:5000/api/model1/detect"
files = {'image': open('invoice.jpg', 'rb')}
response = requests.post(url, files=files)
data = response.json()
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/model1/detect \
  -F "image=@invoice.jpg"
```

**Response:**
```json
{
  "success": true,
  "recognized_text": "Invoice ID: INV_54321\nStore: Quán Sơn\n\nProducts:\nCoca Cola 330ml - 20\nBánh mì thịt - 15\n\nTotal: 650,000 VND",
  "confidence": 0.87,
  "data": {
    "invoice_id": "INV_54321",
    "store_name": "Quán Sơn",
    "store_key": "son",
    "products": [
      {
        "product_id": "SON001",
        "product_name": "Coca Cola 330ml",
        "quantity": 20,
        "unit_price": 12000,
        "line_total": 240000
      },
      {
        "product_id": "SON015",
        "product_name": "Bánh mì thịt",
        "quantity": 15,
        "unit_price": 25000,
        "line_total": 375000
      }
    ],
    "total_amount": 615000,
    "detection_confidence": 0.87,
    "text_regions_count": 5,
    "extracted_text": "...",
    "date": "2025-11-03T14:30:45.123456"
  },
  "total_history_count": 12
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "No image provided"
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid request (no file, wrong format)
- `500`: Server error

---

## 2. Quantity Forecasting (Model 2 - LSTM)

### POST `/api/model2/forecast`

Dự đoán số lượng nhập hàng dựa trên lịch sử.

**Request:**
```http
POST /api/model2/forecast
Content-Type: application/json

Body:
{
  "invoice_data": "Optional: Manual invoice text input"
}
```

**Option 1: Sử dụng lịch sử tự động**
```python
import requests

url = "http://localhost:5000/api/model2/forecast"
response = requests.post(url, json={})
data = response.json()
```

**Option 2: Nhập thủ công**
```python
import requests

url = "http://localhost:5000/api/model2/forecast"
payload = {
  "invoice_data": "Coca Cola - 50\nBánh mì - 30\nCà phê - 20"
}
response = requests.post(url, json=payload)
data = response.json()
```

**Response:**
```json
{
  "success": true,
  "output1": "Predicted total quantity: 450 products",
  "output2": "Dự đoán số lượng nhập hàng kỳ tiếp: 450 sản phẩm\n\n📈 Xu hướng: TĂNG - Nhu cầu đang tăng lên theo thời gian\nKhuyến nghị: Nên nhập nhiều hơn mức trung bình (380 sp)\n\n🏆 Top sản phẩm cần nhập:\n1. Coca Cola 330ml: ~120 sp\n2. Bánh mì thịt: ~85 sp\n3. Cà phê sữa: ~70 sp",
  "confidence": 0.82,
  "data": {
    "predicted_quantity": 450,
    "recommendation_text": "...",
    "confidence": 0.82,
    "historical_avg": 380,
    "trend": "increasing"
  },
  "history_count": 15
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "No invoice history. Please upload invoices first using Model 1 or provide manual invoice data."
}
```

**Status Codes:**
- `200`: Success
- `400`: No history available
- `500`: Server error

---

## 3. History Management

### GET `/api/history`

Lấy lịch sử hóa đơn.

**Request:**
```http
GET /api/history
```

**Response:**
```json
{
  "success": true,
  "count": 15,
  "invoices": [
    {
      "invoice_id": "INV_12345",
      "store_name": "Quán Sơn",
      "products": [...],
      "total_amount": 850000,
      "date": "2025-11-03T10:15:30"
    },
    // ... 9 more recent invoices
  ]
}
```

### POST `/api/history/clear`

Xóa toàn bộ lịch sử hóa đơn.

**Request:**
```http
POST /api/history/clear
```

**Response:**
```json
{
  "success": true,
  "message": "Invoice history cleared"
}
```

---

## 4. Model Information

### GET `/api/models/info`

Lấy thông tin về các models đã load.

**Request:**
```http
GET /api/models/info
```

**Response:**
```json
{
  "success": true,
  "models": {
    "model1_cnn": {
      "name": "Invoice OCR Model (CNN + OCR)",
      "input": "x1 - Hóa đơn giấy (invoice image)",
      "output": "Y1 - Hóa đơn điện tử nhập hàng",
      "architecture": "MobileNetV2 Transfer Learning + Custom Detection Head",
      "status": "Ready",
      "image_size": "224x224",
      "weights": "d:\\...\\saved_models\\cnn_invoice_detector.h5"
    },
    "model2_lstm": {
      "name": "Import Forecast LSTM",
      "input": "Structured invoice history (quantity, price, sales, stock, demand)",
      "output": "Predicted import quantity & confidence",
      "architecture": "Stacked LSTM for time-series forecasting",
      "status": "Ready",
      "lookback": 10,
      "features": 5,
      "weights": "d:\\...\\saved_models\\lstm_text_recognizer.h5"
    }
  },
  "invoice_history_count": 15
}
```

---

## Common Response Fields

### Success Response Structure
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message"
}
```

### Error Response Structure
```json
{
  "success": false,
  "message": "Error description"
}
```

---

## Data Types

### Invoice Object
```typescript
{
  invoice_id: string,           // e.g., "INV_12345"
  store_name: string,           // e.g., "Quán Sơn"
  store_key: string,            // e.g., "son" or "tung"
  products: Product[],          // Array of products
  total_amount: number,         // Total in VND
  detection_confidence: number, // 0.0 - 1.0
  text_regions_count: number,   // Number of detected regions
  extracted_text: string,       // Raw OCR text
  date: string                  // ISO 8601 datetime
}
```

### Product Object
```typescript
{
  product_id: string,      // e.g., "SON001"
  product_name: string,    // e.g., "Coca Cola 330ml"
  quantity: number,        // e.g., 20
  unit_price: number,      // Price per unit in VND
  line_total: number       // quantity × unit_price
}
```

### Forecast Object
```typescript
{
  predicted_quantity: number,     // Số lượng dự đoán
  recommendation_text: string,    // Khuyến nghị chi tiết (Vietnamese)
  confidence: number,             // Độ tin cậy 0.0 - 1.0
  historical_avg: number,         // Trung bình lịch sử
  trend: "increasing" | "decreasing" | "stable"
}
```

---

## Complete Workflow Example

```python
import requests
import time

BASE_URL = "http://localhost:5000"

# Step 1: Upload invoices (Model 1)
for invoice_img in ['invoice1.jpg', 'invoice2.jpg', 'invoice3.jpg']:
    files = {'image': open(invoice_img, 'rb')}
    response = requests.post(f"{BASE_URL}/api/model1/detect", files=files)
    print(f"Uploaded {invoice_img}: {response.json()['success']}")
    time.sleep(1)

# Step 2: Check history
history = requests.get(f"{BASE_URL}/api/history").json()
print(f"Total invoices: {history['count']}")

# Step 3: Get forecast (Model 2)
forecast = requests.post(f"{BASE_URL}/api/model2/forecast", json={}).json()
print(f"Predicted quantity: {forecast['data']['predicted_quantity']}")
print(f"Trend: {forecast['data']['trend']}")
print(f"\nRecommendation:\n{forecast['output2']}")

# Step 4: Clear history (optional)
# requests.post(f"{BASE_URL}/api/history/clear")
```

---

## Notes

- Tất cả responses đều support UTF-8 (tiếng Việt)
- File upload giới hạn: PNG, JPG, JPEG, GIF, WEBP, PDF
- Lịch sử tối đa: 300 hóa đơn (cũ nhất bị xóa tự động)
- LSTM cần tối thiểu 10 hóa đơn để dự đoán chính xác
- Models có thể chạy với weights chưa train (demo mode)

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (missing params, invalid file) |
| 500 | Internal Server Error |
| 501 | Not Implemented |
