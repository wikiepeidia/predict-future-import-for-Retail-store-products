# -*- coding: utf-8 -*-
"""
Flask App - Invoice Forecast Deep Learning Demo
Integrated with CNN (Model 1) and LSTM (Model 2)

Architecture:
- Model 1 (CNN): Hoa don giay -> Hoa don dien tu  
- Model 2 (LSTM): Historical Data -> Quantity Forecast
"""

import os
import sys
import warnings
import logging

# Suppress TensorFlow warnings and logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Only show errors
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN optimizations warning
warnings.filterwarnings('ignore', category=UserWarning, module='tensorflow')
warnings.filterwarnings('ignore', category=UserWarning, module='keras')
warnings.filterwarnings('ignore', category=UserWarning, module='google.protobuf')
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('keras').setLevel(logging.ERROR)
logging.getLogger('absl').setLevel(logging.ERROR)

from datetime import datetime
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import json
import pandas as pd
import re
import unicodedata
from pathlib import Path

# Add models to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))

# Import Deep Learning Models
from models.cnn_model import CNNInvoiceDetector
from models.lstm_model import LSTMTextRecognizer

# Create Flask app with UTF-8
app = Flask(
    __name__,
    template_folder='ui/templates',
    static_folder='static'
)
app.config['JSON_AS_ASCII'] = False
app.config['ENCODING'] = 'utf-8'

# Config
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('saved_models', exist_ok=True)

BASE_DIR = Path(__file__).resolve().parent
MODEL_SAVE_DIR = BASE_DIR / 'models' / 'saved'
MODEL_SAVE_DIR.mkdir(parents=True, exist_ok=True)

CNN_MODEL_PATH = MODEL_SAVE_DIR / 'cnn_invoice_detector.h5'
LSTM_MODEL_PATH = MODEL_SAVE_DIR / 'lstm_text_recognizer.h5'
CATALOG_PATH = BASE_DIR / 'data' / 'product_catalogs.json'

STORE_NAME_LOOKUP = {
    'son': 'Quán Sơn',
    'tung': 'Quán Tùng'
}


def load_product_catalogs(catalog_file: Path):
    if catalog_file.exists():
        try:
            with catalog_file.open('r', encoding='utf-8') as handle:
                data = json.load(handle)
                if isinstance(data, dict):
                    return data
        except (OSError, ValueError) as exc:
            print(f"Warning: Unable to load product catalogs ({exc})")
    return {}


PRODUCT_CATALOGS = load_product_catalogs(CATALOG_PATH)


def normalize_text(text):
    if not isinstance(text, str):
        return ''
    normalized = unicodedata.normalize('NFD', text)
    return ''.join(ch for ch in normalized if not unicodedata.combining(ch)).lower()


CATALOG_INDEX = [
    {
        'store': store_key,
        'product': product,
        'name_normalized': normalize_text(product.get('name', ''))
    }
    for store_key, products in PRODUCT_CATALOGS.items()
    for product in products
]


def detect_store_from_text(text):
    normalized = normalize_text(text)
    if 'quan tung' in normalized or ('tung' in normalized and 'quan' in normalized):
        return 'tung'
    if 'quan son' in normalized or ('son' in normalized and 'quan' in normalized):
        return 'son'
    return None


def extract_numbers_from_line(line):
    matches = re.findall(r'\d{1,3}(?:[\.,]\d{3})+|\d+', line)
    values = []
    for match in matches:
        clean = re.sub(r'[^0-9]', '', match)
        if not clean:
            continue
        try:
            values.append(int(clean))
        except ValueError:
            continue
    return values


def extract_quantity_from_line(line):
    line_lower = line.lower()
    multiplier_match = re.search(r'(?:x|×|\*)\s*(\d{1,3})', line_lower)
    if multiplier_match:
        return int(multiplier_match.group(1))

    unit_match = re.search(r'(\d{1,3})\s*(?:pcs|chai|hop|kg|sp|unit|units|box|thung|ly|goi|bich|dong)', line_lower)
    if unit_match:
        return int(unit_match.group(1))

    numbers = extract_numbers_from_line(line)
    for value in numbers:
        if 0 < value <= 500:
            return value
    return None


def extract_price_candidates(line):
    numbers = extract_numbers_from_line(line)
    return [value for value in numbers if value >= 1000]


def lookup_catalog_price(product_id=None, product_name=None):
    if product_id:
        for entry in CATALOG_INDEX:
            if entry['product'].get('id') == product_id:
                return entry['product'].get('price', 0)
    if product_name:
        normalized_name = normalize_text(product_name)
        for entry in CATALOG_INDEX:
            if entry['name_normalized'] == normalized_name:
                return entry['product'].get('price', 0)
    return 0


def fallback_products(store_key='son', limit=3):
    catalog = PRODUCT_CATALOGS.get(store_key) or []
    fallback = []
    for product in catalog[:limit]:
        fallback.append({
            'product_id': product.get('id'),
            'product_name': product.get('name'),
            'quantity': 1,
            'unit_price': product.get('price', 0),
            'line_total': product.get('price', 0)
        })
    return fallback


def extract_products_from_text(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    normalized_lines = [normalize_text(line) for line in lines]

    aggregated = {}
    store_counts = {store: 0 for store in PRODUCT_CATALOGS.keys()}

    for original_line, normalized_line in zip(lines, normalized_lines):
        for entry in CATALOG_INDEX:
            name_normalized = entry['name_normalized']
            if not name_normalized:
                continue
            if name_normalized not in normalized_line:
                continue

            store_key = entry['store']
            store_counts[store_key] = store_counts.get(store_key, 0) + 1

            product = entry['product']
            product_id = product.get('id')
            aggregated.setdefault(product_id, {
                'product_id': product_id,
                'product_name': product.get('name', 'Unknown Product'),
                'quantity': 0,
                'unit_price': product.get('price', 0),
                'line_total': 0
            })

            record = aggregated[product_id]
            quantity = extract_quantity_from_line(original_line)
            if quantity:
                record['quantity'] += quantity

            prices = extract_price_candidates(original_line)
            if prices:
                candidate_unit = min(prices)
                if candidate_unit < record['unit_price'] * 5 and candidate_unit > 0:
                    record['unit_price'] = candidate_unit
                candidate_total = max(prices)
                if record['quantity']:
                    record['line_total'] = max(record['line_total'], candidate_total, record['unit_price'] * record['quantity'])
                else:
                    record['line_total'] = max(record['line_total'], candidate_total)

    products = []
    for record in aggregated.values():
        if record['quantity'] <= 0:
            record['quantity'] = 1
        if record['unit_price'] <= 0:
            record['unit_price'] = lookup_catalog_price(record.get('product_id'), record.get('product_name')) or 10000
        line_estimate = record['unit_price'] * record['quantity']
        record['line_total'] = max(record['line_total'], line_estimate)
        record['quantity'] = int(round(record['quantity']))
        record['unit_price'] = int(round(record['unit_price']))
        record['line_total'] = int(round(record['line_total']))
        products.append(record)

    products.sort(key=lambda item: item['line_total'], reverse=True)
    return products[:12], store_counts


def build_invoice_payload(_image_path, ocr_result):
    extracted_text = ocr_result.get('extracted_text', '') or ''
    parsed_data = ocr_result.get('parsed_data') or {}

    products, store_counts = extract_products_from_text(extracted_text)
    store_key = detect_store_from_text(extracted_text)

    if not store_key and store_counts:
        try:
            candidate_key, candidate_count = max(store_counts.items(), key=lambda item: item[1])
            if candidate_count > 0:
                store_key = candidate_key
        except ValueError:
            store_key = None

    if store_key not in STORE_NAME_LOOKUP:
        store_key = None

    if not products:
        fallback_key = store_key or 'son'
        products = fallback_products(fallback_key)

    store_name = STORE_NAME_LOOKUP[store_key] if store_key in STORE_NAME_LOOKUP else 'Unknown Store'

    try:
        parsed_total_amount = float(parsed_data.get('total_amount', 0) or 0)
    except (TypeError, ValueError):
        parsed_total_amount = 0.0

    total_amount = sum(product.get('line_total', 0) for product in products)
    if total_amount <= 0 and parsed_total_amount > 0:
        total_amount = parsed_total_amount

    invoice_identifier = parsed_data.get('invoice_number')
    if not invoice_identifier:
        invoice_identifier = f"INV_{int(datetime.now().timestamp())}"

    detection_confidence = float(ocr_result.get('confidence', 0.85))

    invoice_data = {
        'invoice_id': invoice_identifier,
        'store_name': store_name,
        'store_key': store_key,
        'products': products,
        'total_amount': int(round(total_amount)),
        'detection_confidence': detection_confidence,
        'text_regions_count': max(len(products), 1),
        'extracted_text': extracted_text,
        'date': datetime.now().isoformat()
    }

    return invoice_data


def build_forecast_dataframe(invoices):
    records = []
    for invoice in invoices:
        products = invoice.get('products', [])
        total_quantity = sum(max(product.get('quantity', 0), 0) for product in products)
        if total_quantity <= 0:
            total_quantity = max(invoice.get('total_quantity', 0), 0)

        total_amount = invoice.get('total_amount')
        if not total_amount or total_amount <= 0:
            total_amount = sum(
                (product.get('line_total') or product.get('quantity', 0) * product.get('unit_price', 0))
                for product in products
            )

        average_price = 0.0
        if total_quantity > 0:
            average_price = total_amount / total_quantity
        elif products:
            average_price = sum(product.get('unit_price', 0) for product in products) / max(len(products), 1)

        # Estimate auxiliary metrics for LSTM input
        estimated_sales = total_quantity * 0.9
        estimated_stock = max(total_quantity * 1.15, total_quantity + 10)
        demand_indicator = estimated_sales / (estimated_stock + 1)

        records.append({
            'quantity': float(total_quantity),
            'price': float(max(average_price, 0)),
            'sales': float(max(estimated_sales, 0)),
            'stock': float(max(estimated_stock, 0)),
            'demand': float(max(demand_indicator, 0))
        })

    if not records:
        return pd.DataFrame(columns=['quantity', 'price', 'sales', 'stock', 'demand'])

    return pd.DataFrame(records)

# Initialize Deep Learning Models
print("Initializing Deep Learning Models...")
print("\n" + "="*60)
print("INITIALIZING DEEP LEARNING MODELS")
print("="*60)

# Model 1: CNN for Invoice Detection
print("Loading Model 1: CNN Invoice Detector...")
cnn_model = None
try:
    cnn_model = CNNInvoiceDetector(img_height=224, img_width=224)
    if CNN_MODEL_PATH.exists():
        cnn_model.load_model(str(CNN_MODEL_PATH))
        print(f"   ✅ Loaded CNN weights from {CNN_MODEL_PATH.name}")
    else:
        cnn_model.build_model()
        cnn_model.compile_model()
        print("   ⚠️  Pre-trained CNN weights not found; using freshly initialized model")
except Exception as exc:
    print(f"   ⚠️  Unable to load CNNInvoiceDetector: {exc}")
    cnn_model = CNNInvoiceDetector(img_height=224, img_width=224)
    cnn_model.build_model()
    cnn_model.compile_model()

# Model 2: LSTM for Quantity Forecasting
print("Loading Model 2: LSTM Text Recognizer...")
lstm_model = None
try:
    lstm_model = LSTMTextRecognizer(sequence_length=10, num_features=5)
    if LSTM_MODEL_PATH.exists():
        lstm_model.load_model(str(LSTM_MODEL_PATH))
        print(f"   ✅ Loaded LSTM weights from {LSTM_MODEL_PATH.name}")
    else:
        lstm_model.build_model()
        lstm_model.compile_model()
        print("   ⚠️  Pre-trained LSTM weights not found; using freshly initialized model")
except Exception as exc:
    print(f"   ⚠️  Unable to load LSTMTextRecognizer: {exc}")
    lstm_model = LSTMTextRecognizer(sequence_length=10, num_features=5)
    lstm_model.build_model()
    lstm_model.compile_model()

print("="*60)
print("MODELS INITIALIZED - READY TO BUILD ON DEMAND")
print("="*60 + "\n")

# Storage for invoice history (simulating database)
invoice_history = []

def get_cnn_model():
    """Lazy load invoice OCR model"""
    global cnn_model
    if cnn_model is None:
        print("Loading CNNInvoiceDetector on demand...")
        try:
            cnn_model = CNNInvoiceDetector(img_height=224, img_width=224)
            if CNN_MODEL_PATH.exists():
                cnn_model.load_model(str(CNN_MODEL_PATH))
            else:
                cnn_model.build_model()
                cnn_model.compile_model()
        except Exception as exc:
            print(f"   ⚠️  Fallback to fresh CNNInvoiceDetector due to: {exc}")
            cnn_model = CNNInvoiceDetector(img_height=224, img_width=224)
            cnn_model.build_model()
            cnn_model.compile_model()
    return cnn_model


def get_lstm_model():
    """Lazy load LSTM forecast model"""
    global lstm_model
    if lstm_model is None:
        print("Loading LSTMTextRecognizer on demand...")
        try:
            lstm_model = LSTMTextRecognizer(sequence_length=10, num_features=5)
            if LSTM_MODEL_PATH.exists():
                lstm_model.load_model(str(LSTM_MODEL_PATH))
            else:
                lstm_model.build_model()
                lstm_model.compile_model()
        except Exception as exc:
            print(f"   ⚠️  Fallback to fresh LSTMTextRecognizer due to: {exc}")
            lstm_model = LSTMTextRecognizer(sequence_length=10, num_features=5)
            lstm_model.build_model()
            lstm_model.compile_model()
    return lstm_model

def allowed_file(filename):
    """Check if file is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ===== HOMEPAGE =====
@app.route('/')
def index():
    """Main page"""
    try:
        with open('ui/templates/index.html', 'r', encoding='utf-8', errors='replace') as f:
            html_content = f.read()
        return html_content
    except Exception as e:
        return f"<html><body><h1>Error loading page</h1><p>{str(e)}</p></body></html>"

# ===== API: Model 1 - CNN Invoice Detection =====
@app.route('/api/model1/detect', methods=['POST'])
def model1_detect():
    """
    Model 1: CNN - Image Detection
    Input: x1 Hoa don giay (Invoice Image)
    Output: Y1 Hoa don dien tu nhap hang
    """
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image provided'}), 400

        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file'}), 400

        # Save uploaded file
        filename = secure_filename(file.filename or 'invoice')
        filepath = os.path.join(UPLOAD_FOLDER, f"{datetime.now().timestamp()}_{filename}")
        file.save(filepath)

        print(f"\nProcessing invoice image: {filename}")
        model = get_cnn_model()

        # Use CNN to predict invoice data (real deep learning!)
        invoice_data = model.predict_invoice_data(filepath)
        invoice_data['date'] = datetime.now().isoformat()
        
        invoice_history.append(invoice_data)
        if len(invoice_history) > 300:
            invoice_history.pop(0)

        print("Invoice detection results:")
        print(f"  - Invoice ID: {invoice_data['invoice_id']}")
        print(f"  - Store: {invoice_data['store_name']}")
        print(f"  - Products detected: {len(invoice_data['products'])}")
        print(f"  - Total amount: {int(invoice_data['total_amount']):,} VND")
        print(f"  - Confidence: {invoice_data['detection_confidence']:.3f}")
        print(f"  - Total invoices in history: {len(invoice_history)}")

        product_lines = [
            f"{product.get('product_name', 'Unknown')} - {product.get('quantity', 0)}"
            for product in invoice_data.get('products', [])
        ]
        recognized_text = (
            f"Invoice ID: {invoice_data['invoice_id']}\n"
            f"Store: {invoice_data['store_name']}\n\n"
            f"Products:\n" + "\n".join(product_lines) +
            f"\n\nTotal: {int(invoice_data['total_amount']):,} VND"
        )

        return jsonify({
            'success': True,
            'recognized_text': recognized_text,
            'confidence': invoice_data['detection_confidence'],
            'data': invoice_data,
            'total_history_count': len(invoice_history)
        }), 200

    except Exception as e:
        print(f"Error in Model 1: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

# ===== API: Model 2 - LSTM Quantity Forecasting =====
@app.route('/api/model2/forecast', methods=['POST'])
def model2_forecast():
    """
    Model 2: LSTM - Text Recognition (Quantity Forecasting)
    Input: Y1 (tu Model 1) + x2 (Hoa don nhap hang) + x3 (Hoa don nhap hang)
    Output: Y2 TEXT - Du doan so luong de tiep
    """
    try:
        # Get data from request (either manual input or use history)
        data = request.get_json() or {}
        manual_invoice_data = data.get('invoice_data', '').strip()
        
        # Parse manual invoice data if provided
        if manual_invoice_data:
            # Parse the manual input into invoice history format
            lines = manual_invoice_data.split('\n')
            parsed_products = []
            for line in lines:
                line = line.strip()
                if line and ('-' in line or ':' in line):
                    # Split by - or : and try to extract product and quantity
                    parts = line.replace(':', '-').split('-', 1)
                    if len(parts) == 2:
                        product = parts[0].strip()
                        try:
                            quantity = int(parts[1].strip())
                            parsed_products.append({
                                'product_id': None,
                                'product_name': product,
                                'quantity': quantity,
                                'unit_price': 10000,
                                'line_total': quantity * 10000
                            })
                        except ValueError:
                            continue
            
            if parsed_products:
                # Create a mock invoice from manual input
                manual_invoice = {
                    'invoice_id': f'MANUAL_{datetime.now().timestamp()}',
                    'store_name': 'Manual Input',
                    'date': datetime.now().isoformat(),
                    'products': parsed_products,
                    'total_amount': sum(p.get('line_total', 0) for p in parsed_products)
                }
                # Use this manual invoice for forecasting
                forecast_data = [manual_invoice]
            else:
                return jsonify({
                    'success': False,
                    'message': 'Could not parse manual invoice data. Please use format: "Product Name - Quantity"'
                }), 400
        else:
            # Use accumulated invoice history
            if len(invoice_history) == 0:
                return jsonify({
                    'success': False,
                    'message': 'No invoice history. Please upload invoices first using Model 1 or provide manual invoice data.'
                }), 400
            forecast_data = invoice_history

        print(f"\nForecasting with LSTM using {len(forecast_data)} invoice records...")
        model = get_lstm_model()
        
        # Call the correct method from lstm_model.py
        prediction = model.predict_quantity(forecast_data)
        
        if not prediction.get('success', True):
            return jsonify({
                'success': False,
                'message': prediction.get('message', 'Forecasting failed')
            }), 500

        print("Forecast complete:")
        print(f"   Predicted quantity: {prediction.get('predicted_quantity', 0):.0f} products")
        print(f"   Trend: {prediction.get('trend', 'unknown')}")
        print(f"   Confidence: {prediction.get('confidence', 0.0):.2%}")

        # Format outputs for frontend
        predicted_qty = int(prediction.get('predicted_quantity', 0))
        trend_text = prediction.get('trend', 'stable')
        recommendation = prediction.get('recommendation_text', '')
        
        return jsonify({
            'success': True,
            'output1': f"Predicted total quantity: {predicted_qty} products",
            'output2': recommendation or f"Trend analysis: {trend_text}",
            'confidence': float(prediction.get('confidence', 0.0)),
            'data': prediction,
            'history_count': len(forecast_data)
        }), 200

    except Exception as e:
        print(f"Error in Model 2: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500
@app.route('/api/history', methods=['GET'])
def get_history():
    """Get current invoice history"""
    return jsonify({
        'success': True,
        'count': len(invoice_history),
        'invoices': invoice_history[-10:]  # Last 10 invoices
    }), 200

# ===== API: Clear History =====
@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """Clear invoice history"""
    global invoice_history
    invoice_history = []
    return jsonify({
        'success': True,
        'message': 'Invoice history cleared'
    }), 200

# ===== API: Model Info =====
@app.route('/api/models/info', methods=['GET'])
def models_info():
    """Get information about loaded models"""
    return jsonify({
        'success': True,
        'models': {
            'model1_cnn': {
                'name': 'Invoice OCR Model (CNN + OCR)',
                'input': 'x1 - Hóa đơn giấy (invoice image)',
                'output': 'Y1 - Hóa đơn điện tử nhập hàng',
                'architecture': 'Custom CNN feature extractor + Tesseract OCR',
                'status': 'Ready' if cnn_model and getattr(cnn_model, 'model', None) else 'Not loaded',
                'image_size': f"{cnn_model.img_height}x{cnn_model.img_width}" if cnn_model else 'Not loaded',
                'weights': str(CNN_MODEL_PATH) if CNN_MODEL_PATH.exists() else 'In-memory'
            },
            'model2_lstm': {
                'name': 'Import Forecast LSTM',
                'input': 'Structured invoice history (quantity, price, sales, stock, demand)',
                'output': 'Predicted import quantity & confidence',
                'architecture': 'Stacked LSTM for time-series forecasting',
                'status': 'Ready' if lstm_model and getattr(lstm_model, 'model', None) else 'Not loaded',
                'lookback': lstm_model.lookback if lstm_model else 'Not loaded',
                'features': lstm_model.features if lstm_model else 'Not loaded',
                'weights': str(LSTM_MODEL_PATH) if LSTM_MODEL_PATH.exists() else 'In-memory'
            }
        },
        'invoice_history_count': len(invoice_history)
    }), 200

# ===== API: Train Models (Debug endpoint) =====
@app.route('/api/models/train', methods=['POST'])
def train_models():
    """
    Endpoint to trigger model training
    (For development/testing only)
    """
    return jsonify({
        'success': False,
        'message': 'Training endpoint not implemented. Use train_models.py script instead.'
    }), 501

if __name__ == '__main__':
    print("\n" + "="*70)
    print("INVOICE FORECAST SYSTEM - DEEP LEARNING DEMO")
    print("="*70)
    print("Model 1: CNN - Image Detection (Hoa don giay -> Hoa don dien tu)")
    print("Model 2: LSTM - Quantity Forecasting (Y1 + x2 + x3 -> Y2 TEXT)")
    print("="*70)
    print("Server: http://localhost:5000")
    print("API Docs:")
    print("   POST /api/model1/detect     - Upload invoice image (CNN)")
    print("   POST /api/model2/forecast   - Get quantity forecast (LSTM)")
    print("   GET  /api/history           - View invoice history")
    print("   GET  /api/models/info       - Model information")
    print("="*70)
    
    app.run(debug=False, port=5000, host='127.0.0.1', use_reloader=False)
