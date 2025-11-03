# API Reference - Complete Documentation

## Base URL
```
http://localhost:5000
```

---

## 📋 Table of Contents

1. [Model 1 - Invoice Detection](#model-1---invoice-detection)
2. [Model 2 - Forecasting](#model-2---forecasting)
3. [History & Statistics](#history--statistics)
4. [Error Handling](#error-handling)
5. [Response Formats](#response-formats)

---

## Model 1 - Invoice Detection

### 1.1 Detect Invoice from Image

Phát hiện và trích xuất thông tin từ hóa đơn giấy.

**Endpoint:** `POST /api/model1/detect`

**Request:**
```http
POST /api/model1/detect HTTP/1.1
Content-Type: multipart/form-data

file=<binary image data>
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/model1/detect \
  -F "file=@invoice.jpg"
```

**Python Example:**
```python
import requests

with open('invoice.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/model1/detect',
        files={'file': f}
    )
    
print(response.json())
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Invoice detected successfully",
  "invoice_id": "INV-20250120-001",
  "store_name": "Cửa Hàng Tùng",
  "store_key": "tung",
  "detection_confidence": 0.8633,
  "total_amount": 450.0,
  "products": [
    {
      "name": "Product A",
      "quantity": 50,
      "price": 5.0
    },
    {
      "name": "Product B",
      "quantity": 30,
      "price": 10.0
    }
  ],
  "extracted_text": "Cửa Hàng Tùng\nProduct A: 50\nProduct B: 30\n...",
  "timestamp": "2025-01-20T14:30:22"
}
```

**Response (Error - 400):**
```json
{
  "success": false,
  "message": "Invalid file extension 'txt'. Allowed: png, jpg, jpeg, gif, webp, pdf"
}
```

**Validation Rules:**
- File required
- Allowed extensions: `png`, `jpg`, `jpeg`, `gif`, `webp`, `pdf`
- Max file size: 16MB
- File must not be empty

---

### 1.2 Export Invoices

Export danh sách invoices sang file.

**Endpoint:** `GET /api/model1/export`

**Parameters:**
| Parameter | Type   | Required | Default | Description                |
|-----------|--------|----------|---------|----------------------------|
| format    | string | No       | json    | Export format: json/csv/excel |

**Request:**
```http
GET /api/model1/export?format=csv HTTP/1.1
```

**cURL Example:**
```bash
# Export to JSON
curl http://localhost:5000/api/model1/export?format=json

# Export to CSV
curl http://localhost:5000/api/model1/export?format=csv

# Export to Excel
curl http://localhost:5000/api/model1/export?format=excel
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Exported 150 invoices",
  "file": "exports/invoices_20250120_143022.json",
  "format": "json"
}
```

**Response (No Data - 404):**
```json
{
  "success": false,
  "message": "No invoices to export"
}
```

---

## Model 2 - Forecasting

### 2.1 Forecast Quantity

Dự đoán số lượng sản phẩm cần nhập dựa trên lịch sử.

**Endpoint:** `POST /api/model2/forecast`

**Request:**
```http
POST /api/model2/forecast HTTP/1.1
Content-Type: application/json

{
  "invoice_data": "Product A - 50\nProduct B - 30\nProduct C - 20"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/model2/forecast \
  -H "Content-Type: application/json" \
  -d '{"invoice_data": "Product A - 50\nProduct B - 30"}'
```

**Python Example:**
```python
import requests

data = {
    'invoice_data': 'Product A - 50\nProduct B - 30\nProduct C - 20'
}

response = requests.post(
    'http://localhost:5000/api/model2/forecast',
    json=data
)

print(response.json())
```

**Request Body (Optional):**
| Field         | Type   | Required | Description                          |
|---------------|--------|----------|--------------------------------------|
| invoice_data  | string | No       | Manual invoice data (one per line)   |

**Invoice Data Format:**
```
Product Name - Quantity
Product Name: Quantity
```

**Example:**
```
Coca Cola - 50
Pepsi: 30
Sprite - 25
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Forecast completed successfully",
  "predicted_quantity": 338,
  "trend": "stable",
  "confidence": 0.85,
  "recommendation": "moderate_increase",
  "recommendation_text": "Tăng nhẹ số lượng nhập kho",
  "history_count": 5,
  "timestamp": "2025-01-20T14:35:10"
}
```

**Trend Values:**
- `increasing` - Xu hướng tăng
- `stable` - Ổn định
- `decreasing` - Xu hướng giảm

**Recommendation Values:**
- `maintain` - Giữ nguyên
- `slight_increase` - Tăng nhẹ
- `moderate_increase` - Tăng vừa phải
- `significant_increase` - Tăng mạnh
- `decrease` - Giảm

**Response (Error - 400):**
```json
{
  "success": false,
  "message": "Invalid format. Use: \"Product Name - Quantity\" (one per line)"
}
```

**Validation Rules:**
- If no `invoice_data` provided, must have invoice history
- Format: "Product Name - Quantity" or "Product Name: Quantity"
- Quantity must be positive integer
- At least 1 valid product line required

---

### 2.2 Export Forecasts

Export danh sách forecasts sang file.

**Endpoint:** `GET /api/model2/export`

**Parameters:**
| Parameter | Type   | Required | Default | Description                |
|-----------|--------|----------|---------|----------------------------|
| format    | string | No       | json    | Export format: json/csv/excel |

**Request:**
```http
GET /api/model2/export?format=excel HTTP/1.1
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Exported 50 forecasts",
  "file": "exports/forecasts_20250120_143022.xlsx",
  "format": "excel"
}
```

---

## History & Statistics

### 3.1 Get Invoice History (Memory)

Lấy lịch sử invoices từ memory (legacy).

**Endpoint:** `GET /api/history`

**Request:**
```http
GET /api/history HTTP/1.1
```

**Response (Success - 200):**
```json
{
  "success": true,
  "count": 10,
  "history": [
    {
      "invoice_id": "INV-20250120-001",
      "store_name": "Cửa Hàng Tùng",
      "total_amount": 450.0,
      "timestamp": "2025-01-20T14:30:22"
    }
  ]
}
```

---

### 3.2 Get Database History

Lấy lịch sử invoices và forecasts từ database với pagination.

**Endpoint:** `GET /api/history/database`

**Parameters:**
| Parameter | Type    | Required | Default | Description              |
|-----------|---------|----------|---------|--------------------------|
| limit     | integer | No       | 100     | Number of records        |
| offset    | integer | No       | 0       | Offset for pagination    |

**Request:**
```http
GET /api/history/database?limit=50&offset=0 HTTP/1.1
```

**cURL Example:**
```bash
# Get first 100 records
curl http://localhost:5000/api/history/database

# Get next 50 records
curl http://localhost:5000/api/history/database?limit=50&offset=50
```

**Response (Success - 200):**
```json
{
  "success": true,
  "invoices": {
    "count": 50,
    "data": [
      {
        "id": 1,
        "invoice_id": "INV-20250120-001",
        "store_name": "Cửa Hàng Tùng",
        "store_key": "tung",
        "total_amount": 450.0,
        "confidence": 0.8633,
        "products": [
          {"name": "Product A", "quantity": 50, "price": 5.0}
        ],
        "extracted_text": "...",
        "created_at": "2025-01-20 14:30:22"
      }
    ]
  },
  "forecasts": {
    "count": 20,
    "data": [
      {
        "id": 1,
        "predicted_quantity": 338,
        "trend": "stable",
        "confidence": 0.85,
        "recommendation": "Tăng nhẹ số lượng nhập kho",
        "history_count": 5,
        "created_at": "2025-01-20 14:35:10"
      }
    ]
  }
}
```

---

### 3.3 Clear History

Xóa lịch sử invoices (memory và/hoặc database).

**Endpoint:** `POST /api/history/clear`

**Parameters:**
| Parameter | Type    | Required | Default | Description              |
|-----------|---------|----------|---------|--------------------------|
| database  | boolean | No       | false   | Also clear database?     |

**Request:**
```http
POST /api/history/clear?database=true HTTP/1.1
```

**cURL Example:**
```bash
# Clear memory only
curl -X POST http://localhost:5000/api/history/clear

# Clear memory and database
curl -X POST http://localhost:5000/api/history/clear?database=true
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Cleared 10 invoices",
  "database_cleared": true
}
```

---

### 3.4 Get Statistics

Lấy thống kê tổng quan từ database.

**Endpoint:** `GET /api/statistics`

**Request:**
```http
GET /api/statistics HTTP/1.1
```

**Response (Success - 200):**
```json
{
  "success": true,
  "statistics": {
    "total_invoices": 150,
    "total_forecasts": 50,
    "total_amount": 45000.0,
    "average_confidence": 0.92
  }
}
```

---

### 3.5 Export Summary Report

Tạo báo cáo tổng hợp Excel với nhiều sheets.

**Endpoint:** `GET /api/export/summary`

**Request:**
```http
GET /api/export/summary HTTP/1.1
```

**Response (Success - 200):**
```json
{
  "success": true,
  "message": "Summary report created",
  "file": "exports/summary_report_20250120_143022.xlsx"
}
```

**Excel File Contains:**
- Sheet 1: Summary - Thống kê tổng quan
- Sheet 2: Invoices - Tất cả invoices
- Sheet 3: Forecasts - Tất cả forecasts

---

### 3.6 Get Models Info

Lấy thông tin về models đã load.

**Endpoint:** `GET /api/models/info`

**Request:**
```http
GET /api/models/info HTTP/1.1
```

**Response (Success - 200):**
```json
{
  "success": true,
  "models": {
    "cnn": {
      "loaded": true,
      "type": "MobileNetV2",
      "input_shape": [224, 224, 3],
      "classes": 2
    },
    "lstm": {
      "loaded": true,
      "type": "LSTM",
      "sequence_length": 10,
      "features": 1
    }
  },
  "invoice_history_count": 10
}
```

---

### 3.7 Health Check

Kiểm tra server status.

**Endpoint:** `GET /health`

**Request:**
```http
GET /health HTTP/1.1
```

**Response (Success - 200):**
```json
{
  "status": "healthy",
  "service": "Retail Prediction System"
}
```

---

## Error Handling

### Standard Error Response

All errors return JSON with consistent structure:

```json
{
  "success": false,
  "error": "Error Type",
  "message": "Detailed error message"
}
```

### HTTP Status Codes

| Code | Description              | Example                          |
|------|--------------------------|----------------------------------|
| 200  | Success                  | Request processed successfully   |
| 400  | Bad Request              | Invalid input data               |
| 404  | Not Found                | Resource not found               |
| 405  | Method Not Allowed       | Wrong HTTP method                |
| 413  | Request Entity Too Large | File too large                   |
| 500  | Internal Server Error    | Unexpected server error          |
| 501  | Not Implemented          | Feature not implemented          |

### Common Error Messages

**400 Bad Request:**
```json
{
  "success": false,
  "message": "No file provided"
}
```

```json
{
  "success": false,
  "message": "Invalid file extension 'txt'. Allowed: png, jpg, jpeg, gif, webp, pdf"
}
```

```json
{
  "success": false,
  "message": "File too large (20971520 bytes). Max: 16777216 bytes"
}
```

**404 Not Found:**
```json
{
  "success": false,
  "error": "Not Found",
  "message": "The requested resource was not found"
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Internal Server Error",
  "message": "An unexpected error occurred. Please try again later."
}
```

---

## Response Formats

### Export Formats

#### JSON
```json
[
  {
    "invoice_id": "INV-20250120-001",
    "store_name": "Cửa Hàng Tùng",
    "total_amount": 450.0
  }
]
```

#### CSV
```csv
invoice_id,store_name,total_amount
INV-20250120-001,Cửa Hàng Tùng,450.0
INV-20250120-002,Cửa Hàng Sơn,320.0
```

#### Excel
- Multiple sheets support
- Formatted headers
- UTF-8 encoding for Vietnamese

---

## Rate Limiting

Currently not implemented. Will be added in future versions.

---

## Authentication

Currently not implemented. All endpoints are public.

---

## Examples

### Complete Workflow

```python
import requests

BASE_URL = 'http://localhost:5000'

# 1. Upload invoice
with open('invoice.jpg', 'rb') as f:
    response = requests.post(
        f'{BASE_URL}/api/model1/detect',
        files={'file': f}
    )
    invoice = response.json()
    print(f"Invoice detected: {invoice['invoice_id']}")

# 2. Forecast
data = {'invoice_data': 'Product A - 50\nProduct B - 30'}
response = requests.post(
    f'{BASE_URL}/api/model2/forecast',
    json=data
)
forecast = response.json()
print(f"Predicted quantity: {forecast['predicted_quantity']}")

# 3. Get statistics
response = requests.get(f'{BASE_URL}/api/statistics')
stats = response.json()['statistics']
print(f"Total invoices: {stats['total_invoices']}")

# 4. Export summary
response = requests.get(f'{BASE_URL}/api/export/summary')
report = response.json()
print(f"Report created: {report['file']}")
```

---

## Testing

### Using cURL

```bash
# Test Model 1
curl -X POST http://localhost:5000/api/model1/detect \
  -F "file=@test_invoice.jpg"

# Test Model 2
curl -X POST http://localhost:5000/api/model2/forecast \
  -H "Content-Type: application/json" \
  -d '{"invoice_data": "Product A - 50"}'

# Test Statistics
curl http://localhost:5000/api/statistics

# Test Export
curl http://localhost:5000/api/model1/export?format=csv
```

### Using Postman

1. Import collection from `postman_collection.json` (if available)
2. Or create requests manually using examples above

---

## Changelog

### Version 2.0 (Current)
- ✨ Added logging system
- ✨ Added input validation
- ✨ Added error handlers
- ✨ Added database support
- ✨ Added export functionality
- ✨ New endpoints: export, statistics, database history
- 🔧 Enhanced existing endpoints with validation
- 📝 Complete API documentation

### Version 1.0
- Basic invoice detection
- Basic forecasting
- Simple history management

---

## Support

For issues or questions:
1. Check logs in `logs/` folder
2. Check database in `database/invoices.db`
3. Review this documentation
4. Contact development team

---

Last Updated: 2025-01-20
