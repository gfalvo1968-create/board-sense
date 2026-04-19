from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from routes.grade import router as grade_router

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
DB_DIR = BASE_DIR / "db"
MODEL_DIR = BASE_DIR / "model"

IMAGES_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="BoardSense")

app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")
app.include_router(grade_router)


@app.get("/", response_class=HTMLResponse)
def home():
    index_path = BASE_DIR / "index.html"
    return index_path.read_text(encoding="utf-8")
