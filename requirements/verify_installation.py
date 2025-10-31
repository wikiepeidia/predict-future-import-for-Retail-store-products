# -*- coding: utf-8 -*-
"""
Verify Installation and Model Setup
Quick diagnostic script to check if everything is working
"""
import sys
import os
import subprocess

def check_dependencies():
    """Check if all required packages are installed"""
    print("="*60)
    print("1. Checking Dependencies...")
    print("="*60)
    
    required = {
        'tensorflow': 'TensorFlow',
        'keras': 'Keras',
        'numpy': 'NumPy',
        'pandas': 'Pandas',
        'sklearn': 'Scikit-learn',
        'flask': 'Flask',
        'PIL': 'Pillow'
    }
    
    missing = []
    for module, name in required.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - NOT INSTALLED")
            missing.append(name)
    
    # Check optional dependencies
    try:
        import cv2
        print(f"  ✓ OpenCV")
    except ImportError:
        print(f"  ⚠ OpenCV - Optional (for image processing)")
        
    try:
        import pytesseract
        print(f"  ✓ PyTesseract")
        
        # Try to run tesseract
        try:
            pytesseract.get_tesseract_version()
            print(f"  ✓ Tesseract OCR installed")
        except:
            print(f"  ⚠ Tesseract OCR binary not found (install separately)")
    except ImportError:
        print(f"  ⚠ PyTesseract - Optional (for OCR)")
    
    if missing:
        print(f"\n  ❌ Missing packages: {', '.join(missing)}")
        print(f"  Run: pip install -r requirements.txt")
        return False
    else:
        print(f"\n  ✓ All core dependencies installed!")
        return True


def check_models():
    """Check if models are available"""
    print("\n" + "="*60)
    print("2. Checking Models...")
    print("="*60)
    
    model_files = {
        'models/saved/lstm_forecast_model.h5': 'LSTM Forecasting Model',
        'models/saved/lstm_forecast_model_scaler.pkl': 'LSTM Scaler',
        'models/saved/cnn_invoice_model.h5': 'CNN OCR Model'
    }
    
    all_exist = True
    for path, name in model_files.items():
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"  ✓ {name} ({size_mb:.2f} MB)")
        else:
            print(f"  ✗ {name} - NOT FOUND")
            all_exist = False
    
    if not all_exist:
        print(f"\n  ⚠ Some models not found")
        print(f"  Run: python train_models.py")
        return False
    else:
        print(f"\n  ✓ All models ready!")
        return True


def test_model_loading():
    """Try to load models"""
    print("\n" + "="*60)
    print("3. Testing Model Loading...")
    print("="*60)
    
    try:
        # Add models to path
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        print("  Loading LSTM model...")
        from models.lstm_forecast import ImportForecastLSTM
        lstm_model = ImportForecastLSTM(lookback=30, features=5)
        print("  ✓ LSTM model initialized")
        
        print("  Loading CNN model...")
        from models.cnn_invoice_ocr import InvoiceOCRModel
        cnn_model = InvoiceOCRModel()
        print("  ✓ CNN model initialized")
        
        print("\n  ✓ Models loaded successfully!")
        return True
        
    except Exception as e:
        print(f"\n  ✗ Error loading models: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prediction():
    """Test a simple prediction"""
    print("\n" + "="*60)
    print("4. Testing Predictions...")
    print("="*60)
    
    try:
        import pandas as pd
        import numpy as np
        from models.lstm_forecast import ImportForecastLSTM
        
        # Create sample data
        print("  Creating sample data...")
        sample_data = pd.DataFrame({
            'quantity': [100, 120, 115, 130, 125, 140, 135, 150, 145, 160],
            'price': [50.0] * 10,
            'sales': [90, 108, 103.5, 117, 112.5, 126, 121.5, 135, 130.5, 144],
            'stock': [120, 144, 138, 156, 150, 168, 162, 180, 174, 192],
            'demand': [0.75] * 10
        })
        
        print("  Loading model...")
        lstm_model = ImportForecastLSTM(lookback=30, features=5)
        
        print("  Running prediction...")
        result = lstm_model.predict_next_quantity(sample_data)
        
        if result['success']:
            print(f"  ✓ Prediction: {result['predicted_quantity']:.2f} units")
            print(f"  ✓ Confidence: {result['confidence']:.2%}")
            print(f"  ✓ Trend: {result['trend']}")
            print("\n  ✓ LSTM prediction working!")
            return True
        else:
            print(f"  ✗ Prediction failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"\n  ✗ Error during prediction test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all checks"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "INSTALLATION VERIFICATION" + " "*18 + "║")
    print("║" + " "*10 + "Deep Learning Invoice Forecasting" + " "*14 + "║")
    print("╚" + "="*58 + "╝")
    print("\n")
    
    # Check dependencies first
    deps_ok = check_dependencies()
    
    # If dependencies are missing, try to install them
    if not deps_ok:
        print("\nInstalling missing dependencies...")
        try:
            # requirements.txt is in the same directory as this script
            req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_path])
            print("Dependencies installed successfully. Re-checking...")
            deps_ok = check_dependencies()
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            print("Continuing with model checks anyway...")
    
    results = {
        'dependencies': deps_ok,
        'models': check_models(),
        'loading': test_model_loading(),
        'prediction': test_prediction()
    }
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for check, status in results.items():
        status_icon = "✓" if status else "✗"
        print(f"  {status_icon} {check.capitalize()}: {'PASS' if status else 'FAIL'}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n" + "="*60)
        print("✓ ALL CHECKS PASSED!")
        print("="*60)
        print("\nYou're ready to go! Run the app with:")
        print("  python app.py")
        print("\nThen open: http://localhost:5000")
    else:
        print("\n" + "="*60)
        print("⚠ SOME CHECKS FAILED")
        print("="*60)
        print("\nNext steps:")
        if not results['dependencies']:
            print("  1. Install dependencies: pip install -r requirements.txt")
        if not results['models']:
            print("  2. Train models: python train_models.py")
        print("\nThen run this script again to verify.")
    
    print("\n")
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
