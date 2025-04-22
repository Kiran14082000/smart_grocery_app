from flask import Flask, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def home():
    return {'message': '👋 Hello from Grocery AI Backend! Use POST /upload to send images.'}


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return {'error': 'No image part in the request'}, 400

    image = request.files['image']
    filename = image.filename
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(save_path)

    print(f"✅ Received image: {filename} — saved to {save_path}")
    return {'message': 'Image received', 'filename': filename}, 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
