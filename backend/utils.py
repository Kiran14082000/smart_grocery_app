from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch
import requests
import json
import os
from google.cloud import vision
from google.oauth2 import service_account



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


GOOGLE_CREDENTIALS_PATH = "credentials/google_vision.json"

def classify_with_google_vision(image_path):
    print("🌍 Using Google Cloud Vision...")

    # Load credentials and client
    credentials = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS_PATH)
    client = vision.ImageAnnotatorClient(credentials=credentials)

    # Load image
    with open(image_path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    # Send request with both label + web detection
    response = client.annotate_image({
        "image": image,
        "features": [
            {"type_": vision.Feature.Type.LABEL_DETECTION},
            {"type_": vision.Feature.Type.WEB_DETECTION}
        ]
    })

    # Try best guess from web detection
    if response.web_detection and response.web_detection.best_guess_labels:
        guess = response.web_detection.best_guess_labels[0].label
        if guess:
            print(f"🌐 Best guess from web: {guess}")
            return guess

    # Try first label if available
    if response.label_annotations:
        top_label = response.label_annotations[0].description
        print(f"🏷️ Top label from labels: {top_label}")
        return top_label

    raise Exception("No useful data from Google Vision")