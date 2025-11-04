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
    
    # Collect all unique products from history
    product_stats = {}
    for invoice in invoice_data_list:
        products = invoice.get('products', [])
        for product in products:
            product_name = product.get('product_name', 'Unknown')
            quantity = product.get('quantity', 0)
            
            if product_name not in product_stats:
                product_stats[product_name] = {
                    'quantities': [],
                    'total': 0,
                    'count': 0
                }
            
            product_stats[product_name]['quantities'].append(quantity)
            product_stats[product_name]['total'] += quantity
            product_stats[product_name]['count'] += 1
    
    # MODEL 2: LSTM Quantity Forecasting
    # Input: Time series từ INVOICE HISTORY DATABASE
    # Output: Y2 TEXT (Forecast predictions)
    prediction = lstm_model.predict_next_quantity(invoice_data_list)
    
    if not prediction.get('success', True):
        logger.error(f"[MODEL 2] Forecasting failed: {prediction.get('message')}")
        return {
            'success': False,
            'message': prediction.get('message', 'Forecasting failed')
        }
    
    # Generate per-product predictions based on historical proportions
    total_predicted = prediction.get('predicted_quantity', 0)
    predicted_products = []
    
    if product_stats:
        # Calculate total historical quantity
        total_historical = sum(stats['total'] for stats in product_stats.values())
        
        # Distribute predicted quantity proportionally
        for product_name, stats in sorted(product_stats.items(), key=lambda x: x[1]['total'], reverse=True):
            proportion = stats['total'] / total_historical if total_historical > 0 else 0
            predicted_qty = int(total_predicted * proportion)
            avg_qty = stats['total'] / stats['count']
            
            if predicted_qty > 0:  # Only include products with predicted quantity > 0
                predicted_products.append({
                    'product_name': product_name,
                    'predicted_quantity': predicted_qty,
                    'historical_average': int(avg_qty),
                    'frequency': stats['count']
                })
        
        logger.info(f"  - Generated predictions for {len(predicted_products)} products")
    
    # Add per-product predictions to result
    prediction['predicted_products'] = predicted_products
    
    logger.info("[MODEL 2] Forecast completed successfully:")
    logger.info(f"  - Predicted quantity: {prediction.get('predicted_quantity', 0):.0f} products")
    logger.info(f"  - Trend: {prediction.get('trend', 'unknown')}")
    logger.info(f"  - Confidence: {prediction.get('confidence', 0.0):.2%}")
    logger.info(f"  - Individual products: {len(predicted_products)}")
    
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
    confidence = float(prediction.get('confidence', 0.0))
    historical_mean = prediction.get('historical_mean', predicted_qty)
    predicted_products = prediction.get('predicted_products', [])
    
    logger.info("[OUTPUT] Formatting Y2 output for FINAL OUTPUT/UI")
    
    # Generate output1 - Main prediction result with product details
    if trend_text == 'increasing':
        trend_icon = '📈'
        trend_desc = 'Increasing'
    elif trend_text == 'decreasing':
        trend_icon = '📉'
        trend_desc = 'Decreasing'
    else:
        trend_icon = '➡️'
        trend_desc = 'Stable'
    
    output1 = f"{trend_icon} Total Predicted Import: {predicted_qty} products (Trend: {trend_desc})"
    
    # Generate output2 - Simple product list
    output2_lines = []
    
    # Product-level predictions - SIMPLE FORMAT
    if predicted_products:
        output2_lines.append("📦 Predicted Products:")
        output2_lines.append("")
        for i, product in enumerate(predicted_products[:15], 1):  # Show top 15 products
            product_name = product['product_name']
            pred_qty = product['predicted_quantity']
            output2_lines.append(f"{i}. {product_name}: {pred_qty} products")
        
        if len(predicted_products) > 15:
            remaining = len(predicted_products) - 15
            output2_lines.append(f"... and {remaining} more products")
        
        output2_lines.append("")
    
    # Simple summary
    output2_lines.append(f"Total: {predicted_qty} products")
    output2_lines.append(f"Trend: {trend_desc}")
    output2_lines.append(f"Historical Average: {int(historical_mean)} products")
    output2_lines.append(f"Confidence: {confidence * 100:.1f}%")
    
    output2 = '\n'.join(output2_lines)
    
    return {
        'success': True,
        'message': 'Forecast completed successfully',
        'predicted_quantity': predicted_qty,
        'predicted_products': predicted_products,
        'trend': trend_text,
        'confidence': confidence,
        'output1': output1,
        'output2': output2,
        'recommendation': prediction.get('recommendation', 'maintain'),
        'recommendation_text': output2,
        'history_count': history_count or 0,
        'timestamp': datetime.now().isoformat()
    }
