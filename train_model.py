import os
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split

IMG_SIZE = (128, 128)
BATCH_SIZE = 16
DATA_DIR = "data"
LABELS_FILE = "db/labels.csv"
MODEL_OUT = "model/boardsense_model.h5"

label_df = pd.read_csv(LABELS_FILE)

# keep only rows where image file actually exists
label_df["filepath"] = label_df["filename"].apply(lambda x: os.path.join(DATA_DIR, x))
label_df = label_df[label_df["filepath"].apply(os.path.exists)]

class_names = sorted(label_df["label"].unique().tolist())
class_to_index = {name: i for i, name in enumerate(class_names)}
label_df["label_index"] = label_df["label"].map(class_to_index)

train_df, val_df = train_test_split(
    label_df,
    test_size=0.2,
    random_state=42,
    stratify=label_df["label_index"]
)

def load_image(path, label):
    image = tf.io.read_file(path)
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, IMG_SIZE)
    image = image / 255.0
    return image, label

train_ds = tf.data.Dataset.from_tensor_slices(
    (train_df["filepath"].values, train_df["label_index"].values)
)
train_ds = train_ds.map(load_image).shuffle(200).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

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

model.fit(train_ds, validation_data=val_ds, epochs=8)

os.makedirs("model", exist_ok=True)
model.save(MODEL_OUT)

with open("model/class_names.txt", "w", encoding="utf-8") as f:
    for name in class_names:
        f.write(name + "\n")

print("Model saved to", MODEL_OUT)
print("Classes:", class_names)
