# 🧹 Hướng Dẫn Dọn Dẹp Project

## ✅ Files Cần GIỮ (Keep These)

### Core Files
```
app.py                          # Main Flask application
config.py                       # ✨ NEW - Centralized configuration
train_models.py                 # Model training script
test.py                         # ✨ NEW - Simplified test script
requirements.txt                # Python dependencies
LICENSE                         # License file
```

### Models (models/)
```
models/
  ├── __init__.py
  ├── cnn_model.py              # CNN Invoice Detector
  ├── lstm_model.py             # LSTM Forecaster
  └── saved/                    # Trained model weights
      ├── cnn_invoice_detector.h5
      └── lstm_text_recognizer.h5
```

### Utils (utils/) - ✨ NEW
```
utils/
  ├── __init__.py               # ✨ NEW - Package init
  ├── data_processor.py         # ✨ NEW - Data utilities
  └── invoice_processor.py      # ✨ NEW - Invoice utilities
```

### Data (data/)
```
data/
  ├── product_catalogs.json     # Product database
  ├── DATASET-tung1000.csv      # Sample dataset
  └── generate_dataset.py       # Dataset generator
```

### UI (ui/)
```
ui/
  └── templates/
      ├── index.html
      └── dashboard.html
```

### Static (static/)
```
static/
  ├── script.js
  ├── style.css
  └── images/
```

### Documentation (docs/) - ✨ NEW
```
docs/
  ├── SETUP.md                  # ✨ NEW - Setup guide
  ├── API_GUIDE.md              # ✨ NEW - API documentation
  └── MODEL_DOCS.md             # To be created
```

---

## ❌ Files CẦN XÓA (Delete These)

### Redundant Old Files
```
collab.py                       # ❌ Duplicate of app.py for Colab
test_improvements.py            # ❌ Merged into test.py
test_models.py                  # ❌ Merged into test.py
```

### Old Core Files (replaced by utils/)
```
core/
  ├── config.py                 # ❌ Moved to root config.py
  └── utils.py                  # ❌ Split into utils/ package
```

### Backup Files
```
static/
  └── style.css.backup          # ❌ Backup file
```

### Old Dependencies
```
dependencies/
  ├── requirements.txt          # ❌ Use root requirements.txt
  ├── setup.bat                 # ❌ Outdated
  ├── setup.ps1                 # ❌ Outdated
  └── test_api.py               # ❌ Use docs/API_GUIDE.md examples
```

### Test Folder
```
test/
  └── verify_installation.py    # ❌ Use root test.py
```

### Old Model Files (duplicates)
```
models/
  ├── cnn_invoice_ocr.py        # ❌ Older version of cnn_model.py
  ├── lstm_forecast.py          # ❌ Older version of lstm_model.py
```

### Markdown Files (MARKDOWN/) - ❌ ALL 20+ files
```
MARKDOWN/
  ├── 00_START_HERE.md          # ❌ Merged into README.md
  ├── ACTIVITY_TRACKING.md      # ❌ Unnecessary
  ├── ADMIN_GUIDE.md            # ❌ Merged into SETUP.md
  ├── BACKEND_TODO.md           # ❌ Development notes
  ├── CHANGES.txt               # ❌ Use git history
  ├── EXAM_GUIDE.md             # ❌ Merged into docs/
  ├── EXAM_PRESENTATION_GUIDE.md # ❌ Merged into docs/
  ├── FIXES_COMPLETED.md        # ❌ Use git history
  ├── IMPROVEMENT_PROPOSAL.md   # ❌ Development notes
  ├── INSTALL.md                # ❌ Merged into SETUP.md
  ├── MODEL_DOCUMENTATION.md    # ❌ Merge into MODEL_DOCS.md
  ├── MODELS_READY.md           # ❌ Unnecessary
  ├── PROJECT_OUTLINE.md        # ❌ Merged into README.md
  ├── QUICK_REFERENCE.md        # ❌ Merged into API_GUIDE.md
  ├── QUICKSTART.md             # ❌ Merged into README.md
  ├── README_MODELS.md          # ❌ Merge into MODEL_DOCS.md
  ├── SIMPLE_START.txt          # ❌ Merged into SETUP.md
  ├── SIMPLIFICATION_SUMMARY.md # ❌ Development notes
  ├── SUMMARY.md                # ❌ Merged into README.md
  ├── TRAINING_SUCCESS.md       # ❌ Development notes
  └── UI_UPDATES.md             # ❌ Development notes
```

---

## 🔄 Commands để Dọn Dẹp

### Windows (PowerShell)
```powershell
# 1. Xóa old files
Remove-Item collab.py, test_improvements.py, test_models.py

# 2. Xóa core/ folder (đã move to config.py & utils/)
Remove-Item -Recurse core/

# 3. Xóa backup files
Remove-Item static/style.css.backup

# 4. Xóa dependencies/ folder
Remove-Item -Recurse dependencies/

# 5. Xóa test/ folder
Remove-Item -Recurse test/

# 6. Xóa old model files
Remove-Item models/cnn_invoice_ocr.py, models/lstm_forecast.py

# 7. Xóa TOÀN BỘ folder MARKDOWN/
Remove-Item -Recurse MARKDOWN/

# 8. Xóa images/ nếu rỗng
# Remove-Item -Recurse images/
```

### Linux/Mac (Bash)
```bash
# 1. Xóa old files
rm collab.py test_improvements.py test_models.py

# 2. Xóa core/ folder
rm -rf core/

# 3. Xóa backup files
rm static/style.css.backup

# 4. Xóa dependencies/ folder
rm -rf dependencies/

# 5. Xóa test/ folder
rm -rf test/

# 6. Xóa old model files
rm models/cnn_invoice_ocr.py models/lstm_forecast.py

# 7. Xóa TOÀN BỘ folder MARKDOWN/
rm -rf MARKDOWN/

# 8. Xóa images/ nếu rỗng
# rm -rf images/
```

---

## 📂 Cấu Trúc SAU KHI Dọn Dẹp

```
predict-future-import-for-Retail-store-products/
├── app.py
├── config.py                   ✨ NEW
├── train_models.py
├── test.py                     ✨ UPDATED
├── README.md                   ✨ UPDATED
├── LICENSE
├── requirements.txt
│
├── models/
│   ├── __init__.py
│   ├── cnn_model.py
│   ├── lstm_model.py
│   └── saved/
│
├── utils/                      ✨ NEW
│   ├── __init__.py
│   ├── data_processor.py
│   └── invoice_processor.py
│
├── data/
│   ├── product_catalogs.json
│   ├── DATASET-tung1000.csv
│   └── generate_dataset.py
│
├── ui/
│   └── templates/
│       ├── index.html
│       └── dashboard.html
│
├── static/
│   ├── style.css
│   ├── script.js
│   └── images/
│
├── docs/                       ✨ NEW
│   ├── SETUP.md
│   ├── API_GUIDE.md
│   └── MODEL_DOCS.md
│
├── saved_models/               # Auto-created
└── uploads/                    # Auto-created
```

---

## ⚠️ Chú Ý Trước Khi Xóa

1. **Backup quan trọng**: Nếu folder `images/` chứa ảnh demo, GIỮ LẠI
2. **Git history**: Nếu dùng Git, commit trước khi xóa
3. **Dependencies**: Kiểm tra `requirements.txt` root có đầy đủ
4. **Model weights**: KHÔNG xóa `models/saved/` và `saved_models/`

---

## ✅ Kiểm Tra Sau Khi Dọn Dẹp

```bash
# 1. Test models
python test.py

# 2. Check imports
python -c "from utils import normalize_text; print('Utils OK')"
python -c "from config import CNN_MODEL_PATH; print('Config OK')"

# 3. Run app
python app.py
```

---

## 📊 Thống Kê

**Trước khi dọn:**
- Files: ~50+
- Folders: ~10
- Markdown docs: 20+

**Sau khi dọn:**
- Files: ~20
- Folders: ~7
- Docs: 3 (consolidated)

**Giảm**: ~60% files, 100% rõ ràng hơn! 🎉
