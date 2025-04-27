# utils.py

from google.cloud import vision
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# Load BLIP-2 model once
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
device = "mps" if torch.backends.mps.is_available() else "cpu"
model.to(device)

# For Google Cloud Vision
client = vision.ImageAnnotatorClient.from_service_account_file('credentials/google_vision.json')

def classify_with_google_vision(image_path):
    with open(image_path, 'rb') as img_file:
        content = img_file.read()

    image = vision.Image(content=content)
    response = client.web_detection(image=image)
    return response.web_detection.web_entities

def classify_with_clip(image_path):
    raw_image = Image.open(image_path).convert('RGB')

    inputs = processor(raw_image, return_tensors="pt").to(device)
    output = model.generate(**inputs)
    caption = processor.decode(output[0], skip_special_tokens=True)
    return caption

def is_grocery_related_from_web_entities(web_entities):
    food_related_keywords = [
        'fruit', 'vegetable', 'meat', 'bread', 'cheese', 'milk', 'egg', 'grain',
        'rice', 'pasta', 'cereal', 'seafood', 'fish', 'poultry', 'legume', 'bean', 'nut', 'seed', 'chocolate', 'snack', 'grocery', 'food', 'banana', 'apple', 'potato', 'tomato'
    ]

    for entity in web_entities:
        description = entity.description.lower()
        if any(food_word in description for food_word in food_related_keywords):
            print(f"🍎 Matched food-related word in '{description}'")
            return True
    return False

def is_grocery_related_from_caption(caption):
    caption = caption.lower()
    food_related_keywords = [
        'fruit', 'vegetable', 'meat', 'bread', 'cheese', 'milk', 'egg', 'grain',
        'rice', 'pasta', 'cereal', 'seafood', 'fish', 'poultry', 'legume', 'bean', 'nut', 'seed', 'chocolate', 'snack', 'grocery', 'food', 'banana', 'apple', 'potato', 'tomato'
    ]

    if any(food_word in caption for food_word in food_related_keywords):
        print(f"🍎 Matched food-related caption: '{caption}'")
        return True
    return False
