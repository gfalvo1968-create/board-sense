from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import csv
import shutil
import subprocess
import sys

from model.classifier import predict_board_grade

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
DB_DIR = BASE_DIR / "db"
MODEL_DIR = BASE_DIR / "model"
TRAIN_SCRIPT = BASE_DIR / "train_model.py"

LABELS_CSV = DB_DIR / "labels.csv"
SCANS_CSV = DB_DIR / "scans.csv"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter()


class SaveLabelRequest(BaseModel):
    filename: str
    label: str


class ManualGradeRequest(BaseModel):
    gold_fingers: bool
    dense_chips: bool
    industrial_connectors: bool
    power_board: bool
    heavy: bool


def ensure_csv_headers():
    if not LABELS_CSV.exists():
        with LABELS_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["filename", "label"])

    if not SCANS_CSV.exists():
        with SCANS_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["filename", "ai_grade", "confidence", "action", "timestamp"])


def append_scan(filename: str, ai_grade: str, confidence, action: str):
    ensure_csv_headers()
    with SCANS_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            filename,
            ai_grade,
            confidence,
            action,
            datetime.utcnow().isoformat()
        ])


def append_label(filename: str, label: str):
    ensure_csv_headers()
    with LABELS_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([filename, label.lower()])

def estimate_value(grade: str):
    values = {
        "HIGH": 15.0,
        "MEDIUM": 7.0,
        "LOW": 2.0,
        "JUNK": 0.5,
        "PENDING REVIEW": 0.0
    }
    return values.get(grade, 0.0)



@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    ensure_csv_headers()

    suffix = Path(file.filename).suffix.lower()
    if suffix not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp}_{Path(file.filename).name}"
    save_path = IMAGES_DIR / safe_name

    with save_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        ai_grade, confidence, action = predict_board_grade(str(save_path))
    except Exception as e:
        ai_grade = "PENDING REVIEW"
        confidence = 0.0
        action = f"Prediction unavailable: {e}"

    append_scan(safe_name, ai_grade, confidence, action)

    return {
    "filename": safe_name,
    "image_url": f"/data/images/{safe_name}",
    "ai_grade": ai_grade,
    "confidence": confidence,
    "action": action,
    "value_estimate": estimate_value(ai_grade)
}


@router.post("/save-label")
def save_label(payload: SaveLabelRequest):
    ensure_csv_headers()

    filename = payload.filename.strip()
    label = payload.label.strip().lower()

    if not filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    if label not in {"high", "medium", "low", "junk"}:
        raise HTTPException(status_code=400, detail="Invalid label")

def append_label(filename: str, label: str):
    ensure_csv_headers()
    with LABELS_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([filename, label.lower()])


    def estimate_value(grade: str):
        values = {
            "HIGH": 15.0,
            "MEDIUM": 7.0,
            "LOW": 2.0,
            "JUNK": 0.5,
            "PENDING REVIEW": 0.0
    }
        return values.get(grade, 0.0)


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    ensure_csv_headers()

    suffix = Path(file.filename).suffix.lower()
    if suffix not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp}_{Path(file.filename).name}"
    save_path = IMAGES_DIR / safe_name

    with save_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        ai_grade, confidence, action = predict_board_grade(str(save_path))
    except Exception as e:
        ai_grade = "PENDING REVIEW"
        confidence = 0.0
        action = f"Prediction unavailable: {e}"

append_scan(safe_name, ai_grade, confidence, action)

return {
    "filename": safe_name,
    "image_url": f"/data/images/{safe_name}",
    "ai_grade": ai_grade,
    "confidence": confidence,
    "action": action,
    "value_estimate": estimate_value(ai_grade)
}


@router.post("/manual-grade")
def manual_grade(payload: ManualGradeRequest):
    score = 0
    reasons = []

    if payload.gold_fingers:
        score += 3
        reasons.append("gold fingers")

    if payload.dense_chips:
        score += 2
        reasons.append("dense chips")

    if payload.industrial_connectors:
        score += 2
        reasons.append("industrial connectors")

    if payload.power_board:
        score -= 2
        reasons.append("power board")

    if payload.heavy:
        score -= 1
        reasons.append("heavy components")

    if score >= 4:
        grade = "HIGH"
    elif score >= 2:
        grade = "MEDIUM"
    elif score >= 0:
        grade = "LOW"
    else:
        grade = "JUNK"

    return {
        "grade": grade,
        "score": score,
        "reason": ", ".join(reasons) if reasons else "no signals selected"
    }


@router.get("/history")
def history():
    ensure_csv_headers()

    items = []
    with LABELS_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append({
                "filename": row.get("filename", ""),
                "label": row.get("label", "")
            })

    return items


@router.get("/training-status")
def training_status():
    ensure_csv_headers()

    counts = {
        "high": 0,
        "medium": 0,
        "low": 0,
        "junk": 0
    }

    with LABELS_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = (row.get("label") or "").strip().lower()
            if label in counts:
                counts[label] += 1

    total = sum(counts.values())

    return {
        "high": counts["high"],
        "medium": counts["medium"],
        "low": counts["low"],
        "junk": counts["junk"],
        "total": total,
        "ready": total >= 8
    }


@router.post("/train-model")
def train_model():
    if not TRAIN_SCRIPT.exists():
        raise HTTPException(status_code=500, detail="train_model.py not found")

    result = subprocess.run(
        [sys.executable, str(TRAIN_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(BASE_DIR)
    )

    output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=output.strip() or "Training failed"
        )

    return {
        "message": "Training completed successfully",
        "output": output.strip() or "Training completed"
    }

@router.get("/health")
def health():
    return {"status": "running"}

