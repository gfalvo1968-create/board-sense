import tensorflow as tf
import numpy as np
from PIL import Image

MODEL_PATH = "model/boardsense_model.h5"
CLASS_NAMES_PATH = "model/class_names.txt"
IMG_SIZE = (128, 128)

model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
    class_names = [line.strip() for line in f.readlines() if line.strip()]

def predict_board_grade(image_path):
    image = Image.open(image_path).convert("RGB")
    image = image.resize(IMG_SIZE)
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    predictions = model.predict(image_array, verbose=0)[0]
    best_idx = int(np.argmax(predictions))
    best_label = class_names[best_idx]
    confidence = float(predictions[best_idx])

    return best_label, round(confidence, 4)
