def signal_light(level):
    if level == "GREEN":
        return "🟢"
    if level == "ORANGE":
        return "🟠"
    return "🔴"


def analyze_features(name: str):
    name = name.lower()

    features = {
        "gold_fingers": 0,
        "dense_chips": 0,
        "connectors": 0,
    }

    # 🔍 Simple keyword detection (we’ll upgrade later)
    if "finger" in name or "gold" in name:
        features["gold_fingers"] += 3

    if "chip" in name or "ic" in name:
        features["dense_chips"] += 2

    if "connector" in name or "port" in name:
        features["connectors"] += 1

    return {
        "gold_fingers": signal_level(features["gold_fingers"]),
        "dense_chips": signal_level(features["dense_chips"]),
        "connectors": signal_level(features["connectors"]),
    }
