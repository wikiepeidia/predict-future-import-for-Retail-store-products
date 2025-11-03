"""
Model 2 Routes
Forecast API endpoints
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import time

from services.model_loader import get_lstm_model
from services.forecast_service import parse_manual_invoice_data, forecast_quantity, format_forecast_response
from services.invoice_service import invoice_history
from utils.validators import validate_invoice_data, ValidationError
from utils.database import save_forecast_to_db
from utils.logger import get_logger, log_api_request
from utils.export_utils import export_forecasts

# Create blueprint
model2_bp = Blueprint('model2', __name__, url_prefix='/api/model2')
logger = get_logger(__name__)


@model2_bp.route('/forecast', methods=['POST'])
def forecast():
    """Forecast product quantities"""
    start_time = time.time()
    
    try:
        # Get manual invoice data
        data = request.get_json() or {}
        manual_invoice = data.get('invoice_data', '').strip()
        
        # Validate input
        if manual_invoice:
            validate_invoice_data(manual_invoice)
        
        logger.info("Processing forecast request")
        
        # Get LSTM model
        lstm_model = get_lstm_model()
        if lstm_model is None:
            logger.error("LSTM model not loaded")
            return jsonify({
                'success': False,
                'message': 'LSTM model not loaded. Please initialize models first.'
            }), 500
        
        # Parse manual data if provided
        if manual_invoice:
            parsed_products = parse_manual_invoice_data(manual_invoice)
            if not parsed_products:
                raise ValidationError('No valid products found in input')
            
            logger.info(f"Parsed {len(parsed_products)} products from manual input")
            
            # Create forecast history
            forecast_history = invoice_history.copy()
            forecast_history.append({
                'products': parsed_products,
                'total_amount': sum(p['quantity'] for p in parsed_products),
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Use existing history
            if not invoice_history:
                raise ValidationError('No invoice history. Please upload invoices first or provide manual data.')
            
            forecast_history = invoice_history
        
        # Perform forecast
        forecast_result = forecast_quantity(lstm_model, forecast_history)
        
        # Save to database
        try:
            save_forecast_to_db(forecast_result)
        except Exception as db_error:
            logger.warning(f"Failed to save forecast to database: {db_error}")
        
        # Format response
        response = format_forecast_response(forecast_result)
        
        # Log API request
        duration = (time.time() - start_time) * 1000
        log_api_request('/api/model2/forecast', 'POST',
                       params={'has_manual_data': bool(manual_invoice)},
                       status_code=200, duration=duration)
        
        logger.info(f"Forecast completed successfully in {duration:.2f}ms")
        
        return jsonify(response)
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error generating forecast: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error generating forecast: {str(e)}'
        }), 500


@model2_bp.route('/export', methods=['GET'])
def export_forecast_data():
    """Export forecast history to file"""
    try:
        format_type = request.args.get('format', 'json').lower()
        
        if format_type not in ['json', 'csv', 'excel']:
            return jsonify({
                'success': False,
                'message': 'Invalid format. Use: json, csv, or excel'
            }), 400
        
        from utils.database import get_forecasts_from_db
        forecasts = get_forecasts_from_db(limit=1000)
        
        if not forecasts:
            return jsonify({
                'success': False,
                'message': 'No forecasts to export'
            }), 404
        
        # Export
        filepath = export_forecasts(forecasts, format=format_type)
        
        logger.info(f"Exported {len(forecasts)} forecasts to {format_type}")
        
        return jsonify({
            'success': True,
            'message': f'Exported {len(forecasts)} forecasts',
            'file': filepath,
            'format': format_type
        })
        
    except Exception as e:
        logger.error(f"Error exporting forecasts: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

