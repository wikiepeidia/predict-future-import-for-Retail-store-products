# Dataset Structure

## 📁 Folder Organization

### Raw Warehouse Data

```
data/
├── QUANSON.csv          (14,142 products - Wholesale warehouse)
├── QUANTUNG.csv         (959 products - Retail warehouse)
└── HOADON.csv           (Coming soon - Sales invoices)
```

### Generated Invoice Images

#### QUANSON Warehouse

```
data/generated_invoices_quanson/
├── train/                    (80 images)
│   ├── invoice_0000.png
│   ├── invoice_0001.png
│   └── ...
├── test/                     (20 images)
│   ├── invoice_0000.png
│   └── ...
├── train_metadata.json       (Training data metadata)
└── test_metadata.json        (Test data metadata)
```

Store Names:

- Kho Quân Sơn - Chi nhánh HN
- Kho Quân Sơn - Chi nhánh HCM
- Kho Quân Sơn - Trung tâm
- Kho Quân Sơn - Phân phối
- Kho Quân Sơn - Bán sỉ

#### QUANTUNG Warehouse

```
data/generated_invoices_quantung/
├── train/                    (80 images)
│   ├── invoice_0000.png
│   ├── invoice_0001.png
│   └── ...
├── test/                     (20 images)
│   ├── invoice_0000.png
│   └── ...
├── train_metadata.json       (Training data metadata)
└── test_metadata.json        (Test data metadata)
```

Store Names:

- Kho Quân Tùng - Chi nhánh 1
- Kho Quân Tùng - Chi nhánh 2
- Kho Quân Tùng - Bán lẻ
- Kho Quân Tùng - Showroom
- Kho Quân Tùng - Trung tâm

---

## 📊 Dataset Statistics

### QUANSON.csv

- **Products**: 14,142
- **Type**: Wholesale warehouse
- **Price Range**: 0 - 4,950,000 VND
- **Average Price**: 117,460 VND
- **Has Import Prices**: ✅ Yes

### QUANTUNG.csv

- **Products**: 959
- **Type**: Retail warehouse
- **Price Range**: 5,000 - 350,000,000 VND
- **Average Price**: 1,043,054 VND
- **Has Import Prices**: ✅ Yes (calculated with 35% margin)

### Generated Images

- **Total Training Images**: 160 (80 + 80)
- **Total Test Images**: 40 (20 + 20)
- **Image Format**: PNG (800x1000 pixels)
- **Metadata Format**: JSON with Vietnamese product names

---

## 🔄 Price Formula

**QUANTUNG** import prices calculated using:

```
Giá bán lẻ = Giá nhập + (Giá nhập × 35%)
Giá bán lẻ = Giá nhập × 1.35

Therefore:
Giá nhập = Giá bán lẻ / 1.35
```

Prices are rounded to nearest thousand:

- 12,283 → 12,000
- 13,845 → 14,000
- 282,948 → 283,000

---

## 🚀 Usage

### Generate New Images

```bash
python data/invoice_image_generator.py
```

This generates:

- 100 images from QUANSON (80 train + 20 test)
- 100 images from QUANTUNG (80 train + 20 test)

### Train Models

```bash
python train_models.py
```

This trains:

- **CNN Model**: On 160 combined images from both warehouses
- **LSTM Model**: On QUANSON + QUANTUNG raw CSV data

---

## 📝 Notes

1. **Product Overlap**: 0% (completely different products in each warehouse)
2. **Training Strategy**: Separate models for each warehouse, then ensemble
3. **Image Quality**: Synthetic with noise, rotation, and realistic formatting
4. **Language**: All product names in Vietnamese
5. **Price Format**: "12.000" (dot as thousand separator)

---

## ✅ Data Quality Checks

- [x] Import prices calculated correctly
- [x] Price formatting with dots (12.000)
- [x] Vietnamese product names preserved
- [x] Metadata JSON files valid
- [x] Images generated successfully
- [x] Both warehouses represented equally
