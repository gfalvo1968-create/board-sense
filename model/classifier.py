import os
import tensorflow as tf
import numpy as np
from PIL import Image

# Base directory (safe for Railway)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "boardsense_model.h5")
CLASS_NAMES_PATH = os.path.join(BASE_DIR, "class_names.txt")
IMG_SIZE = (128, 128)

# Load class names
try:
    with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
        class_names = [line.strip() for line in f.readlines() if line.strip()]
except:
    class_names = []

# Load model safely
try:
    model = tf.keras.models.load_model(MODEL_PATH)
except Exception as e:
    print("Model load failed:", e)
    model = None


def predict_board_grade(image_path):
    # If model not available → fallback
    if model is None:
        return "PENDING REVIEW", 0.0

    image = Image.open(image_path).convert("RGB")
    image = image.resize(IMG_SIZE)

    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    predictions = model.predict(image_array, verbose=0)[0]
    best_idx = int(np.argmax(predictions))

    best_label = class_names[best_idx] if class_names else "UNKNOWN"
    confidence = float(predictions[best_idx])

    return best_label, round(confidence, 4)
