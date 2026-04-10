from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

app = FastAPI()

class BoardInput(BaseModel):
    gold_fingers: bool
    dense_chips: bool
    industrial_connectors: bool
    power_board: bool
    heavy: bool

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
    file_location = f"data/{file.filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "Image saved"}
