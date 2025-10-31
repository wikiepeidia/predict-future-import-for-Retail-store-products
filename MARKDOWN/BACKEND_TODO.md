# 🔧 Backend Implementation TODO

## UI Features Already Implemented ✅

### Model 1 - Multiple Image Upload

- ✅ **Multiple file selection** (2-3 invoices)
- ✅ **Image preview** with thumbnails
- ✅ **Remove individual images** (× button)
- ✅ **Drag & drop** support for multiple files
- ✅ **Product table display** (Invoice | Product Name | Quantity)
- ✅ **Auto-populate Model 2** with extracted products
- ✅ **Batch processing UI** (processes all images sequentially)

### Model 2 - Text Input

- ✅ **Textarea** for structured product data
- ✅ **Auto-fill** from Model 1 results
- ✅ **Ctrl+Enter** shortcut to predict

---

## Backend Requirements (For Backend Team)

### 1. **Fix API Endpoints** 🚨 CRITICAL

#### Current Problem

```python
# WRONG - endpoints are reversed!
@app.route('/api/model1/predict', methods=['POST'])
def model1_predict():
    data = request.get_json()  # ❌ Expects JSON text
    
@app.route('/api/model2/recognize', methods=['POST'])
def model2_recognize():
    file = request.files['image']  # ❌ Expects image
```

#### Required Fix

```python
# ✅ CORRECT
@app.route('/api/model1/predict', methods=['POST'])
def model1_predict():
    """Model 1: OCR - Paper Invoice Image → Product Lines"""
    files = request.files.getlist('image')  # Accept multiple images
    # Process each image with CNN/OCR
    # Parse products from OCR text
    # Return: list of products with {invoice, product_name, quantity}

@app.route('/api/model2/recognize', methods=['POST'])
def model2_recognize():
    """Model 2: LSTM - Predict Quantities from Product Data"""
    data = request.get_json()  # Accept text/JSON
    text_input = data.get('text')
    # Parse product list
    # Use LSTM to predict future quantities
    # Return: predicted quantities per product
```

---

### 2. **Database Schema** 📊

Create SQLite database: `invoices.db`

#### Table 1: `invoices`

```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    image_path TEXT NOT NULL,          -- Path to saved image
    image_data BLOB,                   -- Optional: store image binary
    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    ocr_confidence REAL,
    processed BOOLEAN DEFAULT FALSE
);
```

#### Table 2: `products`

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,       -- Foreign key to invoices table
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL,                   -- Optional
    total_price REAL,                  -- Optional
    line_number INTEGER,               -- Position in invoice
    FOREIGN KEY (invoice_id) REFERENCES invoices(id)
);
```

#### Table 3: `predictions` (Optional)

```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    current_quantity INTEGER,
    predicted_quantity INTEGER,
    prediction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    confidence REAL
);
```

---

### 3. **Product Line Parsing** 🔍

Extract individual products from OCR text:

```python
def parse_invoice_products(ocr_text):
    """
    Parse OCR text into individual product entries
    
    Expected format:
    - "Coca Cola - 50"
    - "Product: Pepsi, Qty: 30"
    - "Water     100 units"
    
    Returns: list of {product_name, quantity}
    """
    products = []
    lines = ocr_text.split('\n')
    
    for line in lines:
        # Pattern 1: "Product - Quantity"
        match = re.match(r'(.+?)\s*[-:]\s*(\d+)', line)
        if match:
            products.append({
                'product_name': match.group(1).strip(),
                'quantity': int(match.group(2))
            })
    
    return products
```

---

### 4. **Updated API Response Format**

#### Model 1 Response (OCR)

```json
{
    "success": true,
    "invoices_processed": 3,
    "products": [
        {
            "invoice": "invoice1.jpg",
            "product": "Coca Cola",
            "quantity": 50
        },
        {
            "invoice": "invoice1.jpg",
            "product": "Pepsi",
            "quantity": 30
        },
        {
            "invoice": "invoice2.jpg",
            "product": "Water",
            "quantity": 100
        }
    ],
    "confidence": 0.92,
    "recognized_text": "Full OCR text here..."  // For debugging
}
```

#### Model 2 Response (Prediction)

```json
{
    "success": true,
    "output1": "Predicted import quantities:",
    "output2": "Coca Cola: 60 units\nPepsi: 35 units\nWater: 120 units",
    "confidence": 0.89,
    "predictions": [
        {"product": "Coca Cola", "current": 50, "predicted": 60},
        {"product": "Pepsi", "current": 30, "predicted": 35},
        {"product": "Water", "current": 100, "predicted": 120}
    ]
}
```

---

### 5. **File Storage**

```python
import os
from datetime import datetime

UPLOAD_FOLDER = 'uploads/invoices'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_invoice_image(file):
    """Save uploaded invoice image"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, f"{timestamp}_{filename}")
    file.save(filepath)
    return filepath
```

---

## Frontend Expectations

### What UI Sends to Backend

**Model 1:**

```javascript
// Multiple images in FormData
const formData = new FormData();
formData.append('image', file1);  // Will send as 'image' array
formData.append('image', file2);
formData.append('image', file3);

// Use: request.files.getlist('image') to get all files
```

**Model 2:**

```javascript
// Text/JSON
{
    "text": "Coca Cola - 50\nPepsi - 30\nWater - 100"
}
```

### What UI Expects from Backend

1. **Model 1:** Return products as array with invoice source
2. **Model 2:** Return predictions with confidence scores
3. **Error handling:** Return `{success: false, message: "error"}` on failure

---

## Testing Checklist

- [ ] Upload single invoice → Extract products
- [ ] Upload 2-3 invoices → Extract all products separately
- [ ] Products stored in database with correct invoice_id
- [ ] Each product on separate row in database
- [ ] Model 2 receives parsed product list
- [ ] Predictions generated per product
- [ ] Image files saved to disk
- [ ] Database contains image paths + OCR text

---

## Priority Order

1. **P0 (Critical):** Fix API endpoints (swap image/text handling)
2. **P1 (High):** Implement product parsing from OCR text
3. **P2 (High):** Database schema + save operations
4. **P3 (Medium):** Multiple image handling
5. **P4 (Low):** Optimize OCR accuracy

---

## Notes for Backend Team

- UI already handles multiple files correctly
- UI parses products client-side as demo (backend should do real parsing)
- UI auto-populates Model 2 with extracted products
- Database structure supports separate product entries (required for Model 2)
- Image preview shows which files are uploaded
- Remove button allows users to deselect specific images

**Contact frontend if you need any UI changes!** 🚀
