def preprocess_image(image_path: str):
    img = Image.open(image_path).convert("RGB")
    img = img.resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr


def predict_board_grade(image_path: str):
    model, class_names = load_model_and_classes()
    image_tensor = preprocess_image(image_path)

    preds = model.predict(image_tensor, verbose=0)[0]
    best_index = int(np.argmax(preds))
    confidence = round(float(preds[best_index]) * 100, 2)
    label = class_names[best_index].upper()

    if confidence >= 80:
        return label, confidence, f"Predicted as {label}"
    elif confidence >= 60:
        return label, confidence, f"Low confidence prediction: {label}"
    else:
        return "PENDING REVIEW", confidence, "Unseen or uncertain board, review manually"
