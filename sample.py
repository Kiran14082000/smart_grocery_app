import cv2
from pyzbar.pyzbar import decode
import numpy as np
import time
import requests

def fetch_product_info(barcode):
    """Fetch product info from Open Food Facts using the barcode."""
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get('status') == 1:
            product = data['product']
            name = product.get('product_name', 'Unknown Product')
            nutriments = product.get('nutriments', {})
            ingredients = product.get('ingredients_text', 'Ingredients not available.')
            nova_group = product.get('nova_group', 'Unknown')
            nutriscore_grade = product.get('nutriscore_grade', 'Unknown').upper()
            ecoscore_grade = product.get('ecoscore_grade', 'Unknown').upper()

            # Try fetching main nutrients
            energy = nutriments.get('energy-kj_value_computed') or nutriments.get('energy-kj') or nutriments.get('energy_100g')
            sugars = nutriments.get('sugars_100g')
            proteins = nutriments.get('proteins_100g')

            result = f"\n🛒 Product: {name}"

            important_info_found = False

            if energy is not None:
                result += f"\n⚡ Energy: {round(float(energy))} kJ / 100g"
                important_info_found = True
            if sugars is not None:
                result += f"\n🍭 Sugars: {sugars} g / 100g"
                important_info_found = True
            if proteins is not None:
                result += f"\n🥩 Proteins: {proteins} g / 100g"
                important_info_found = True

            result += f"\n🏷️ Nova Group: {nova_group}"
            result += f"\n🅰️ NutriScore Grade: {nutriscore_grade}"
            result += f"\n🌍 EcoScore Grade: {ecoscore_grade}"

            # If no important nutrition info found, fallback to ingredients
            if not important_info_found:
                result += f"\n📋 Ingredients: {ingredients}"

            return result

        else:
            return "❌ Product not found."
    except Exception as e:
        print(f"❌ Error fetching product info: {e}")
        return "❌ Error fetching product info."

def scan_barcode_from_camera():
    cap = cv2.VideoCapture(1)  # 0 = default webcam, 1 = iPhone/Continuity camera

    if not cap.isOpened():
        print("❌ Cannot open camera")
        return

    print("🚀 Scanning for barcodes. Press 'q' to quit.")

    last_detected = None
    last_detected_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to grab frame")
            break

        current_time = time.time()

        # Decode barcodes in the frame
        barcodes = decode(frame)

        if barcodes and (current_time - last_detected_time > 3):  # 3 second cooldown
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                barcode_type = barcode.type

                # Draw rectangle or polygon
                pts = [(pt.x, pt.y) for pt in barcode.polygon]
                if len(pts) == 4:
                    pts_array = np.array(pts, np.int32)
                    pts_array = pts_array.reshape((-1, 1, 2))
                    cv2.polylines(frame, [pts_array], True, (0, 255, 0), 2)
                else:
                    rect = cv2.boundingRect(np.array(pts, np.int32))
                    x, y, w, h = rect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                print(f"\n📦 Detected {barcode_type}: {barcode_data}")

                # Fetch and print product info
                product_info = fetch_product_info(barcode_data)
                print(product_info)
                print("-" * 60)  # separator line after each product

                last_detected = barcode_data
                last_detected_time = current_time

                break  # Only process one barcode at a time

        # Show the camera feed
        cv2.imshow('📸 Barcode Scanner', frame)

        # Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    scan_barcode_from_camera()
