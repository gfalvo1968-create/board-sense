from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
LABELS_FILE = BASE_DIR / "db" / "labels.csv"
MODEL_DIR = BASE_DIR / "model"
CLASS_NAMES_OUT = MODEL_DIR / "class_names.txt"
MODEL_OUT = MODEL_DIR / "boardsense_model.txt"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

if not LABELS_FILE.exists():
    raise ValueError("labels.csv not found")

df = pd.read_csv(LABELS_FILE)
df["label"] = df["label"].astype(str).str.strip().str.lower()
df = df[df["label"].isin(["high", "medium", "low", "junk"])]

if len(df) < 8:
    raise ValueError("Need at least 8 labeled images to train")

class_names = sorted(df["label"].unique().tolist())

if len(class_names) < 2:
    raise ValueError("Need at least 2 different label classes to train")

with CLASS_NAMES_OUT.open("w", encoding="utf-8") as f:
    for name in class_names:
        f.write(name + "\n")

with MODEL_OUT.open("w", encoding="utf-8") as f:
    f.write("BoardSense training placeholder\n")
    f.write(f"Total labels: {len(df)}\n")
    f.write(f"Classes: {', '.join(class_names)}\n")

print("Training completed successfully")
print(f"Total labels: {len(df)}")
print(f"Classes: {', '.join(class_names)}")
print(f"Model marker saved to {MODEL_OUT}")
