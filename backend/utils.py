from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch
from google.cloud import vision
from google.oauth2 import service_account

# =========================
# CONFIGURATION
# =========================

# Categories that define valid grocery-related concepts
GROCERY_CATEGORIES = ["food", "fruit", "vegetable", "grocery", "produce", "meal"]

# Path to your Google Cloud Vision credentials JSON
GOOGLE_CREDENTIALS_PATH = "credentials/google_vision.json"

# Initialize Google Vision client
credentials = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH)
vision_client = vision.ImageAnnotatorClient(credentials=credentials)

# Load BLIP-2 model ONCE at startup
print("🚀 Loading BLIP-2 model (only once)...")
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b",
    device_map="auto",
    torch_dtype=torch.float16
)
print("✅ BLIP-2 model loaded!")

# =========================
# MAIN FUNCTIONS
# =========================

def classify_with_google_vision(image_path):
    """Classify an image using Google Cloud Vision and return labels, web entities."""
    print("🌍 Using Google Cloud Vision...")

    with open(image_path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    response = vision_client.web_detection(image=image)

    if response.web_detection and response.web_detection.web_entities:
        web_entities = response.web_detection.web_entities
        print(f"🌐 Found web entities: {[e.description for e in web_entities if e.description]}")
        return web_entities

    raise Exception("No useful data from Google Vision")

def classify_with_clip(image_path):
    """Classify an image using already-loaded BLIP-2 model."""
    print("🧠 Using BLIP-2 to describe image...")

    image = Image.open(image_path).convert('RGB')

    # Determine model device automatically
    device = next(model.parameters()).device
    print(f"🔍 Model is running on: {device}")

    inputs = processor(images=image, return_tensors="pt")
    inputs = {key: val.to(device) for key, val in inputs.items()}

    generated_ids = model.generate(**inputs, max_new_tokens=20)
    caption = processor.decode(generated_ids[0], skip_special_tokens=True)

    caption = caption.lower()
    print(f"🖼️ BLIP-2 generated caption: {caption}")
    return caption

def is_grocery_related_from_web_entities(web_entities):
    """Check if Google Vision's web entities match grocery categories."""
    for entity in web_entities:
        if entity.description:
            desc = entity.description.lower()
            for keyword in GROCERY_CATEGORIES:
                if keyword in desc:
                    print(f"✅ Web entity '{desc}' matched grocery category '{keyword}'")
                    return True
    return False

def is_grocery_related_from_caption(caption):
    """Check if BLIP-2 caption matches grocery categories."""
    caption = caption.lower()
    for keyword in GROCERY_CATEGORIES:
        if keyword in caption:
            print(f"✅ Caption '{caption}' matched grocery category '{keyword}'")
            return True
    return False
