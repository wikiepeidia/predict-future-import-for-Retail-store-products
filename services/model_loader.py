"""
Model Loader - Quản lý việc load và khởi tạo models
"""
import os
from pathlib import Path

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from models.cnn_model import CNNInvoiceDetector
from models.lstm_model import ImportForecastLSTM
from config import CNN_MODEL_PATH, LSTM_MODEL_PATH, LSTM_SEQUENCE_LENGTH, LSTM_NUM_FEATURES

# Global model instances
cnn_model = None
lstm_model = None


def initialize_models():
    """Khởi tạo models khi start app"""
    print("\n" + "="*60)
    print("INITIALIZING DEEP LEARNING MODELS")
    print("="*60)
    
    # Model 1: CNN
    print("Loading Model 1: CNN Invoice Detector...")
    global cnn_model
    try:
        cnn_model = CNNInvoiceDetector(img_height=224, img_width=224)
        if CNN_MODEL_PATH.exists():
            cnn_model.load_model(str(CNN_MODEL_PATH))
            print(f"   [OK] Loaded CNN weights from {CNN_MODEL_PATH.name}")
        else:
            cnn_model.build_model()
            cnn_model.compile_model()
            print("   [WARNING] Pre-trained CNN weights not found; using freshly initialized model")
    except Exception as exc:
        print(f"   [WARNING] Unable to load CNNInvoiceDetector: {exc}")
        cnn_model = CNNInvoiceDetector(img_height=224, img_width=224)
        cnn_model.build_model()
        cnn_model.compile_model()
    
    # Model 2: LSTM
    print("Loading Model 2: LSTM Forecasting...")
    global lstm_model
    try:
        lstm_model = ImportForecastLSTM(lookback=LSTM_SEQUENCE_LENGTH, features=LSTM_NUM_FEATURES)
        if LSTM_MODEL_PATH.exists():
            lstm_model.load_model(str(LSTM_MODEL_PATH))
            print(f"   [OK] Loaded LSTM weights from {LSTM_MODEL_PATH.name}")
        else:
            lstm_model.build_model()
            print("   [WARNING] Pre-trained LSTM weights not found; using freshly initialized model")
    except Exception as exc:
        print(f"   [WARNING] Unable to load ImportForecastLSTM: {exc}")
        lstm_model = ImportForecastLSTM(lookback=LSTM_SEQUENCE_LENGTH, features=LSTM_NUM_FEATURES)
        lstm_model.build_model()
    
    print("="*60)
    print("MODELS INITIALIZED - READY TO BUILD ON DEMAND")
    print("="*60 + "\n")


def get_cnn_model():
    """Lazy load CNN model"""
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
            print(f"   [WARNING] Fallback to fresh CNNInvoiceDetector due to: {exc}")
            cnn_model = CNNInvoiceDetector(img_height=224, img_width=224)
            cnn_model.build_model()
            cnn_model.compile_model()
    return cnn_model


def get_lstm_model():
    """Lazy load LSTM model"""
    global lstm_model
    if lstm_model is None:
        print("Loading ImportForecastLSTM on demand...")
        try:
            lstm_model = ImportForecastLSTM(lookback=LSTM_SEQUENCE_LENGTH, features=LSTM_NUM_FEATURES)
            if LSTM_MODEL_PATH.exists():
                lstm_model.load_model(str(LSTM_MODEL_PATH))
            else:
                lstm_model.build_model()
        except Exception as exc:
            print(f"   [WARNING] Fallback to fresh ImportForecastLSTM due to: {exc}")
            lstm_model = ImportForecastLSTM(lookback=LSTM_SEQUENCE_LENGTH, features=LSTM_NUM_FEATURES)
            lstm_model.build_model()
    return lstm_model


def get_models_info():
    """Lấy thông tin về models đã load"""
    return {
        'model1_cnn': {
            'name': 'Invoice OCR Model (CNN + OCR)',
            'input': 'x1 - Hóa đơn giấy (invoice image)',
            'output': 'Y1 - Hóa đơn điện tử nhập hàng',
            'architecture': 'MobileNetV2 Transfer Learning + Custom Detection Head',
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
    }
