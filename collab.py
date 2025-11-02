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
%cd /content/drive/MyDrive/predict-future-import-for-Retail-store-products

# Get the current working directory after changing
DRIVE_ROOT = os.getcwd()
print(f"Working directory: {DRIVE_ROOT}")

# Add the relative path to the models directory to sys.path
sys.path.append(os.path.join(DRIVE_ROOT, 'models'))

# Import the correct model classes
from models.cnn_model import CNNInvoiceDetector
from models.lstm_model import LSTMTextRecognizer


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
cnn_model = CNNInvoiceDetector(img_height=224, img_width=224)
try:
    cnn_model.load_model(os.path.join(SAVED_MODELS, 'cnn_invoice_detector.h5'))
    print("✅ CNN model loaded from saved weights")
except:
    cnn_model.build_model()
    cnn_model.compile_model()
    print("⚠️  CNN model initialized (no saved weights found)")

lstm_model = LSTMTextRecognizer(sequence_length=10, num_features=5)
try:
    lstm_model.load_model(os.path.join(SAVED_MODELS, 'lstm_text_recognizer.h5'))
    print("✅ LSTM model loaded from saved weights")
except:
    lstm_model.build_model()
    lstm_model.compile_model()
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
        invoice_data = cnn_model.predict_invoice_data(filepath)
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
        prediction = lstm_model.predict_quantity(invoice_history)
        
        if not prediction.get('success', True):
            return jsonify({
                'success': False,
                'message': prediction.get('message', 'Forecasting failed')
            }), 500
        
        # Format outputs for frontend (matches what script.js expects)
        predicted_qty = int(prediction.get('predicted_quantity', 0))
        trend_text = prediction.get('trend', 'stable')
        recommendation = prediction.get('recommendation_text', '')
        
        return jsonify({
            'success': True,
            'output1': f"Predicted total quantity: {predicted_qty} products",
            'output2': recommendation or f"Trend analysis: {trend_text}",
            'confidence': float(prediction.get('confidence', 0.0)),
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