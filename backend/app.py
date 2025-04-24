from flask import Flask, request
from flask_cors import CORS
import os
from utils import classify_with_google_vision, classify_with_clip

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return {'message': 'Hello from Smart Grocery Backend!'}

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return {'error': 'No image provided'}, 400

    image = request.files['image']
    filename = image.filename
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(save_path)

    try:
        print("🌐 Trying Google Cloud Vision...")
        label = classify_with_google_vision(save_path)
    except Exception as e:
        print(f"⚠️ Vision API failed: {e}")
        print("🧠 Falling back to CLIP model...")
        label = classify_with_clip(save_path)


    print(f"✅ Final label: {label}")
    return {'detected_objects': [label]}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
