# Quick Reference Guide

## 🚀 Quick Start

### Generate Dataset & Train Models (One Command)

**Windows:**

```batch
run_complete_pipeline.bat
```

**Linux/Mac:**

```bash
bash run_complete_pipeline.sh
```

---

## 📋 Manual Workflow

### Step 1: Generate Dataset (1000 images)

```bash
python data/generate_balanced_dataset.py
```

**Output:**

- `data/generated_invoices/train/` - 700 images (350 QUANSON + 350 QUANTUNG)
- `data/generated_invoices/valid/` - 200 images (100 QUANSON + 100 QUANTUNG)
- `data/generated_invoices/test/` - 100 images (50 QUANSON + 50 QUANTUNG)

### Step 2: Train Models

```bash
python train_models.py
```

**Configuration:**

- Epochs: 48
- Batch Size: 12
- Learning Rate: 0.01 (adaptive)

**Output:**

- `saved_models/lstm_text_recognizer.weights.h5`
- `saved_models/cnn_invoice_detector.weights.h5`
- `saved_models/lstm_training_history.json`
- `saved_models/cnn_training_history.json`

### Step 3: Generate Evaluation Charts

```bash
python evaluate_models.py
```

**Output:**

- `evaluation/dataset_distribution.png`
- `evaluation/scenario_comparison.png`
- `evaluation/lstm_training_history.png`
- `evaluation/cnn_training_history.png`

### Step 4: Run Flask App

```bash
python app.py
```

Open browser: <http://localhost:5000>

---

## 📊 Dataset Details

### Business Scenarios

| Warehouse | Type | Demand | Products/Invoice | Images |
|-----------|------|--------|-----------------|--------|
| QUANSON | Minimart | High | 5-15 items | 500 |
| QUANTUNG | Souvenir | Low | 2-6 items | 500 |

### Split Distribution

| Split | QUANSON | QUANTUNG | Total | Percentage |
|-------|---------|----------|-------|------------|
| Train | 350 | 350 | 700 | 70% |
| Valid | 100 | 100 | 200 | 20% |
| Test | 50 | 50 | 100 | 10% |
| **Total** | **500** | **500** | **1000** | **100%** |

---

## 🔧 Troubleshooting

### Issue: FileNotFoundError - No such file or directory

**Problem:** Old folder structure referenced

```
FileNotFoundError: data\generated_invoices\train\invoice_0000.png
```

**Solution:** Run new dataset generator

```bash
python data/generate_balanced_dataset.py
```

New structure uses:

- `data/generated_invoices/train/quanson_train_0000.png`
- `data/generated_invoices/train/quantung_train_0000.png`

### Issue: Model not training

**Check:**

1. Dataset generated? `ls data/generated_invoices/`
2. Metadata files exist?
   - `data/generated_invoices/train_metadata.json`
   - `data/generated_invoices/valid_metadata.json`

### Issue: Evaluation charts not generating

**Requirements:**

```bash
pip install matplotlib numpy pandas
```

**Check training history exists:**

- `saved_models/lstm_training_history.json`
- `saved_models/cnn_training_history.json`

---

## 📝 Configuration Files

### Training Parameters (train_models.py)

```python
# LSTM Training
epochs=48
batch_size=12

# CNN Training
epochs=48
batch_size=12
```

### Dataset Generator (data/generate_balanced_dataset.py)

```python
# Total images per warehouse
half_images = 500

# Splits
train: 350 (70%)
valid: 100 (20%)
test: 50 (10%)

# QUANSON scenario
num_products = random.randint(5, 15)  # High demand

# QUANTUNG scenario
num_products = random.randint(2, 6)   # Low demand
```

---

## 📦 Project Structure

```
project/
├── data/
│   ├── QUANSON.csv                      # 14,142 products
│   ├── QUANTUNG.csv                     # 959 products
│   ├── invoice_image_generator.py       # Image generator class
│   ├── generate_balanced_dataset.py     # NEW: Balanced generator
│   └── generated_invoices/              # Generated dataset
│       ├── train/                       # 700 images
│       ├── valid/                       # 200 images
│       ├── test/                        # 100 images
│       └── *_metadata.json
├── models/
│   ├── lstm_model.py                    # LSTM forecaster
│   └── cnn_model.py                     # CNN detector
├── saved_models/                        # Trained weights
├── evaluation/                          # Performance charts
├── train_models.py                      # Training script
├── evaluate_models.py                   # NEW: Evaluation script
├── run_complete_pipeline.bat            # NEW: Windows automation
├── run_complete_pipeline.sh             # NEW: Linux automation
└── app.py                               # Flask web app
```

---

## 🎯 Training Metrics

### LSTM Model

- **Loss**: Huber (robust to outliers)
- **Metrics**: MAE (Mean Absolute Error)
- **Target**: MAE < 0.1 (on normalized data)

### CNN Model

- **Loss**: Huber + CrossEntropy
- **Architecture**: MobileNetV2 transfer learning
- **Target**: High invoice detection accuracy

---

## 💡 Tips

1. **GPU Training**: Models will automatically use GPU if available
2. **Memory**: 1000 images require ~2GB RAM during training
3. **Time**: Complete pipeline takes ~30-60 minutes
4. **Charts**: Check `evaluation/` folder after training
5. **History**: JSON files in `saved_models/` for custom analysis

---

## 📚 Documentation

- `README.md` - Main documentation
- `CHANGES_SUMMARY.md` - Recent updates
- `QUICKSTART.md` - This file
- API docs in `docs/` folder

---

## ✅ Checklist

Before training:

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] CSV files exist: `data/QUANSON.csv`, `data/QUANTUNG.csv`
- [ ] Run dataset generator

After training:

- [ ] Check saved models in `saved_models/`
- [ ] Review evaluation charts in `evaluation/`
- [ ] Test Flask app: `python app.py`
- [ ] Verify predictions work

---

**Last Updated:** November 4, 2025
**Version:** 2.0 (Balanced Dataset Update)
