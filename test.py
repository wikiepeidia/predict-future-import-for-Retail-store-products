"""
Quick test script to verify models are working
"""

import os
import sys

# Add models to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'models'))

# Import CONSOLIDATED models (no more duplicates!)
from models.cnn_model import CNNInvoiceDetector
from models.lstm_model import ImportForecastLSTM

print("\n" + "="*70)
print("🧪 TESTING DEEP LEARNING MODELS")
print("="*70)

# Test CNN Model
print("\n📦 Testing CNN Model...")
try:
    cnn = CNNInvoiceDetector(img_height=224, img_width=224)
    cnn.build_model()
    cnn.compile_model()
    
    print("   ✅ CNN Model built successfully")
    print(f"   Architecture: MobileNetV2 + Custom Head")
    print(f"   Input shape: ({cnn.img_height}, {cnn.img_width}, 3)")
    print(f"   Total parameters: {cnn.model.count_params():,}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test LSTM Model
print("\n📦 Testing LSTM Model...")
try:
    lstm = LSTMTextRecognizer(sequence_length=10, num_features=5)
    lstm.build_model()
    lstm.compile_model()
    
    print("   ✅ LSTM Model built successfully")
    print(f"   Architecture: Stacked LSTM with Attention")
    print(f"   Input shape: ({lstm.sequence_length}, {lstm.num_features})")
    print(f"   Total parameters: {lstm.model.count_params():,}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test CNN Prediction (with dummy data)
print("\n🔍 Testing CNN Prediction...")
try:
    from PIL import Image
    import numpy as np
    
    # Create dummy invoice image
    dummy_img = Image.new('RGB', (800, 1000), color='white')
    
    # Predict
    result = cnn.predict_invoice_data(dummy_img)
    
    print("   ✅ CNN Prediction successful")
    print(f"   Invoice ID: {result['invoice_id']}")
    print(f"   Store: {result['store_name']}")
    print(f"   Products detected: {len(result['products'])}")
    print(f"   Confidence: {result['detection_confidence']:.2%}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test LSTM Prediction (with dummy history)
print("\n📊 Testing LSTM Prediction...")
try:
    from datetime import datetime, timedelta
    
    # Create dummy invoice history
    dummy_history = []
    for i in range(15):
        dummy_history.append({
            'invoice_id': f'TEST_{i:03d}',
            'store_name': 'Test Store',
            'products': [
                {'product_name': 'Product A', 'quantity': 100 + i*10},
                {'product_name': 'Product B', 'quantity': 50 + i*5}
            ],
            'total_amount': 500000 + i*50000,
            'date': (datetime.now() - timedelta(days=15-i)).isoformat()
        })
    
    # Predict
    prediction = lstm.predict_next_quantity(dummy_history)
    
    print("   ✅ LSTM Prediction successful")
    print(f"   Predicted quantity: {prediction['predicted_quantity']} products")
    print(f"   Trend: {prediction['trend']}")
    print(f"   Confidence: {prediction['confidence']:.2%}")
    print(f"\n   📝 Recommendation:")
    for line in prediction['recommendation_text'].split('\n')[:3]:
        print(f"      {line}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("✅ ALL TESTS COMPLETED")
print("="*70)
print("\n💡 Next steps:")
print("   1. Run: python data/generate_dataset.py  (to create dataset)")
print("   2. Run: python train_models.py          (to train models)")
print("   3. Run: python app.py                   (to start web app)")
print("\n")
