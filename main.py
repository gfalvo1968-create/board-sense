from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import shutil
import os
import csv
from datetime import datetime

app = FastAPI()

class BoardInput(BaseModel):
    gold_fingers: bool
    dense_chips: bool
    industrial_connectors: bool
    power_board: bool
    heavy: bool
class LabelInput(BaseModel):
    filename: str
    label: str
@app.get("/")
def home():
    return {"message": "BoardSense is running"}

@app.post("/grade")
def grade_board(data: BoardInput):
    score = 0
    if data.gold_fingers: score += 3
    if data.dense_chips: score += 2
    if data.industrial_connectors: score += 2
    if data.power_board: score -= 2
    if data.heavy: score += 1

    if score >= 5:
        grade, action = "HIGH", "Sell as high-grade / check resale"
    elif score >= 3:
        grade, action = "MEDIUM", "Batch sell or strip parts"
    elif score >= 1:
        grade, action = "LOW", "Scrap / low-grade buyer"
    else:
        grade, action = "JUNK", "Strip & move on"

    return {"score": score, "grade": grade, "action": action}

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    os.makedirs("data", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = file.filename.replace(" ", "_")
    filename = f"{timestamp}_{safe_name}"
    file_location = f"data/{filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "Image saved",
        "filename": filename
   @app.post("/label")
def save_label(data: LabelInput):
    os.makedirs("db", exist_ok=True)
    csv_file = "db/labels.csv"
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, "a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["filename", "label", "timestamp"])
        writer.writerow([
            data.filename,
            data.label,
            datetime.now().isoformat()
        ])

    return {"message": f"Label '{data.label}' saved for {data.filename}"}
    
    }
    

    
