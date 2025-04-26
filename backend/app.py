from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
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

# ✅ Spoonacular API Key (Get yours for free at spoonacular.com/food-api)
SPOONACULAR_API_KEY = "bc1a1d0fd422407baf9adc2d2e2566a0"  # <-- Replace this!

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

# 🆕 API to get Nutrition Info
@app.route('/nutrition/<item_name>')
def get_nutrition(item_name):
    try:
        search_url = f"https://api.spoonacular.com/food/ingredients/search?query={item_name}&apiKey={SPOONACULAR_API_KEY}"
        search_response = requests.get(search_url)
        search_data = search_response.json()

        if not search_data.get('results'):
            return jsonify({"error": "No item found"}), 404

        item_id = search_data['results'][0]['id']

        nutrition_url = f"https://api.spoonacular.com/food/ingredients/{item_id}/information?amount=1&apiKey={SPOONACULAR_API_KEY}"
        nutrition_response = requests.get(nutrition_url)
        nutrition_data = nutrition_response.json()

        nutrients = {}
        for nutrient in nutrition_data.get('nutrition', {}).get('nutrients', []):
            nutrients[nutrient['name']] = f"{nutrient['amount']} {nutrient['unit']}"

        return jsonify(nutrients)
    except Exception as e:
        print(f"❌ Nutrition fetch error: {e}")
        return jsonify({"error": str(e)}), 500

# 🆕 API to get Recipes
@app.route('/recipes/<item_name>')
def get_recipes(item_name):
    try:
        recipe_url = f"https://api.spoonacular.com/recipes/complexSearch?query={item_name}&number=5&apiKey={SPOONACULAR_API_KEY}"
        recipe_response = requests.get(recipe_url)
        recipe_data = recipe_response.json()

        if not recipe_data.get('results'):
            return jsonify({"error": "No recipes found"}), 404

        recipes = []
        for recipe in recipe_data['results']:
            recipes.append({
                "title": recipe.get('title', 'No Title'),
                "instructions": f"https://spoonacular.com/recipes/{recipe['title'].replace(' ', '-')}-{recipe['id']}"
            })

        return jsonify(recipes)
    except Exception as e:
        print(f"❌ Recipe fetch error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
