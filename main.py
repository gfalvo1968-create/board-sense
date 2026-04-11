from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import os
import shutil
import csv

app = FastAPI()

# Make sure folders exist
os.makedirs("data", exist_ok=True)
os.makedirs("db", exist_ok=True)

def simple_ai_grade(filename):
    name = filename.lower()

    score = 0

    if "gold" in name:
        score += 3
    if "server" in name or "dense" in name:
        score += 2
    if "industrial" in name:
        score += 2
    if "power" in name:
        score -= 2

    if score >= 5:
        return "HIGH", "0.85"
    elif score >= 3:
        return "MEDIUM", "0.70"
    elif score >= 1:
        return "LOW", "0.60"
    else:
        return "JUNK", "0.40"

# -----------------------------
# Data models
# -----------------------------
class BoardInput(BaseModel):
    gold_fingers: bool
    dense_chips: bool
    industrial_connectors: bool
    power_board: bool
    heavy: bool


class LabelInput(BaseModel):
    filename: str
    label: str


# -----------------------------
# Serve uploaded images
# -----------------------------
app.mount("/data", StaticFiles(directory="data"), name="data")


# -----------------------------
# Home page
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as file:
        return file.read()


# -----------------------------
# Manual grading route
# -----------------------------
@app.post("/grade")
def grade_board(data: BoardInput):
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
        action = "Sell as high-grade board or check resale before scrapping"
    elif score >= 3:
        grade = "MEDIUM"
        action = "Batch sell or strip valuable parts"
    elif score >= 1:
        grade = "LOW"
        action = "Scrap or sell as low-grade board"
    else:
        grade = "JUNK"
        action = "Strip what you can and move on"

    return {
        "score": score,
        "grade": grade,
        "action": action
    }


# -----------------------------
# Upload image route
# -----------------------------
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = file.filename.replace(" ", "_")
    filename = f"{timestamp}_{safe_name}"
    file_location = os.path.join("data", filename)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ai_grade, confidence = simple_ai_grade(filename)
action = "Auto AI grading complete"

    return {
        "message": "Image saved",
        "filename": filename,
        "image_url": f"/data/{filename}",
        "ai_grade": ai_grade,
        "confidence": confidence,
        "action": action
    }


# -----------------------------
# Save label route
# -----------------------------
@app.post("/label")
def save_label(data: LabelInput):
    csv_file = os.path.join("db", "labels.csv")
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["filename", "label", "timestamp"])

        writer.writerow([
            data.filename,
            data.label,
            datetime.now().isoformat()
        ])

    return {
        "message": f"Saved label {data.label} for {data.filename}"
    }

    
