from pathlib import Path
import numpy as np
from PIL import Image
import tensorflow as tf

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "boardsense_model.h5"
CLASS_NAMES_PATH = BASE_DIR / "model" / "class_names.txt"
IMG_SIZE = (128, 128)

_model = None
_class_names = None


def load_model_and_classes():
    global _model, _class_names

    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        _model = tf.keras.models.load_model(MODEL_PATH)

    if _class_names is None:
        if not CLASS_NAMES_PATH.exists():
            raise FileNotFoundError(f"Class names file not found: {CLASS_NAMES_PATH}")
        with CLASS_NAMES_PATH.open("r", encoding="utf-8") as f:
            _class_names = [line.strip() for line in f if line.strip()]

    if not _class_names:
        raise ValueError("No class names loaded")

    return _model, _class_names


def preprocess_image(image_path: str):
    img = Image.open(image_path).convert("RGB")
    img = img.resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr


preds = model.predict(image_tensor, verbose=0)[0]
best_index = int(np.argmax(preds))
confidence = round(float(preds[best_index]) * 100, 2)
label = class_names[best_index].upper()

if confidence >= 80:
    return label, confidence, f"Predicted as {label}"
elif confidence >= 60:
    return label, confidence, f"Low confidence prediction: {label}"
else:
    return "PENDING REVIEW", confidence, "Unseen or uncertain board, review manually"

}
