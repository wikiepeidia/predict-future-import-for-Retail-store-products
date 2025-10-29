# Inventory Import Forecast - Deep Learning Project

## Project Objective

Build a deep learning system to predict future import quantities for retail store products based on:

1. Invoice image analysis (historical and new invoices)
2. Sales and inventory tracking data

---

## Business Problem

### Retail Store Challenge

Every retail store product (grocery, cafe, food establishments, etc.) has common characteristics:

- **Barcode identification**
- **Product image and description**

### Key Question

Does image recognition really matter for inventory management?

### Real Example

- Store "Tùng" has 2,000 products
- Last import included: 10 boxes of Brand A milk, 5 prenatal products from Brand B, etc.
- Both imports and sales generate invoices

---

## System Requirements

### Assumption 1: Automated Invoice Processing

When store staff inputs a purchase invoice (e.g., import receipt), the system should:

- Automatically extract product information
- Update inventory records based on invoice data

### Assumption 2: Intelligent Stock Verification

Build a system that:

- Monitors current inventory levels
- Recommends import quantities based on store's demand patterns

---

## Model Pipeline

### INPUT 1: Purchase Invoice Image

- **Source**: Scanned paper receipts OR digital invoice images
- **Format**: JPG, PNG, or PDF

### INPUT 2: Inventory Snapshot

- Current stock levels per SKU
- Historical sales data for the store
- Previous import patterns

---

## Model Architecture

### **Model 1: Invoice Detection (CNN)**

**Purpose**: Extract product line items from invoice images

- **Input**: Invoice image (JPG/PNG/PDF)
- **Output Y1**: Normalized digital invoice (structured data)
  - Product SKU
  - Product name
  - Quantity ordered
  - Unit price
  - Total line amount

**Architecture**: Convolutional Neural Network (CNN)

- Image preprocessing and feature extraction
- Object detection for invoice elements
- OCR/Text recognition for item details

---

### **Model 2: Quantity Forecasting (LSTM)**

**Purpose**: Predict next-period import quantities

- **Input X1**: Normalized invoice (from Model 1 output)
- **Input X2**: Inventory snapshot (current stock, sales history)
- **Output Y2**: Predicted import quantities per SKU

**Architecture**: Long Short-Term Memory (LSTM) Network

- Time-series analysis of historical imports and sales
- Pattern recognition for seasonal demand
- Quantity recommendations per product

---

## Data Pipeline Flow

```
Purchase Invoice Image (INPUT 1)
        ↓
    [Model 1 - CNN]
    Invoice Detection
        ↓
Normalized Invoice Data (Y1)
        ↓
    Merge with Inventory Data (INPUT 2)
        ↓
    [Model 2 - LSTM]
    Quantity Forecasting
        ↓
Predicted Import Quantities (Y2)
```

---

## Dataset Strategy

### Data Sources

1. **Historical invoices from Store Son**
2. **Historical invoices from Store Tùng**
3. **Structured import/sales records**

### Split Strategy

- **Training**: 70%
- **Validation**: 10%
- **Testing**: 20%

---

## Deliverables

### 1. Deep Learning Models

- Trained CNN model for invoice item extraction
- Trained LSTM model for quantity forecasting

### 2. Web Interface

- Simple upload page for invoice images
- API endpoints for model inference
- Results display showing predicted quantities

### 3. Documentation

- Model architecture and training details
- API documentation
- Usage examples

---

## Out of Scope (NOT INCLUDED)

- ❌ User authentication/login system
- ❌ Complex dashboards with heavy UI
- ❌ Multi-user admin panels
- ❌ Database persistence (simplified demo)
- ❌ Production deployment configurations

---

## Project Status: Deep Learning Exam Demo

This is a **simplified, focused project** for demonstration purposes in a deep learning exam context. The emphasis is on:

- **Model architecture and training**
- **Data pipeline understanding**
- **Practical application of CNN and LSTM**

NOT on frontend or backend infrastructure.
