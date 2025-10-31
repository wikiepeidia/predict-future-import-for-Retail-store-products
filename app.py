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
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import json

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
    cnn_model.load_model('saved_models/cnn_invoice_detector.h5')
    print("   ✅ CNN Model loaded from saved file")
except:
    print("   ⚠️  Saved model not found - will build on first use")
    cnn_model = None

# Model 2: LSTM for Quantity Forecasting
print("Loading Model 2: LSTM Text Recognizer...")
lstm_model = None
try:
    lstm_model = LSTMTextRecognizer(sequence_length=10, num_features=5)
    lstm_model.load_model('saved_models/lstm_text_recognizer.h5')
    print("   ✅ LSTM Model loaded from saved file")
except:
    print("   ⚠️  Saved model not found - will build on first use")
    lstm_model = None

print("="*60)
print("MODELS INITIALIZED - READY TO BUILD ON DEMAND")
print("="*60 + "\n")

# Storage for invoice history (simulating database)
invoice_history = []

def get_cnn_model():
    """Lazy load CNN model"""
    global cnn_model
    if cnn_model is None:
        print("Building CNN model on demand...")
        cnn_model = CNNInvoiceDetector(img_height=224, img_width=224)
        cnn_model.build_model()
        cnn_model.compile_model()
        print("CNN model ready!")
    return cnn_model

def get_lstm_model():
    """Lazy load LSTM model"""
    global lstm_model
    if lstm_model is None:
        print("Building LSTM model on demand...")
        lstm_model = LSTMTextRecognizer(sequence_length=10, num_features=5)
        lstm_model.build_model()
        lstm_model.compile_model()
        print("LSTM model ready!")
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

        # REAL CNN MODEL PREDICTION
        print(f"\nProcessing invoice image with CNN: {filename}")
        model = get_cnn_model()
        
        # Debug: Check if file exists and get its size
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"File size: {file_size} bytes")
        else:
            print(f"ERROR: File does not exist: {filepath}")
        
        invoice_data = model.predict_invoice_data(filepath)
        
        print(f"Invoice detection results:")
        print(f"  - Invoice ID: {invoice_data['invoice_id']}")
        print(f"  - Store: {invoice_data['store_name']}")
        print(f"  - Products found: {len(invoice_data['products'])}")
        print(f"  - Total amount: {invoice_data['total_amount']:,} VND")
        print(f"  - Text regions: {invoice_data['text_regions_count']}")
        print(f"  - Confidence: {invoice_data['detection_confidence']:.3f}")

        return jsonify({
            'success': True,
            'recognized_text': f"Invoice ID: {invoice_data['invoice_id']}\nStore: {invoice_data['store_name']}\n\nProducts:\n" + "\n".join([f"{p['product_name']} - {p['quantity']}" for p in invoice_data['products']]) + f"\n\nTotal: {invoice_data['total_amount']:,} VND",
            'confidence': 0.92,  # Mock confidence for now
            'data': invoice_data
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
                                'product': product,
                                'quantity': quantity
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
                    'total_amount': sum(p['quantity'] for p in parsed_products) * 10000  # Mock total
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

        # REAL LSTM MODEL PREDICTION
        print(f"\nForecasting with LSTM using {len(forecast_data)} historical invoices...")
        model = get_lstm_model()
        prediction = model.predict_quantity(forecast_data)

        print(f"Forecast complete:")
        print(f"   Predicted quantity: {prediction['predicted_quantity']} products")
        print(f"   Trend: {prediction['trend']}")
        print(f"   Confidence: {prediction['confidence']:.2%}")

        return jsonify({
            'success': True,
            'output1': f"Predicted total quantity: {prediction['predicted_quantity']} products",
            'output2': f"Trend analysis: {prediction['trend']}",
            'confidence': prediction['confidence'],
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
                'name': 'CNN Invoice Detector',
                'input': 'x1 - Hoa don giay (Invoice Image)',
                'output': 'Y1 - Hoa don dien tu nhap hang',
                'architecture': 'MobileNetV2 + Custom Detection Head',
                'status': 'Ready' if cnn_model and cnn_model.model else 'Not loaded',
                'image_size': f'{cnn_model.img_height}x{cnn_model.img_width}' if cnn_model else 'Not loaded'
            },
            'model2_lstm': {
                'name': 'LSTM Text Recognizer',
                'input': 'Y1 + x2 + x3 (Historical invoices)',
                'output': 'Y2 TEXT - Du doan so luong',
                'architecture': 'Stacked LSTM with Attention',
                'status': 'Ready' if lstm_model and lstm_model.model else 'Not loaded',
                'sequence_length': lstm_model.sequence_length if lstm_model else 'Not loaded',
                'num_features': lstm_model.num_features if lstm_model else 'Not loaded'
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
