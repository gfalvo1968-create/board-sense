from pathlib import Path

# -----------------------------
# SIGNAL LEVEL LOGIC
# -----------------------------
def signal_level(score: int):
    if score >= 3:
        return "GREEN"
    elif score == 2:
        return "ORANGE"
    return "RED"


def signal_light(level: str):
    if level == "GREEN":
        return "🟢"
    elif level == "ORANGE":
        return "🟠"
    return "🔴"


# -----------------------------
# FEATURE DETECTION (BRAIN)
# -----------------------------
def analyze_features(image_path: str):
    name = str(image_path).lower()

    # Basic detection (you will upgrade this later)
    features = {
        "gold_fingers": 1 if "gold" in name else 0,
        "dense_chips": 1 if "chip" in name else 0,
        "industrial_connectors": 1 if "port" in name or "connector" in name else 0,
        "power_board": 1 if "power" in name else 0,
        "heavy": 1 if "heavy" in name else 0,
    }

    # Convert to signal strength (0–3 scale later)
    signals = {
        key: signal_level(value)
        for key, value in features.items()
    }

    # Add emoji lights for UI
    lights = {
        key: signal_light(value)
        for key, value in signals.items()
    }

    # -----------------------------
    # JACKPOT LOGIC 💥
    # -----------------------------
    jackpot = all(value == "GREEN" for value in signals.values())

    # -----------------------------
    # SCORE SYSTEM
    # -----------------------------
    score = sum(features.values())

    if score >= 4:
        grade = "HIGH"
        action = "RECOVER"
    elif score == 3:
        grade = "MEDIUM"
        action = "PART OUT"
    elif score == 2:
        grade = "LOW"
        action = "SCRAP"
    else:
        grade = "JUNK"
        action = "DISCARD"

    # -----------------------------
    # FINAL RESPONSE
    # -----------------------------
    return {
        "features": features,
        "signals": signals,
        "lights": lights,
        "score": score,
        "grade": grade,
        "action": action,
        "jackpot": jackpot,
        "message": (
            "💥 JACKPOT — This is a board to recover. Launch Pay_Dirt."
            if jackpot else
            "Needs more signals"
        )
    }
