from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import shutil
import os
import csv
from collections import Counter

app = FastAPI()

# =========================
# Setup
# =========================
os.makedirs("data", exist_ok=True)
os.makedirs("db", exist_ok=True)
os.makedirs("model", exist_ok=True)

app.mount("/data", StaticFiles(directory="data"), name="data")


# =========================
# Optional AI import
# =========================
AI_AVAILABLE = True
AI_IMPORT_ERROR = ""

try:
    from model.classifier import predict_board_grade
except Exception as e:
    AI_AVAILABLE = False
    AI_IMPORT_ERROR = str(e)


# =========================
# Data models
# =========================
class LabelInput(BaseModel):
    filename: str
    label: str


class ManualGradeInput(BaseModel):
    gold_fingers: bool
    dense_chips: bool
    industrial_connectors: bool
    power_board: bool
    heavy: bool


# =========================
# Helpers
# =========================
def labels_csv_path():
    return os.path.join("db", "labels.csv")


def scans_csv_path():
    return os.path.join("db", "scans.csv")


def simple_manual_grade(data: ManualGradeInput):
    score = 0

    if data.gold_fingers:
        score += 3
    if data.dense_chips:
        score += 2
    if data.industrial_connectors:
        score += 2
    if data.power_board:
        score -= 2
    if data.heavy:
        score += 1

    if score >= 5:
        grade = "HIGH"
        action = "Sell as high-grade board or check resale first"
    elif score >= 3:
        grade = "MEDIUM"
        action = "Batch sell or strip valuable parts"
    elif score >= 1:
        grade = "LOW"
        action = "Scrap or sell as low-grade board"
    else:
        grade = "JUNK"
        action = "Strip what you can and move on"

    return score, grade, action


def append_scan_history(filename: str, ai_grade: str, confidence):
    path = scans_csv_path()
    file_exists = os.path.isfile(path)

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["filename", "ai_grade", "confidence", "timestamp"])
        writer.writerow([
            filename,
            ai_grade,
            confidence,
            datetime.now().isoformat()
        ])


def append_label(filename: str, label: str):
    path = labels_csv_path()
    file_exists = os.path.isfile(path)

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["filename", "label", "timestamp"])
        writer.writerow([
            filename,
            label,
            datetime.now().isoformat()
        ])


def read_recent_scans(limit=10):
    path = scans_csv_path()
    if not os.path.isfile(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    rows.reverse()
    return rows[:limit]


def read_label_counts():
    path = labels_csv_path()
    counts = Counter({"HIGH": 0, "MEDIUM": 0, "LOW": 0, "JUNK": 0})

    if not os.path.isfile(path):
        return counts

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = row.get("label", "").strip().upper()
            if label in counts:
                counts[label] += 1

    return counts


# =========================
# Routes
# =========================
@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = file.filename.replace(" ", "_")
    filename = f"{timestamp}_{safe_name}"
    file_location = os.path.join("data", filename)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # AI prediction
    try:
        if not AI_AVAILABLE:
            raise RuntimeError(f"classifier not ready: {AI_IMPORT_ERROR}")

        ai_grade, confidence = predict_board_grade(file_location)
        confidence = str(confidence)
        action = "AI image grading complete"

    except Exception as e:
        ai_grade = "PENDING REVIEW"
        confidence = "0.00"
        action = f"AI not ready: {str(e)}"

    append_scan_history(filename, ai_grade, confidence)

    return {
        "message": "Image saved",
        "filename": filename,
        "image_url": f"/data/{filename}",
        "ai_grade": ai_grade,
        "confidence": confidence,
        "action": action
    }


@app.post("/label")
def save_label(data: LabelInput):
    append_label(data.filename, data.label.upper())

    return {
        "message": f"Saved label {data.label.upper()} for {data.filename}"
    }


@app.post("/grade")
def grade_manual(data: ManualGradeInput):
    score, grade, action = simple_manual_grade(data)
    return {
        "score": score,
        "grade": grade,
        "action": action
    }


@app.get("/history")
def get_history():
    return {"history": read_recent_scans(10)}


@app.get("/training-status")
def training_status():
    counts = read_label_counts()
    total = sum(counts.values())

    return {
        "HIGH": counts["HIGH"],
        "MEDIUM": counts["MEDIUM"],
        "LOW": counts["LOW"],
        "JUNK": counts["JUNK"],
        "TOTAL": total,
        "READY": total >= 5
    }
