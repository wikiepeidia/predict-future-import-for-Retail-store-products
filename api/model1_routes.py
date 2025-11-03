"""
Model 1 Routes
Invoice Detection API endpoints
"""
from flask import Blueprint, request, jsonify, send_file
import cv2
import numpy as np
from werkzeug.utils import secure_filename
from datetime import datetime
import time

from services.model_loader import get_cnn_model
from services.invoice_service import process_invoice_image, format_invoice_response
from config import ALLOWED_EXTENSIONS
from utils.validators import validate_image_file, ValidationError
from utils.database import save_invoice_to_db
from utils.logger import get_logger, log_api_request
from utils.export_utils import export_invoices

# Create blueprint
model1_bp = Blueprint('model1', __name__, url_prefix='/api/model1')
logger = get_logger(__name__)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from services import get_cnn_model, process_invoice_image, format_invoice_response
from config import UPLOAD_DIR, ALLOWED_EXTENSIONS

model1_bp = Blueprint('model1', __name__, url_prefix='/api/model1')


def allowed_file(filename):
    """Kiểm tra file extension hợp lệ"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@model1_bp.route('/detect', methods=['POST'])
def detect_invoice():
    """Detect invoice from uploaded image"""
    start_time = time.time()
    
    try:
        # Validate file upload
        if 'file' not in request.files:
            raise ValidationError('No file provided')
        
        file = request.files['file']
        
        # Validate file
        validate_image_file(file)
        
        logger.info(f"Processing invoice image: {file.filename}")
        
        # Get CNN model
        cnn_model = get_cnn_model()
        if cnn_model is None:
            logger.error("CNN model not loaded")
            return jsonify({
                'success': False,
                'message': 'CNN model not loaded. Please initialize models first.'
            }), 500
        
        # Read image
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValidationError('Failed to read image')
        
        # Process invoice
        invoice_data = process_invoice_image(image, cnn_model)
        
        # Save to database
        try:
            save_invoice_to_db(invoice_data)
        except Exception as db_error:
            logger.warning(f"Failed to save invoice to database: {db_error}")
        
        # Format response
        response = format_invoice_response(invoice_data)
        
        # Log API request
        duration = (time.time() - start_time) * 1000
        log_api_request('/api/model1/detect', 'POST', 
                       params={'file': file.filename},
                       status_code=200, duration=duration)
        
        logger.info(f"Invoice processed successfully in {duration:.2f}ms")
        
        return jsonify(response)
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error processing image: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error processing image: {str(e)}'
        }), 500


@model1_bp.route('/export', methods=['GET'])
def export_invoice_data():
    """Export invoice history to file"""
    try:
        format_type = request.args.get('format', 'json').lower()
        
        if format_type not in ['json', 'csv', 'excel']:
            return jsonify({
                'success': False,
                'message': 'Invalid format. Use: json, csv, or excel'
            }), 400
        
        from utils.database import get_invoices_from_db
        invoices = get_invoices_from_db(limit=1000)
        
        if not invoices:
            return jsonify({
                'success': False,
                'message': 'No invoices to export'
            }), 404
        
        # Export
        filepath = export_invoices(invoices, format=format_type)
        
        logger.info(f"Exported {len(invoices)} invoices to {format_type}")
        
        return jsonify({
            'success': True,
            'message': f'Exported {len(invoices)} invoices',
            'file': filepath,
            'format': format_type
        })
        
    except Exception as e:
        logger.error(f"Error exporting invoices: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
