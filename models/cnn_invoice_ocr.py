# -*- coding: utf-8 -*-
"""
CNN Model for Invoice OCR and Text Extraction
Uses pre-trained OCR + Custom CNN for invoice structure recognition
"""
import os
import numpy as np
import cv2
from PIL import Image
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
import pytesseract

# Optional: Set tesseract path if needed (Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class InvoiceOCRModel:
    """CNN-based Invoice OCR Model"""
    
    def __init__(self, model_path=None):
        """Initialize the model"""
        self.model = None
        self.img_height = 224
        self.img_width = 224
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.build_model()
    
    def build_model(self):
        """Build CNN architecture for invoice classification/detection"""
        model = models.Sequential([
            # Input layer
            layers.Input(shape=(self.img_height, self.img_width, 3)),
            
            # Conv Block 1
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Conv Block 2
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Conv Block 3
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.3),
            
            # Conv Block 4
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.3),
            
            # Flatten and Dense layers
            layers.Flatten(),
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.4),
            
            # Output layer (for invoice type classification)
            layers.Dense(10, activation='softmax')  # 10 invoice categories
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        return model
    
    def preprocess_image(self, image_path):
        """Preprocess image for OCR"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                # Try PIL if cv2 fails
                img = np.array(Image.open(image_path))
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale for OCR
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply image enhancements
            # 1. Denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # 2. Thresholding
            thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            return thresh, img
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None, None
    
    def extract_text_ocr(self, image_path):
        """Extract text from invoice using Tesseract OCR"""
        try:
            preprocessed, original = self.preprocess_image(image_path)
            if preprocessed is None:
                return ""
            
            # Use pytesseract for OCR
            custom_config = r'--oem 3 --psm 6'  # OCR Engine Mode 3, Page Segmentation Mode 6
            text = pytesseract.image_to_string(preprocessed, config=custom_config)
            
            return text.strip()
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
    
    def parse_invoice_text(self, text):
        """Parse extracted text to find invoice details"""
        lines = text.split('\n')
        
        # Initialize result dictionary
        result = {
            'invoice_number': '',
            'date': '',
            'items': [],
            'total_quantity': 0,
            'total_amount': 0.0
        }
        
        # Simple parsing logic (can be enhanced with regex)
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Look for invoice number
            if any(keyword in line.lower() for keyword in ['invoice', 'hóa đơn', 'bill', 'receipt']):
                # Extract number after keyword
                parts = line.split()
                for part in parts:
                    if any(c.isdigit() for c in part):
                        result['invoice_number'] = part
                        break
            
            # Look for date
            if any(keyword in line.lower() for keyword in ['date', 'ngày', 'dated']):
                result['date'] = line
            
            # Look for quantity patterns (number + "units" or Vietnamese equivalents)
            if any(keyword in line.lower() for keyword in ['quantity', 'số lượng', 'units', 'boxes', 'items']):
                # Extract numbers from line
                numbers = [int(s) for s in line.split() if s.isdigit()]
                if numbers:
                    result['total_quantity'] += sum(numbers)
            
            # Look for amount/price
            if any(keyword in line.lower() for keyword in ['total', 'amount', 'price', 'tổng', 'thành tiền', 'vnd', '$']):
                # Extract numbers (remove commas and special chars)
                clean_line = ''.join(c if c.isdigit() or c == '.' else ' ' for c in line)
                numbers = [float(s) for s in clean_line.split() if s.replace('.', '').isdigit()]
                if numbers:
                    result['total_amount'] = max(numbers)  # Assume largest number is total
        
        return result
    
    def predict(self, image_path):
        """
        Main prediction method: Extract invoice data from image
        Returns structured invoice data
        """
        try:
            # Step 1: OCR text extraction
            extracted_text = self.extract_text_ocr(image_path)
            
            if not extracted_text:
                return {
                    'success': False,
                    'message': 'Failed to extract text from image',
                    'extracted_text': '',
                    'parsed_data': None
                }
            
            # Step 2: Parse invoice structure
            parsed_data = self.parse_invoice_text(extracted_text)
            
            # Step 3: CNN classification (optional - for invoice type detection)
            # This can be used to classify invoice types if needed
            
            return {
                'success': True,
                'extracted_text': extracted_text,
                'parsed_data': parsed_data,
                'confidence': 0.85  # Placeholder confidence score
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error during prediction: {str(e)}',
                'extracted_text': '',
                'parsed_data': None
            }
    
    def train(self, train_data, val_data, epochs=50, batch_size=32):
        """Train the CNN model"""
        if self.model is None:
            self.build_model()
        
        history = self.model.fit(
            train_data,
            validation_data=val_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[
                keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
                keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5)
            ]
        )
        
        return history
    
    def save_model(self, path='models/saved/cnn_invoice_model.h5'):
        """Save trained model"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.model.save(path)
        print(f"Model saved to {path}")
    
    def load_model(self, path):
        """Load pre-trained model"""
        self.model = keras.models.load_model(path)
        print(f"Model loaded from {path}")


# Convenience function for quick inference
def extract_invoice_data(image_path, model_path=None):
    """Quick function to extract invoice data from image"""
    model = InvoiceOCRModel(model_path)
    return model.predict(image_path)


if __name__ == "__main__":
    # Example usage
    print("CNN Invoice OCR Model initialized")
    model = InvoiceOCRModel()
    print(f"Model summary:")
    model.model.summary()
