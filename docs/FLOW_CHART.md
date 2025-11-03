# System Flow Chart - Invoice Forecast System

## 📊 INVOICE FORECAST SYSTEM FLOW CHART
**PREDICT FUTURE IMPORTS WITH 2 MODELS**

---

## 🔄 Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  DATASET                    MODEL 1: CNN              INVOICE HISTORY  │
│  ┌──────────┐              ┌──────────┐              DATABASE          │
│  │• Sơn     │──x1:Images──▶│Image     │─Y1 Output──▶┌──────────┐     │
│  │• Tùng    │              │Detection │              │Y1+x2+x3  │     │
│  │• Invoices│              │          │              │Combined  │     │
│  │          │              │MobileNet │              │Store 50  │     │
│  │x1: Images│              │Custom    │              │Time-     │     │
│  │x2: Text  │─x2,x3:Text──▶│OpenCV    │──────────────│series    │     │
│  │x3: Text  │              │          │              └──────────┘     │
│  └──────────┘              │Y1: JSON  │                    │          │
│                            └──────────┘                    │          │
│                            Training:70%                    │          │
│                            Testing:10%                     │          │
│                            Validation:20%                  │          │
│                                                            │          │
│                                                  Y1+x2+x3  │          │
│                                                            ▼          │
│                            ┌──────────┐         ┌──────────────┐     │
│                            │MODEL 2:  │◀────────│Input:        │     │
│                            │LSTM      │         │Y1+x2+x3      │     │
│                            │          │         │Time Series   │     │
│                            │Stacked   │         └──────────────┘     │
│                            │LSTM      │                               │
│                            │128+64    │                               │
│                            │Attention │                               │
│                            │Trend     │                               │
│                            │          │                               │
│                            │Y2: TEXT  │                               │
│                            │Forecast  │                               │
│                            └──────────┘                               │
│                            Training:70%                               │
│                            Testing:10%                                │
│                            Validation:20%                             │
│                                  │                                    │
│                                  │Y2 Output                           │
│                                  ▼                                    │
│                            ┌──────────┐                               │
│                            │FINAL     │                               │
│                            │OUTPUT/UI │                               │
│                            │          │                               │
│                            │• Y1:     │                               │
│                            │  Products│                               │
│                            │• Y2:     │                               │
│                            │  Forecast│                               │
│                            │• Scores  │                               │
│                            │• Trends  │                               │
│                            └──────────┘                               │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 DATASET Component

**Input Sources:**
- **Danh sách sản phẩm quán Sơn** - Product catalog Sơn
- **Danh sách sản phẩm quán Tùng** - Product catalog Tùng
- **Hóa đơn** - Invoice images

**Input Types:**
- **x1: Hóa đơn giấy (Images)** - Paper invoices for CNN
- **x2: Hóa đơn hiện tại** - Current invoice text
- **x3: Hóa đơn lịch sử** - Historical invoice text

**File Location:**
- `data/product_catalogs.json` - Product catalogs
- `data/DATASET-tung1000.csv` - Training dataset
- User uploads - Invoice images

---

## 🖼️ MODEL 1: CNN - Invoice Detection

**Purpose:** Image Detection (Paper Invoice → Electric Invoice)

**Architecture:**
- **Base:** MobileNetV2 (Transfer Learning)
- **Custom Layer:** Detection Head
- **Text Extraction:** OpenCV
- **Input:** x1 (Invoice Images)
- **Output:** Y1 (Electronic Invoice JSON)

**Training Split:**
- Training: 70%
- Testing: 10%
- Validation: 20%

**Y1 Output Format (JSON):**
```json
{
  "invoice_id": "INV-20251103-001",
  "store_name": "Cửa Hàng Tùng",
  "store_key": "tung",
  "products": [
    {
      "product_name": "Coca Cola",
      "quantity": 50,
      "unit_price": 10000,
      "line_total": 500000
    }
  ],
  "total_amount": 500000,
  "detection_confidence": 0.863,
  "extracted_text": "...",
  "timestamp": "2025-11-03T14:30:00"
}
```

**Code Files:**
- `models/cnn_model.py` - CNN implementation
- `services/invoice_service.py` - Processing logic
- `api/model1_routes.py` - API endpoints

**API Endpoint:**
```
POST /api/model1/detect
Input: image file (x1)
Output: Y1 JSON
```

---

## 💾 INVOICE HISTORY DATABASE

**Purpose:** Store last 50 invoices + Create time-series sequences

**Data Stored:**
- **Y1:** Output from MODEL 1 (detected invoices)
- **x2:** Current manual invoice data
- **x3:** Historical invoice data

**Combined Format:** Y1 + x2 + x3 (Time Series)

**Database Schema:**
```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
    invoice_id TEXT UNIQUE,
    store_name TEXT,
    store_key TEXT,
    total_amount REAL,
    confidence REAL,
    products TEXT,  -- JSON array
    extracted_text TEXT,
    created_at TIMESTAMP
);
```

**Features:**
- Stores last 50 invoices
- Creates time-series sequences for LSTM
- Combines Y1 (detected) + x2,x3 (manual)
- Provides historical data for forecasting

**Code Files:**
- `utils/database.py` - Database operations
- `database/invoices.db` - SQLite database

**Access:**
```python
from utils.database import get_invoices_from_db, save_invoice_to_db

# Save Y1 output
save_invoice_to_db(invoice_data)

# Get time series for MODEL 2
invoices = get_invoices_from_db(limit=50)
```

---

## 📈 MODEL 2: LSTM - Quantity Forecasting

**Purpose:** Quantity Forecasting from time series

**Architecture:**
- **Type:** Stacked LSTM (128 + 64 units)
- **Features:** Attention Mechanism + Trend Analysis
- **Input:** Y1 + x2 + x3 (Time Series from DATABASE)
- **Output:** Y2 TEXT (Forecast predictions)

**Training Split:**
- Training: 70%
- Testing: 10%
- Validation: 20%

**Input Format:**
```python
# Time series from INVOICE HISTORY DATABASE
[
  {"products": [...], "total_amount": 500000, "timestamp": "..."},
  {"products": [...], "total_amount": 450000, "timestamp": "..."},
  # ... last 50 invoices
]
```

**Y2 Output Format (TEXT):**
```json
{
  "predicted_quantity": 338,
  "trend": "stable",
  "confidence": 0.85,
  "recommendation": "moderate_increase",
  "recommendation_text": "Tăng nhẹ số lượng nhập kho",
  "history_count": 10
}
```

**Trend Analysis:**
- `increasing` - Xu hướng tăng
- `stable` - Ổn định
- `decreasing` - Xu hướng giảm

**Recommendations:**
- `maintain` - Giữ nguyên
- `slight_increase` - Tăng nhẹ
- `moderate_increase` - Tăng vừa phải
- `significant_increase` - Tăng mạnh
- `decrease` - Giảm

**Code Files:**
- `models/lstm_model.py` - LSTM implementation
- `services/forecast_service.py` - Forecasting logic
- `api/model2_routes.py` - API endpoints

**API Endpoint:**
```
POST /api/model2/forecast
Input: manual invoice data (x2, x3) - optional
Output: Y2 TEXT (forecast)
```

---

## 🎯 FINAL OUTPUT / UI

**Displays:**
- **Y1: Extracted Products** - From MODEL 1
- **Y2: Predicted Quantities** - From MODEL 2
- **Confidence Scores** - Detection & Forecast confidence
- **Trends** - Trend analysis and recommendations

**Output Components:**

### 1. Y1 Display (Invoice Detection Results)
```
Invoice ID: INV-20251103-001
Store: Cửa Hàng Tùng
Products:
  - Coca Cola: 50 units
  - Pepsi: 30 units
Total: 500,000 VND
Confidence: 86.3%
```

### 2. Y2 Display (Forecast Results)
```
Predicted Quantity: 338 products
Trend: Stable
Confidence: 85%
Recommendation: Tăng nhẹ số lượng nhập kho
```

### 3. Combined Dashboard
- Historical trends chart
- Prediction visualization
- Confidence scores
- Recommendation actions

**UI Files:**
- `ui/templates/index.html` - Main interface
- `static/script.js` - Frontend logic
- `static/style.css` - Styling

**Access:**
```
http://localhost:5000/
```

---

## 🔄 Complete Workflow

### Step 1: Upload Invoice (x1)
```
User → Upload image → MODEL 1 (CNN) → Y1 Output → DATABASE
```

### Step 2: Store in Database
```
Y1 Output → INVOICE HISTORY DATABASE → Store as time series
```

### Step 3: Add Manual Data (Optional)
```
User → Input x2, x3 → DATABASE → Combine with Y1
```

### Step 4: Forecast
```
DATABASE (Y1+x2+x3) → MODEL 2 (LSTM) → Y2 Output
```

### Step 5: Display Results
```
Y1 + Y2 → FINAL OUTPUT/UI → User sees results
```

---

## 📊 Data Flow Example

### Example Scenario:

**Input:**
1. User uploads invoice image (x1)
2. Optionally adds manual data (x2, x3)

**Processing:**
```
Step 1: MODEL 1 processes image
  Input:  invoice.jpg (x1)
  Output: Y1 = {invoice_id: "INV-001", products: [...], amount: 500000}

Step 2: Save to DATABASE
  Y1 → INVOICE HISTORY DATABASE
  Combined with x2, x3 → Time series created

Step 3: MODEL 2 forecasts
  Input:  Y1 + x2 + x3 (50 invoices time series)
  Output: Y2 = {predicted_quantity: 338, trend: "stable", confidence: 0.85}

Step 4: Display
  UI shows:
    - Y1: Detected products (Coca: 50, Pepsi: 30)
    - Y2: Predicted 338 products, stable trend, 85% confidence
    - Recommendation: Tăng nhẹ số lượng nhập kho
```

---

## 🎨 Flow Chart Colors

According to the diagram:
- 🔵 **Blue** - DATASET (Input data)
- 🟢 **Green** - MODEL 1: CNN (Image detection)
- 🟡 **Yellow** - INVOICE HISTORY DATABASE (Storage)
- 🔴 **Red** - MODEL 2: LSTM (Forecasting)
- 🟣 **Purple** - FINAL OUTPUT/UI (Results)

---

## 🔧 Technical Implementation

### MODEL 1 Implementation
```python
# services/invoice_service.py
def process_invoice_image(cnn_model, image_path):
    """x1 Images → MODEL 1 → Y1 Output"""
    invoice_data = cnn_model.predict_invoice_data(image_path)
    save_invoice_to_db(invoice_data)  # Y1 → DATABASE
    return invoice_data  # Y1 Output
```

### DATABASE Implementation
```python
# utils/database.py
def save_invoice_to_db(invoice_data):
    """Store Y1 output in INVOICE HISTORY DATABASE"""
    # Saves to invoices table
    # Creates time-series sequences
    # Combines Y1 + x2 + x3
```

### MODEL 2 Implementation
```python
# services/forecast_service.py
def forecast_quantity(lstm_model, invoice_data_list):
    """Y1+x2+x3 Time Series → MODEL 2 → Y2 Output"""
    prediction = lstm_model.predict_quantity(invoice_data_list)
    return prediction  # Y2 TEXT (Forecast)
```

---

## 📈 Performance Metrics

### MODEL 1 (CNN)
- **Training:** 70% of dataset
- **Testing:** 10% of dataset
- **Validation:** 20% of dataset
- **Output:** Y1 (Electronic Invoice JSON)
- **Confidence:** Typically 80-90%

### MODEL 2 (LSTM)
- **Training:** 70% of time series
- **Testing:** 10% of time series
- **Validation:** 20% of time series
- **Output:** Y2 TEXT (Forecast)
- **Confidence:** Typically 75-95%

### INVOICE HISTORY DATABASE
- **Capacity:** Last 50 invoices
- **Purpose:** Time-series creation
- **Format:** Y1 + x2 + x3 combined

---

## 🚀 API Integration

### Complete API Flow

```bash
# 1. Detect Invoice (MODEL 1)
curl -X POST http://localhost:5000/api/model1/detect \
  -F "file=@invoice.jpg"
# Returns: Y1 Output (JSON)

# 2. Forecast Quantity (MODEL 2)
curl -X POST http://localhost:5000/api/model2/forecast \
  -H "Content-Type: application/json" \
  -d '{"invoice_data": "Coca Cola - 50\nPepsi - 30"}'
# Returns: Y2 Output (Forecast TEXT)

# 3. Get Database History
curl http://localhost:5000/api/history/database?limit=50
# Returns: Y1 + x2 + x3 time series

# 4. Get Statistics
curl http://localhost:5000/api/statistics
# Returns: Overall system statistics
```

---

## 📝 Summary

This system implements a **complete invoice forecasting pipeline** with:

1. **DATASET** → Multiple input sources (x1, x2, x3)
2. **MODEL 1 (CNN)** → Image detection → Y1 Output
3. **INVOICE HISTORY DATABASE** → Store Y1+x2+x3 → Time series
4. **MODEL 2 (LSTM)** → Quantity forecasting → Y2 Output
5. **FINAL OUTPUT/UI** → Display Y1+Y2 results

All components work together following the **INVOICE FORECAST SYSTEM FLOW CHART** specification.

---

**Last Updated:** 2025-11-03
**Version:** 2.0 (Flow Chart Aligned)
**Status:** ✅ Implemented and Running
