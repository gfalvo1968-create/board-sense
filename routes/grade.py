from fastapi import APIRouter
from model.classifier import predict_board_grade

router = APIRouter()

@router.post("/predict")
def predict():
    # TEMP: use a test image
    image_path = "data/images/IMG_0772.jpeg"

    result = predict_board_grade(image_path)

    return {"prediction": result}
