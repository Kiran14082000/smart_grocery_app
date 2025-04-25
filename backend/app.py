from flask import Flask, request
from flask_cors import CORS
import os
from utils import (
    classify_with_google_vision,
    classify_with_clip,
    is_grocery_related_from_web_entities,
    is_grocery_related_from_caption
)

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
        web_entities = classify_with_google_vision(save_path)
        if is_grocery_related_from_web_entities(web_entities):
            detected_label = web_entities[0].description if web_entities[0].description else "Grocery Item"
            print(f"✅ Detected and confirmed by Vision: {detected_label}")
            return {'detected_objects': [detected_label]}
        else:
            print("⚠️ Google Vision could not confirm grocery item.")
    except Exception as e:
        print(f"❌ Vision API error: {e}")

    # Fallback to BLIP-2
    try:
        print("🧠 Falling back to BLIP-2 Captioning...")
        caption = classify_with_clip(save_path)
        if is_grocery_related_from_caption(caption):
            print(f"✅ Detected and confirmed by BLIP-2: {caption}")
            return {'detected_objects': [caption]}
        else:
            print("❌ BLIP-2 also could not confirm grocery item.")
    except Exception as e:
        print(f"❌ BLIP-2 error: {e}")

    return {'detected_objects': ['Not a valid grocery item']}, 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
