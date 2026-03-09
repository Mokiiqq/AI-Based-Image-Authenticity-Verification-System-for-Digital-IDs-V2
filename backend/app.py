from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from PIL import Image
from torchvision import transforms
import io
import os
import base64
from load_model import load_model
from database import init_db, create_user, verify_user, user_exists, save_upload, get_upload_history

# Serve frontend static files from the same server
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'project')
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

init_db()

print("Loading model...")
model = load_model()
print("Model loaded successfully!")

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        fullname = data.get('fullname')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([fullname, username, email, password]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        if user_exists(username):
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        if create_user(fullname, username, email, password):
            return jsonify({'success': True, 'message': 'Registration successful'}), 201
        else:
            return jsonify({'success': False, 'message': 'Registration failed'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password are required'}), 400
        
        if verify_user(username, password):
            return jsonify({'success': True, 'message': 'Login successful', 'username': username}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict if ID is real or fake"""
    try:
        data = request.json
        
        id_front = data.get('idFront')
        
        if not id_front:
            return jsonify({'success': False, 'message': 'Front ID image is required'}), 400
        
        result_front = process_image(id_front)
        
        overall_prediction = result_front['prediction']
        avg_confidence = result_front['confidence']
        return jsonify({
            'success': True,
            'prediction': overall_prediction,
            'confidence': round(avg_confidence, 2),
            'front': result_front,
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def process_image(base64_image):
    """Process a single image and return prediction"""
    try:
        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]
        
        image_data = base64.b64decode(base64_image)
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        
        img_tensor = transform(image).unsqueeze(0)
        
        with torch.no_grad():
            outputs = model(img_tensor)
            probs = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probs, 1)
        
        labels = ["FAKE ID", "OTHER", "REAL ID"]
        
        print(f"Raw outputs: {outputs}")
        print(f"Probabilities: {probs}")
        print(f"Predicted class: {predicted.item()}")
        print(f"Confidence: {confidence.item()}")
        print(f"Prediction: {labels[predicted.item()]}")
        
        return {
            'prediction': labels[predicted.item()],
            'confidence': confidence.item()
        }
        
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

@app.route('/api/save-upload', methods=['POST'])
def save_upload_endpoint():
    """Save upload result"""
    try:
        data = request.json
        username = data.get('username')
        image = data.get('image')
        result = data.get('result')
        
        if not all([username, image, result]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        if save_upload(username, image, result):
            return jsonify({'success': True, 'message': 'Upload saved'}), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to save upload'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/history', methods=['POST'])
def history():
    """Get upload history for a user"""
    try:
        data = request.json
        username = data.get('username')
        
        if not username:
            return jsonify({'success': False, 'message': 'Username required'}), 400
        
        uploads = get_upload_history(username)
        return jsonify(uploads), 200
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200

@app.route('/')
def serve_index():
    return app.send_static_file('login.html')

@app.route('/<path:path>')
def serve_frontend(path):
    """Serve frontend files, fallback to login.html"""
    try:
        return app.send_static_file(path)
    except Exception:
        return app.send_static_file('login.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
