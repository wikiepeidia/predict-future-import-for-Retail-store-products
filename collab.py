import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import threading
import pyngrok
from pyngrok import ngrok

# Change directory to the root of your project in Google Drive
%cd /content/drive/MyDrive/predict-future-import-for-Retail-store-products-main

# Add the relative path to the models directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'models'))

# Import the correct model classes
from models.cnn_model import CNNInvoiceDetector
from models.lstm_model import LSTMTextRecognizer


app = Flask(__name__, template_folder='ui/templates', static_folder='static')
app.config['JSON_AS_ASCII'] = False

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('saved_models', exist_ok=True)

print("Initializing Models...")
cnn_model = CNNInvoiceDetector(img_height=224, img_width=224)
try:
    cnn_model.load_model('saved_models/cnn_invoice_detector.h5')
except:
    cnn_model.build_model()
    cnn_model.compile_model()

lstm_model = LSTMTextRecognizer(sequence_length=10, num_features=5)
try:
    lstm_model.load_model('saved_models/lstm_text_recognizer.h5')
except:
    lstm_model.build_model()
    lstm_model.compile_model()

invoice_history = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    try:
        with open('ui/templates/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "<html><body><h1>Error loading page</h1></body></html>"

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
        prediction = lstm_model.predict_quantity(invoice_history)
        return jsonify({'success': True, 'data': prediction}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/models/info', methods=['GET'])
def models_info():
    return jsonify({'success': True, 'models': {'cnn': 'Ready', 'lstm': 'Ready'}}), 200

def run_flask_app():
    # Disable the reloader when running in a separate thread
    app.run(debug=True, port=5000, host='0.0.0.0', use_reloader=False)

if __name__ == '__main__':
    # Run Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    # Kill any existing ngrok processes
    os.system("killall ngrok")

    # Replace 'YOUR_AUTHTOKEN' with your actual ngrok authtoken
    ngrok.set_auth_token("34t4ixRxfJp57ypGASVtj3KRyIB_481BrEn6uYi9fHRw69wWe")

    # Connect to ngrok and print the public URL
    public_url = ngrok.connect(5000)
    print(f"Ngrok tunnel started at: {public_url}")