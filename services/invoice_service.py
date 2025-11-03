"""
Invoice Service - Xử lý logic nghiệp vụ cho hóa đơn
Theo FLOW CHART: DATASET → MODEL 1 (CNN) → Y1 Output → INVOICE HISTORY DATABASE
"""
from datetime import datetime
from utils.invoice_processor import build_invoice_data
from utils.database import save_invoice_to_db, get_invoices_from_db
from utils.logger import get_logger
from config import CATALOG_PATH, STORE_NAME_LOOKUP

logger = get_logger(__name__)

# Storage for invoice history (in-memory) - Giữ cho backward compatibility
invoice_history = []


def process_invoice_image(cnn_model, image_path):
    """
    Xử lý ảnh hóa đơn và trích xuất dữ liệu
    FLOW: x1 Images → MODEL 1 (CNN) → Y1 (Electronic Invoice JSON)
    
    Args:
        cnn_model: CNN model instance (MobileNetV2 + Custom Detection Head)
        image_path: Đường dẫn ảnh hóa đơn
        
    Returns:
        dict: Y1 Output - Dữ liệu hóa đơn điện tử (JSON)
    """
    logger.info(f"[MODEL 1] Processing invoice image: {image_path}")
    
    # MODEL 1: CNN Image Detection (Paper Invoice → Electric Invoice)
    # Architecture: MobileNetV2 (Transfer Learning) + Custom Detection Head + OpenCV Text Extraction
    invoice_data = cnn_model.predict_invoice_data(image_path)
    invoice_data['date'] = datetime.now().isoformat()
    
    # Y1 OUTPUT → INVOICE HISTORY DATABASE
    # Store last 50 invoices + Create time-series sequences
    try:
        save_invoice_to_db(invoice_data)
        logger.info(f"[DATABASE] Saved Y1 output to INVOICE HISTORY DATABASE: {invoice_data['invoice_id']}")
    except Exception as e:
        logger.warning(f"[DATABASE] Failed to save to database: {e}")
    
    # Lưu vào memory history (backward compatibility)
    invoice_history.append(invoice_data)
    if len(invoice_history) > 50:  # Giữ 50 invoices gần nhất (theo flow chart)
        invoice_history.pop(0)
    
    logger.info(f"[MODEL 1] Invoice detection completed:")
    logger.info(f"  - Invoice ID: {invoice_data['invoice_id']}")
    logger.info(f"  - Store: {invoice_data['store_name']}")
    logger.info(f"  - Products detected: {len(invoice_data['products'])}")
    logger.info(f"  - Total amount: {int(invoice_data['total_amount']):,} VND")
    logger.info(f"  - Confidence: {invoice_data['detection_confidence']:.3f}")
    logger.info(f"  - Total in DATABASE: {len(get_invoices_from_db(limit=1000))}")
    
    return invoice_data


def format_invoice_response(invoice_data):
    """
    Format invoice data thành response cho API
    
    Args:
        invoice_data: Dữ liệu hóa đơn
        
    Returns:
        dict: Response formatted
    """
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
    
    return {
        'success': True,
        'recognized_text': recognized_text,
        'confidence': invoice_data['detection_confidence'],
        'data': invoice_data,
        'total_history_count': len(invoice_history)
    }


def get_invoice_history(limit=10):
    """
    Lấy lịch sử hóa đơn từ INVOICE HISTORY DATABASE
    FLOW CHART: Y1 + x2 + x3 (Combined) stored in database
    
    Args:
        limit: Số lượng hóa đơn trả về (mặc định 10 gần nhất)
        
    Returns:
        dict: History data từ database
    """
    try:
        # Lấy từ database (primary source)
        db_invoices = get_invoices_from_db(limit=limit)
        
        return {
            'success': True,
            'count': len(db_invoices),
            'invoices': db_invoices,
            'source': 'database'
        }
    except Exception as e:
        logger.warning(f"Failed to get from database, using memory: {e}")
        # Fallback to memory
        return {
            'success': True,
            'count': len(invoice_history),
            'invoices': invoice_history[-limit:] if limit else invoice_history,
            'source': 'memory'
        }


def clear_invoice_history():
    """
    Xóa toàn bộ lịch sử hóa đơn (memory + database)
    """
    global invoice_history
    invoice_history = []
    
    try:
        from utils.database import clear_database
        clear_database()
        logger.info("Cleared invoice history from database and memory")
    except Exception as e:
        logger.warning(f"Failed to clear database: {e}")
    
    return {
        'success': True,
        'message': 'Invoice history cleared from database and memory'
    }


def get_history_count():
    """Lấy số lượng hóa đơn trong history"""
    return len(invoice_history)
