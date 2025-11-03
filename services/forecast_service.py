"""
Forecast Service - Xử lý logic dự đoán số lượng nhập hàng
Theo FLOW CHART: INVOICE HISTORY DATABASE (Y1 + x2 + x3) → MODEL 2 (LSTM) → Y2 Output
"""
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


def parse_manual_invoice_data(manual_invoice_data):
    """
    Parse dữ liệu hóa đơn nhập thủ công (x2, x3: Hóa đơn hiện tại & lịch sử)
    FLOW CHART: x2, x3 Text → Parse → Add to time series
    
    Args:
        manual_invoice_data: String input từ user (format: "Product - Quantity")
        
    Returns:
        list: Danh sách products parsed
    """
    if not manual_invoice_data or not manual_invoice_data.strip():
        return None
    
    logger.info("[INPUT] Parsing manual invoice data (x2, x3)")
    
    lines = manual_invoice_data.split('\n')
    parsed_products = []
    
    for line in lines:
        line = line.strip()
        if line and ('-' in line or ':' in line):
            # Split by - hoặc : và extract product và quantity
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
                    logger.debug(f"  Parsed: {product} - {quantity}")
                except ValueError:
                    logger.warning(f"  Skipped invalid line: {line}")
                    continue
    
    if not parsed_products:
        logger.warning("[INPUT] No valid products parsed")
        return None
    
    logger.info(f"[INPUT] Successfully parsed {len(parsed_products)} products")
    return parsed_products


def forecast_quantity(lstm_model, invoice_data_list):
    """
    Dự đoán số lượng nhập hàng
    FLOW CHART: Input Y1 + x2 + x3 (Time Series) → MODEL 2 (LSTM) → Y2 Output (Forecast)
    
    Architecture MODEL 2:
    - Stacked LSTM (128 + 64 units)
    - Attention Mechanism
    - Trend Analysis
    - Training: 70%, Testing: 10%, Validation: 20%
    
    Args:
        lstm_model: LSTM model instance
        invoice_data_list: Y1 + x2 + x3 combined time series data
        
    Returns:
        dict: Y2 TEXT (Forecast) - Predicted quantities + Confidence + Trends
    """
    logger.info(f"[MODEL 2] Starting LSTM forecasting with {len(invoice_data_list)} records")
    logger.info(f"[MODEL 2] Input: Y1 (from DATABASE) + x2 + x3 (manual inputs)")
    
    # MODEL 2: LSTM Quantity Forecasting
    # Input: Time series từ INVOICE HISTORY DATABASE
    # Output: Y2 TEXT (Forecast predictions)
    prediction = lstm_model.predict_quantity(invoice_data_list)
    
    if not prediction.get('success', True):
        logger.error(f"[MODEL 2] Forecasting failed: {prediction.get('message')}")
        return {
            'success': False,
            'message': prediction.get('message', 'Forecasting failed')
        }
    
    logger.info("[MODEL 2] Forecast completed successfully:")
    logger.info(f"  - Predicted quantity: {prediction.get('predicted_quantity', 0):.0f} products")
    logger.info(f"  - Trend: {prediction.get('trend', 'unknown')}")
    logger.info(f"  - Confidence: {prediction.get('confidence', 0.0):.2%}")
    logger.info(f"  - Recommendation: {prediction.get('recommendation_text', 'N/A')}")
    
    return prediction


def format_forecast_response(prediction, history_count=None):
    """
    Format Y2 Output (forecast result) thành response cho FINAL OUTPUT / UI
    
    FLOW CHART: Y2 Output → FINAL OUTPUT/UI
    - Y1: Extracted Products
    - Y2: Predicted Quantities
    - Confidence Scores + Trends
    
    Args:
        prediction: Y2 Output từ MODEL 2
        history_count: Số lượng records trong time series
        
    Returns:
        dict: Response cho UI
    """
    predicted_qty = int(prediction.get('predicted_quantity', 0))
    trend_text = prediction.get('trend', 'stable')
    recommendation = prediction.get('recommendation_text', '')
    confidence = float(prediction.get('confidence', 0.0))
    
    logger.info("[OUTPUT] Formatting Y2 output for FINAL OUTPUT/UI")
    
    return {
        'success': True,
        'message': 'Forecast completed successfully',
        'predicted_quantity': predicted_qty,
        'trend': trend_text,
        'confidence': confidence,
        'recommendation': prediction.get('recommendation', 'maintain'),
        'recommendation_text': recommendation or f"Trend analysis: {trend_text}",
        'history_count': history_count or 0,
        'timestamp': datetime.now().isoformat()
    }
