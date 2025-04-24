from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch
import requests
import json



BING_API_KEY = "YOUR_BING_KEY_HERE"
BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/images/visualsearch"

def classify_with_clip(image_path):
    # BLIP-2 Captioning (no label list needed!)
    print("🧠 Using BLIP-2 to describe image...")

    processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
    model = Blip2ForConditionalGeneration.from_pretrained(
        "Salesforce/blip2-opt-2.7b", device_map="auto", torch_dtype=torch.float16
    )

    image = Image.open(image_path).convert('RGB')
    inputs = processor(images=image, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
    generated_ids = model.generate(**inputs, max_new_tokens=20)
    caption = processor.decode(generated_ids[0], skip_special_tokens=True)

    print(f"🖼️ BLIP-2 generated caption: {caption}")
    return caption

def classify_with_web(image_path):
    print("🌍 Sending image to Bing Visual Search...")

    headers = {
        "Ocp-Apim-Subscription-Key": BING_API_KEY
    }

    with open(image_path, "rb") as img_file:
        files = {
            'image': ("image.jpg", img_file, "multipart/form-data")
        }

        response = requests.post(BING_ENDPOINT, headers=headers, files=files)
        response.raise_for_status()

        data = response.json()
        print("✅ Bing response received")

        # Extract best guess from tags or captions
        tags = data.get("tags", [])
        if tags:
            display_name = tags[0].get("displayName", "")
            print(f"🔍 Bing suggests: {display_name}")
            return display_name

        raise Exception("No tags found in Bing response")
