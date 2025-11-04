from datetime import datetime
from utils.invoice_processor import build_invoice_data
from utils.database import save_invoice_to_db, get_invoices_from_db
from utils.logger import get_logger
from config import CATALOG_PATH, STORE_NAME_LOOKUP

logger = get_logger(__name__)

# Storage for invoice history (in-memory),backward compatibility
invoice_history = []


def process_invoice_image(image, cnn_model):
   
    logger.info(f"[MODEL 1] Processing invoice image (shape: {image.shape})")

    # MODEL 1: CNN Image Detection (Paper Invoice → Electric Invoice)
    
    invoice_data = cnn_model.predict_invoice_data(image)
    invoice_data['date'] = datetime.now().isoformat()

    
    # Store last 50 invoices + Create time-series sequences
    try:
        save_invoice_to_db(invoice_data)
        logger.info(f"[DATABASE] Saved Y1 output to INVOICE HISTORY DATABASE: {invoice_data['invoice_id']}")
    except Exception as e:
        logger.warning(f"[DATABASE] Failed to save to database: {e}")

    # save to memory history (backward compatibility)
    invoice_history.append(invoice_data)
    if len(invoice_history) > 50:#Keep50 invoices
        invoice_history.pop(0)

    logger.info(f"[MODEL 1] Invoice detection completed:")
    logger.info(f" - Invoice ID: {invoice_data['invoice_id']}")
    # Store name removed from logging
    logger.info(f" - Products detected: {len(invoice_data['products'])}")
    logger.info(f" - Total amount: {int(invoice_data['total_amount']):,} VND")
    logger.info(f" - Confidence: {invoice_data['detection_confidence']:.3f}")
    logger.info(f" - Total in DATABASE: {len(get_invoices_from_db(limit=1000))}")

    return invoice_data


def format_invoice_response(invoice_data):

    product_lines = [
        f"{product.get('product_name', 'Unknown')} - {product.get('quantity', 0)}"
        for product in invoice_data.get('products', [])
    ]

    recognized_text = (
        f"Invoice ID: {invoice_data['invoice_id']}\n\n"
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
    
    try:
        # Database
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
    
    return len(invoice_history)
