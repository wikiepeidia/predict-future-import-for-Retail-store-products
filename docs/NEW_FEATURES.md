# New Features Documentation

## Tổng Quan Chức Năng Mới

Project đã được nâng cấp với 5 chức năng chính:

### 1. 📝 **Logging System** - Hệ Thống Ghi Log

**File:** `utils/logger.py`

**Chức năng:**
- Ghi log chi tiết mọi hoạt động của system
- Tự động phân loại log theo mức độ (DEBUG, INFO, WARNING, ERROR)
- Lưu log vào files với rotation (tự động tạo file mới khi đầy)
- 3 loại log files:
  - `logs/app.log` - Tất cả logs
  - `logs/error.log` - Chỉ errors
  - `logs/api.log` - API requests

**Sử dụng:**
```python
from utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Processing started")
logger.error("Something went wrong")
```

**API Logging:**
```python
from utils.logger import log_api_request

log_api_request('/api/model1/detect', 'POST', 
               params={'file': 'invoice.jpg'},
               status_code=200, duration=1234)
```

---

### 2. ✅ **Validators** - Kiểm Tra Dữ Liệu Đầu Vào

**File:** `utils/validators.py`

**Chức năng:**
- Validate uploaded files (type, size, content)
- Validate invoice data format
- Validate quantities and store keys
- Sanitize filenames để bảo mật

**Validators có sẵn:**

```python
from utils.validators import (
    validate_image_file,      # Kiểm tra file ảnh
    validate_invoice_data,    # Kiểm tra invoice data
    validate_quantity,        # Kiểm tra số lượng
    validate_store_key,       # Kiểm tra store
    sanitize_filename        # Làm sạch tên file
)
```

**Ví dụ:**
```python
# Validate file upload
try:
    validate_image_file(file)
    # File hợp lệ, tiếp tục xử lý
except ValidationError as e:
    return jsonify({'error': str(e)}), 400

# Validate invoice data
validate_invoice_data("Product A - 50\nProduct B - 30")
```

---

### 3. 🛡️ **Error Handlers** - Xử Lý Lỗi

**File:** `utils/error_handlers.py`

**Chức năng:**
- Tự động catch và xử lý mọi lỗi HTTP
- Trả về JSON response thống nhất
- Log errors chi tiết
- Ẩn thông tin nhạy cảm trong production

**Errors được xử lý:**
- 400 Bad Request
- 404 Not Found
- 405 Method Not Allowed
- 413 Request Entity Too Large
- 500 Internal Server Error
- Tất cả exceptions khác

**Custom Errors:**
```python
from utils.error_handlers import ValidationError, NotFoundError

raise ValidationError("Invalid input")
raise NotFoundError("Invoice not found")
```

---

### 4. 💾 **Database** - Lưu Trữ Persistent

**File:** `utils/database.py`

**Chức năng:**
- SQLite database để lưu invoices và forecasts
- Tự động tạo tables khi khởi động
- Context manager để quản lý connections
- Functions để CRUD operations

**Database Schema:**

**Table: invoices**
```sql
- id (INTEGER PRIMARY KEY)
- invoice_id (TEXT UNIQUE)
- store_name (TEXT)
- store_key (TEXT)
- total_amount (REAL)
- confidence (REAL)
- products (TEXT JSON)
- extracted_text (TEXT)
- created_at (TIMESTAMP)
```

**Table: forecasts**
```sql
- id (INTEGER PRIMARY KEY)
- predicted_quantity (INTEGER)
- trend (TEXT)
- confidence (REAL)
- recommendation (TEXT)
- history_count (INTEGER)
- created_at (TIMESTAMP)
```

**Functions:**
```python
from utils.database import (
    init_database,              # Khởi tạo DB
    save_invoice_to_db,         # Lưu invoice
    save_forecast_to_db,        # Lưu forecast
    get_invoices_from_db,       # Lấy invoices
    get_forecasts_from_db,      # Lấy forecasts
    get_invoice_by_id,          # Tìm invoice
    get_statistics,             # Thống kê
    clear_database              # Xóa data
)
```

**Ví dụ:**
```python
# Lưu invoice
save_invoice_to_db(invoice_data)

# Lấy invoices (pagination)
invoices = get_invoices_from_db(limit=100, offset=0)

# Thống kê
stats = get_statistics()
# Returns: {
#   'total_invoices': 150,
#   'total_forecasts': 50,
#   'total_amount': 45000,
#   'average_confidence': 0.92
# }
```

---

### 5. 📊 **Export Utils** - Xuất Dữ Liệu

**File:** `utils/export_utils.py`

**Chức năng:**
- Export data sang JSON, CSV, Excel
- Tạo summary reports với multiple sheets
- Tự động handle nested objects
- UTF-8 encoding cho tiếng Việt

**Export Formats:**
- JSON - Dữ liệu structured
- CSV - Dùng với Excel, Google Sheets
- Excel - Multiple sheets, formatting

**Functions:**
```python
from utils.export_utils import (
    export_to_json,           # Export JSON
    export_to_csv,            # Export CSV
    export_to_excel,          # Export Excel
    export_invoices,          # Export invoices
    export_forecasts,         # Export forecasts
    create_summary_report     # Tạo report tổng hợp
)
```

**Ví dụ:**
```python
# Export invoices to CSV
filepath = export_invoices(invoices, format='csv')

# Export forecasts to Excel
filepath = export_forecasts(forecasts, format='excel')

# Tạo summary report
filepath = create_summary_report(
    invoices=invoices,
    forecasts=forecasts,
    statistics=stats
)
```

---

## 🔌 New API Endpoints

### Model 1 (CNN) - Invoice Detection

**1. Detect Invoice** (đã có, đã nâng cấp)
```
POST /api/model1/detect
Content-Type: multipart/form-data

Body:
- file: <image file>

Response: {
  "success": true,
  "invoice_id": "INV-20250120-001",
  "store_name": "Cửa Hàng Tùng",
  "detection_confidence": 0.87,
  "products": [...],
  ...
}
```

**2. Export Invoices** (MỚI)
```
GET /api/model1/export?format=json

Params:
- format: json|csv|excel (default: json)

Response: {
  "success": true,
  "message": "Exported 150 invoices",
  "file": "exports/invoices_20250120_143022.json",
  "format": "json"
}
```

### Model 2 (LSTM) - Forecasting

**1. Forecast Quantity** (đã có, đã nâng cấp)
```
POST /api/model2/forecast
Content-Type: application/json

Body: {
  "invoice_data": "Product A - 50\nProduct B - 30"
}

Response: {
  "success": true,
  "predicted_quantity": 338,
  "trend": "stable",
  "confidence": 0.85,
  ...
}
```

**2. Export Forecasts** (MỚI)
```
GET /api/model2/export?format=csv

Params:
- format: json|csv|excel (default: json)

Response: {
  "success": true,
  "message": "Exported 50 forecasts",
  "file": "exports/forecasts_20250120_143022.csv",
  "format": "csv"
}
```

### History & Stats

**1. Get History (Memory)** (đã có)
```
GET /api/history
```

**2. Get Database History** (MỚI)
```
GET /api/history/database?limit=100&offset=0

Params:
- limit: Number of records (default: 100)
- offset: Offset for pagination (default: 0)

Response: {
  "success": true,
  "invoices": {
    "count": 150,
    "data": [...]
  },
  "forecasts": {
    "count": 50,
    "data": [...]
  }
}
```

**3. Clear History** (đã nâng cấp)
```
POST /api/history/clear?database=true

Params:
- database: true|false (clear DB too?)

Response: {
  "success": true,
  "message": "Cleared 10 invoices",
  "database_cleared": true
}
```

**4. Get Statistics** (MỚI)
```
GET /api/statistics

Response: {
  "success": true,
  "statistics": {
    "total_invoices": 150,
    "total_forecasts": 50,
    "total_amount": 45000.0,
    "average_confidence": 0.92
  }
}
```

**5. Export Summary Report** (MỚI)
```
GET /api/export/summary

Response: {
  "success": true,
  "message": "Summary report created",
  "file": "exports/summary_report_20250120_143022.xlsx"
}
```

**6. Get Models Info** (đã có)
```
GET /api/models/info
```

---

## 📁 File Structure (Updated)

```
project/
├── app.py                        # Main app (đã nâng cấp)
├── config.py                     # Configuration
├── train_models.py               # Training script
│
├── api/                          # API Routes (đã nâng cấp)
│   ├── model1_routes.py          # + Export endpoint
│   ├── model2_routes.py          # + Export endpoint
│   └── history_routes.py         # + 4 endpoints mới
│
├── services/                     # Business Logic
│   ├── model_loader.py           # Model management
│   ├── invoice_service.py        # Invoice processing
│   └── forecast_service.py       # Forecast logic
│
├── models/                       # ML Models
│   ├── cnn_model.py             # CNN model
│   └── lstm_model.py            # LSTM model
│
├── utils/                        # Utilities (MỚI)
│   ├── __init__.py
│   ├── logger.py                # ✨ Logging system
│   ├── validators.py            # ✨ Input validation
│   ├── error_handlers.py        # ✨ Error handling
│   ├── database.py              # ✨ SQLite database
│   ├── export_utils.py          # ✨ Export utilities
│   ├── data_processor.py        # Data processing
│   └── invoice_processor.py     # Invoice processing
│
├── data/                         # Data files
├── static/                       # CSS, JS
├── ui/templates/                 # HTML templates
│
├── database/                     # ✨ Database files (MỚI)
│   └── invoices.db              # SQLite database
│
├── logs/                         # ✨ Log files (MỚI)
│   ├── app.log                  # All logs
│   ├── error.log                # Error logs only
│   └── api.log                  # API requests
│
└── exports/                      # ✨ Exported files (MỚI)
    ├── invoices_*.json/csv/xlsx
    ├── forecasts_*.json/csv/xlsx
    └── summary_report_*.xlsx
```

---

## 🚀 Cách Sử Dụng

### 1. Chạy Application

```bash
python app.py
```

Server sẽ start với:
- Logging system đã kích hoạt
- Database đã khởi tạo
- Error handlers đã đăng ký
- Tất cả endpoints sẵn sàng

### 2. Xem Logs

Logs được lưu tự động trong folder `logs/`:
```bash
# Xem all logs
cat logs/app.log

# Xem chỉ errors
cat logs/error.log

# Follow logs realtime
tail -f logs/app.log
```

### 3. Kiểm Tra Database

```bash
# Dùng SQLite client
sqlite3 database/invoices.db

# Trong SQLite shell
.tables                    # Liệt kê tables
SELECT * FROM invoices;    # Xem invoices
SELECT * FROM forecasts;   # Xem forecasts
```

### 4. Export Data

**Via API:**
```bash
# Export invoices to JSON
curl http://localhost:5000/api/model1/export?format=json

# Export forecasts to CSV
curl http://localhost:5000/api/model2/export?format=csv

# Export summary report
curl http://localhost:5000/api/export/summary
```

**Via Python:**
```python
from utils.export_utils import export_invoices
from utils.database import get_invoices_from_db

invoices = get_invoices_from_db()
filepath = export_invoices(invoices, format='excel')
print(f"Exported to: {filepath}")
```

### 5. Xem Statistics

```bash
curl http://localhost:5000/api/statistics
```

---

## 🔧 Configuration

Tất cả config trong `config.py`:

```python
# Logging
LOGS_DIR = BASE_DIR / 'logs'

# Database
DB_DIR = BASE_DIR / 'database'
DB_PATH = DB_DIR / 'invoices.db'

# Exports
EXPORTS_DIR = BASE_DIR / 'exports'

# Validation
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
```

---

## ✨ Benefits

### Trước khi có features mới:
- ❌ Không có logging → khó debug
- ❌ Không validate input → dễ lỗi
- ❌ Lỗi không được xử lý tốt → crash
- ❌ Data mất khi restart → không persistent
- ❌ Không thể export data → khó phân tích

### Sau khi có features mới:
- ✅ Logging đầy đủ → dễ debug và monitor
- ✅ Validate tất cả inputs → ít lỗi hơn
- ✅ Error handling tốt → không crash
- ✅ Database persistent → data không mất
- ✅ Export nhiều formats → dễ phân tích

---

## 📝 Example Workflow

```python
# 1. Upload invoice
response = requests.post(
    'http://localhost:5000/api/model1/detect',
    files={'file': open('invoice.jpg', 'rb')}
)
# → Tự động: validate file, log request, save to DB

# 2. Forecast
response = requests.post(
    'http://localhost:5000/api/model2/forecast',
    json={'invoice_data': 'Product A - 50'}
)
# → Tự động: validate data, log request, save to DB

# 3. View statistics
response = requests.get('http://localhost:5000/api/statistics')
# → Returns: total invoices, forecasts, amount, confidence

# 4. Export all data
response = requests.get('http://localhost:5000/api/export/summary')
# → Creates Excel file với 3 sheets: Summary, Invoices, Forecasts

# 5. Check logs
# → All operations logged in logs/app.log
```

---

## 🎯 Next Steps

Có thể thêm:
1. **Authentication** - User login/register
2. **Rate Limiting** - Giới hạn requests
3. **Caching** - Cache predictions
4. **Webhooks** - Notify khi có forecast mới
5. **Dashboard** - Web UI để xem statistics
6. **Scheduled Jobs** - Auto export hàng ngày
7. **Email Reports** - Gửi reports qua email

---

Tất cả chức năng đã hoạt động và sẵn sàng sử dụng! 🎉
