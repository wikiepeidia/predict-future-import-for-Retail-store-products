# -*- coding: utf-8 -*-
"""
Flask App - Invoice Forecast Deep Learning Demo (Simplified)
"""
import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

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


# ===== API: Model 1 - Invoice Text Prediction =====
@app.route('/api/model1/predict', methods=['POST'])
def model1_predict():
    """Model 1: Text-based invoice quantity prediction"""
    try:
        data = request.get_json()
        text_input = data.get('text', '').strip()
        
        if not text_input:
            return jsonify({'success': False, 'message': 'No input text'}), 400
        
        # Mock ML model - replace with actual model
        lines = text_input.split('\n')
        total_items = len([l for l in lines if l.strip()])
        
        mock_result = {
            'output1': f'Invoice quantity extracted: {total_items * 50} units',
            'output2': f'Predicted next quantity: {int(total_items * 50 * 1.2)} units',
            'confidence': 0.89
        }
        
        return jsonify(mock_result), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ===== API: Model 2 - Image Recognition =====
@app.route('/api/model2/recognize', methods=['POST'])
def model2_recognize():
    """Model 2: Image text recognition (OCR)"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file'}), 400
        
        # Save file
        filename = secure_filename(file.filename or 'image')
        filepath = os.path.join(UPLOAD_FOLDER, f"{datetime.now().timestamp()}_{filename}")
        file.save(filepath)
        
        # Mock OCR model - replace with actual model
        mock_result = {
            'recognized_text': 'Invoice #12345\nProduct Quantity: 150 units\nTotal Price: 4,500,000 VND',
            'confidence': 0.92
        }
        
        return jsonify(mock_result), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)