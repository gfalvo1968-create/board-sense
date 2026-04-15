import os
from pathlib import Path
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "images"
LABELS_FILE = BASE_DIR / "db" / "labels.csv"
MODEL_OUT = BASE_DIR / "model" / "boardsense_model.h5"
CLASS_NAMES_OUT = BASE_DIR / "model" / "class_names.txt"

IMG_SIZE = (128, 128)
BATCH_SIZE = 8
EPOCHS = 8

if not LABELS_FILE.exists():
    raise ValueError("labels.csv not found")

label_df = pd.read_csv(LABELS_FILE)

if "filename" not in label_df.columns or "label" not in label_df.columns:
    raise ValueError("labels.csv must contain filename and label columns")

label_df["filename"] = label_df["filename"].astype(str).str.strip()
label_df["label"] = label_df["label"].astype(str).str.strip().str.lower()

label_df["filepath"] = label_df["filename"].apply(lambda x: str(DATA_DIR / x))
label_df = label_df[label_df["filepath"].apply(os.path.exists)].copy()

if len(label_df) < 8:
    raise ValueError("Need at least 8 labeled images to train the model")

if label_df["label"].nunique() < 2:
    raise ValueError("Need at least 2 different label classes to train the model")

class_names = sorted(label_df["label"].unique().tolist())
class_to_index = {name: i for i, name in enumerate(class_names)}
label_df["label_index"] = label_df["label"].map(class_to_index)

test_size = 0.3 if len(label_df) >= 10 else 0.4

train_df, val_df = train_test_split(
    label_df,
    test_size=test_size,
    random_state=42,
    stratify=label_df["label_index"]
)


def load_image(path, label):
    image = tf.io.read_file(path)
    image = tf.image.decode_image(image, channels=3, expand_animations=False)
    image = tf.image.resize(image, IMG_SIZE)
    image = tf.cast(image, tf.float32) / 255.0
    return image, label


train_ds = tf.data.Dataset.from_tensor_slices(
    (train_df["filepath"].values, train_df["label_index"].values)
)
train_ds = train_ds.map(load_image).shuffle(100).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

val_ds = tf.data.Dataset.from_tensor_slices(
    (val_df["filepath"].values, val_df["label_index"].values)
)
val_ds = val_ds.map(load_image).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

model = models.Sequential([
    layers.Input(shape=(128, 128, 3)),
    layers.Conv2D(16, (3, 3), activation="relu"),
    layers.MaxPooling2D(),
    layers.Conv2D(32, (3, 3), activation="relu"),
    layers.MaxPooling2D(),
    layers.Conv2D(64, (3, 3), activation="relu"),
    layers.MaxPooling2D(),
    layers.Flatten(),
    layers.Dense(64, activation="relu"),
    layers.Dropout(0.3),
    layers.Dense(len(class_names), activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    verbose=1
)

MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
model.save(MODEL_OUT)

with CLASS_NAMES_OUT.open("w", encoding="utf-8") as f:
    for name in class_names:
        f.write(name + "\n")

print(f"Model saved to {MODEL_OUT}")
print(f"Classes: {class_names}")
print(f"Final train accuracy: {history.history['accuracy'][-1]:.4f}")
print(f"Final val accuracy: {history.history['val_accuracy'][-1]:.4f}")
