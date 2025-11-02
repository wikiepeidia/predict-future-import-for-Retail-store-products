import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import threading
import pyngrok
from pyngrok import ngrok

# Change directory to the root of your project in Google Drive
# UPDATED FOLDER NAME
# %cd /content/drive/MyDrive/predict-future-import-for-Retail-store-products

# Get the current working directory after changing
DRIVE_ROOT = os.getcwd()
print(f"Working directory: {DRIVE_ROOT}")

# Add the relative path to the models directory to sys.path
sys.path.append(os.path.join(DRIVE_ROOT, 'models'))

# Import the correct model classes
from models.cnn_model import CNNInvoiceDetector  # Deep learning CNN with MobileNetV2
from models.lstm_forecast import ImportForecastLSTM  # Changed from LSTMTextRecognizer


# Fix Flask paths to use absolute paths
TEMPLATE_FOLDER = os.path.join(DRIVE_ROOT, 'ui', 'templates')
STATIC_FOLDER = os.path.join(DRIVE_ROOT, 'static')

print(f"Template folder: {TEMPLATE_FOLDER}")
print(f"Static folder: {STATIC_FOLDER}")

app = Flask(__name__, 
            template_folder=TEMPLATE_FOLDER,
            static_folder=STATIC_FOLDER,
            static_url_path='/static')
app.config['JSON_AS_ASCII'] = False

UPLOAD_FOLDER = os.path.join(DRIVE_ROOT, 'uploads')
SAVED_MODELS = os.path.join(DRIVE_ROOT, 'saved_models')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SAVED_MODELS, exist_ok=True)

print("Initializing Models...")
cnn_model = CNNInvoiceDetector(img_height=224, img_width=224)  # Deep learning CNN
cnn_model_path = os.path.join(SAVED_MODELS, 'cnn_invoice_detector.weights.h5')
print(f"Looking for CNN model at: {cnn_model_path}")
print(f"File exists: {os.path.exists(cnn_model_path)}")
try:
    cnn_model.load_model(cnn_model_path)
    print("✅ CNN model loaded from saved weights")
except Exception as e:
    print(f"⚠️  CNN model load failed: {e}")
    print("⚠️  CNN model initialized (no saved weights found)")

lstm_model = ImportForecastLSTM(lookback=30, features=5)
lstm_model_path = os.path.join(SAVED_MODELS, 'lstm_text_recognizer.weights.h5')
print(f"Looking for LSTM model at: {lstm_model_path}")
print(f"File exists: {os.path.exists(lstm_model_path)}")
try:
    lstm_model.load_model(lstm_model_path)
    print("✅ LSTM model loaded from saved weights")
except Exception as e:
    print(f"⚠️  LSTM model load failed: {e}")
    print("⚠️  LSTM model initialized (no saved weights found)")

invoice_history = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    try:
        index_path = os.path.join(TEMPLATE_FOLDER, 'index.html')
        print(f"Loading index from: {index_path}")
        print(f"Static files at: {STATIC_FOLDER}")
        print(f"CSS should be at: {os.path.join(STATIC_FOLDER, 'style.css')}")
        print(f"CSS exists: {os.path.exists(os.path.join(STATIC_FOLDER, 'style.css'))}")
        
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"<html><body><h1>Error loading page</h1><p>{str(e)}</p><p>Template path: {TEMPLATE_FOLDER}</p></body></html>"

# Add explicit static file serving for debugging
@app.route('/static/<path:filename>')
def serve_static(filename):
    from flask import send_from_directory
    print(f"Static file requested: {filename}")
    static_path = os.path.join(STATIC_FOLDER, filename)
    print(f"Serving from: {static_path}")
    print(f"File exists: {os.path.exists(static_path)}")
    return send_from_directory(STATIC_FOLDER, filename)

@app.route('/api/model1/detect', methods=['POST'])
def model1_detect():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False}), 400
        file = request.files['image']
        if not file.filename or not allowed_file(file.filename):
            return jsonify({'success': False}), 400
        filename = secure_filename(file.filename or 'invoice')
        filepath = os.path.join(UPLOAD_FOLDER, f"{datetime.now().timestamp()}_{filename}")
        file.save(filepath)
        # Extract invoice data using CNN (Deep Learning)
        invoice_data = cnn_model.predict_invoice_data(filepath)  # Back to predict_invoice_data
        invoice_data['date'] = datetime.now().isoformat()
        invoice_history.append(invoice_data)
        return jsonify({'success': True, 'data': invoice_data}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/model2/forecast', methods=['POST'])
def model2_forecast():
    try:
        if not invoice_history:
            return jsonify({'success': False, 'message': 'No history'}), 400
        
        # Call LSTM predict_quantity method
        prediction = lstm_model.predict_next_quantity(invoice_history)
        
        if not prediction.get('success', True):
            return jsonify({
                'success': False,
                'message': prediction.get('message', 'Forecasting failed')
            }), 500
        
        # Format outputs for frontend (matches what script.js expects)
        predicted_qty = int(prediction.get('predicted_quantity', 0))
        trend_text = prediction.get('trend', 'stable')
        confidence = float(prediction.get('confidence', 0.0))
        hist_mean = prediction.get('historical_mean', 0)
        
        # Trend emoji and English translation
        trend_emoji = "📈" if trend_text == "increasing" else "📉" if trend_text == "decreasing" else "➡️"
        trend_vn = "tăng" if trend_text == "increasing" else "giảm" if trend_text == "decreasing" else "ổn định"
        
        # Recommendation based on trend
        if trend_text == "increasing":
            rec_en = f"Recommended: Increase import to ~{int(predicted_qty * 1.1)} products"
            rec_vn = f"Khuyến nghị: Tăng nhập hàng lên ~{int(predicted_qty * 1.1)} sp"
        elif trend_text == "decreasing":
            rec_en = f"Recommended: Reduce import to ~{int(predicted_qty * 0.9)} products"
            rec_vn = f"Khuyến nghị: Giảm nhập hàng xuống ~{int(predicted_qty * 0.9)} sp"
        else:
            rec_en = f"Recommended: Maintain average level (~{int(hist_mean)} products)"
            rec_vn = f"Khuyến nghị: Duy trì mức trung bình (~{int(hist_mean)} sp)"
        
        # Extract top products from history
        product_counts = {}
        for inv in invoice_history:
            if 'products' in inv and isinstance(inv['products'], list):
                for product in inv['products']:
                    if isinstance(product, dict):
                        # CNN uses 'product_name' field
                        name = product.get('product_name', product.get('name', 'Unknown'))
                        qty = product.get('quantity', 1)
                        if name != 'Unknown':
                            product_counts[name] = product_counts.get(name, 0) + qty
        
        # Get top 3 products
        top_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        if top_products and sum(product_counts.values()) > 0:
            top_products_text = "\n".join([
                f"{i+1}. {name}: ~{int(qty * predicted_qty / sum(product_counts.values()))} products"
                for i, (name, qty) in enumerate(top_products)
            ])
        else:
            # Generate sample products if no real data (for demo purposes)
            top_products_text = f"1. Nước cam: ~{int(predicted_qty * 0.25)} products\n2. Cà phê đen: ~{int(predicted_qty * 0.20)} products\n3. Nước suối: ~{int(predicted_qty * 0.18)} products"
        
        # Build detailed output (English only, clean format)
        output1 = f"""Predicted total quantity: {predicted_qty} products

{trend_emoji} Trend: {trend_text}
Recommended: {'Increase' if trend_text == 'increasing' else 'Reduce' if trend_text == 'decreasing' else 'Maintain'} import to ~{int(predicted_qty * 1.1 if trend_text == 'increasing' else predicted_qty * 0.9 if trend_text == 'decreasing' else hist_mean)} products"""
        
        output2 = f"""🏆 Top products to import:
{top_products_text}

"""
        
        return jsonify({
            'success': True,
            'output1': output1,
            'output2': output2,
            'confidence': confidence,
            'data': prediction
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/models/info', methods=['GET'])
def models_info():
    return jsonify({'success': True, 'models': {'cnn': 'Ready', 'lstm': 'Ready'}}), 200

def run_flask_app():
    import socket
    
    # Pick an available port
    def pick_port(preferred=5000):
        for port in range(preferred, preferred + 10):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('0.0.0.0', port))
                    return port
            except OSError:
                continue
        return preferred + 100  # Fallback to high port
    
    port = pick_port(5000)
    print(f"🚀 Starting Flask on port {port}")
    
    # Return port so ngrok can use it
    global flask_port
    flask_port = port
    
    # Disable the reloader when running in a separate thread
    app.run(debug=False, port=port, host='0.0.0.0', use_reloader=False)

if __name__ == '__main__':
    flask_port = 5000  # Default
    
    # Run Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    
    # Wait a moment for Flask to start and set the port
    import time
    time.sleep(2)

    # Kill any existing ngrok processes
    os.system("killall ngrok > /dev/null 2>&1")

    # Replace 'YOUR_AUTHTOKEN' with your actual ngrok authtoken
    ngrok.set_auth_token("34t4ixRxfJp57ypGASVtj3KRyIB_481BrEn6uYi9fHRw69wWe")

    # Connect to ngrok with the actual port Flask is using
    public_url = ngrok.connect(flask_port)
    print(f"✅ Ngrok tunnel started at: {public_url}")
    print(f"📱 Access your app at: {public_url}")
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")