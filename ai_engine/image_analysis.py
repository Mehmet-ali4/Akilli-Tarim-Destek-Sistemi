from datetime import date, timedelta
from io import BytesIO

import numpy as np
from PIL import Image

CROP_CYCLE_DAYS = {
    "misir": 120,
    "mısır": 120,
    "bugday": 150,
    "buğday": 150,
    "domates": 90,
    "patates": 100,
    "aycicegi": 110,
    "ayçiçeği": 110,
    "elma": 180,
    "uzum": 140,
    "üzüm": 140,
}


def normalize_crop_name(crop_name):
    if not crop_name:
        return None
    return crop_name.strip().lower()


def get_crop_cycle_days(crop_name):
    normalized = normalize_crop_name(crop_name)
    if not normalized:
        return 100
    return CROP_CYCLE_DAYS.get(normalized, 100)


def analyze_plant_image(image_bytes, crop_name=None):
    """Tarla fotografini analiz ederek bitki sagligi ve hasat tahmini uretir."""
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    image = image.resize((256, 256))
    pixels = np.array(image)

    red = pixels[:, :, 0].astype(float)
    green = pixels[:, :, 1].astype(float)
    blue = pixels[:, :, 2].astype(float)
    total_pixels = pixels.shape[0] * pixels.shape[1]

    green_mask = (green > red + 12) & (green > blue + 12) & (green > 55)
    yellow_mask = (red > 85) & (green > 85) & (blue < 115)
    brown_mask = (red > 65) & (green < 75) & (blue < 65)

    green_ratio = float(green_mask.sum() / total_pixels)
    yellow_ratio = float(yellow_mask.sum() / total_pixels)
    brown_ratio = float(brown_mask.sum() / total_pixels)
    stress_ratio = yellow_ratio + brown_ratio

    health_score = round(max(0, min(100, green_ratio * 110 - stress_ratio * 90 + 35)), 1)
    disease_risk = round(min(1.0, stress_ratio * 2.2 + brown_ratio * 2.8), 4)

    if green_ratio > 0.42 and stress_ratio < 0.18:
        leaf_color = "yesil"
        growth_stage = "buyume"
        maturity_ratio = 0.35
        stage_label = "Buyume donemi"
    elif yellow_ratio > 0.22:
        leaf_color = "sari"
        growth_stage = "olgunlasma"
        maturity_ratio = 0.78
        stage_label = "Olgunlasma donemi"
    elif brown_ratio > 0.12:
        leaf_color = "kahverengi"
        growth_stage = "stresli"
        maturity_ratio = 0.55
        stage_label = "Stres / olasi hastalik belirtisi"
    else:
        leaf_color = "karma"
        growth_stage = "orta"
        maturity_ratio = 0.58
        stage_label = "Orta gelisim donemi"

    cycle_days = get_crop_cycle_days(crop_name)
    remaining_days = max(7, int(cycle_days * (1 - maturity_ratio)))

    if health_score < 50:
        remaining_days = int(remaining_days * 1.15)
    elif health_score > 80:
        remaining_days = int(remaining_days * 0.95)

    harvest_date = date.today() + timedelta(days=remaining_days)

    if health_score >= 75:
        health_status = "Iyi"
    elif health_score >= 50:
        health_status = "Orta"
    else:
        health_status = "Dusuk"

    notes = []
    if disease_risk >= 0.45:
        notes.append("Yapraklarda stres veya hastalik belirtisi olabilir; uzman kontrolu onerilir.")
    if yellow_ratio > 0.25:
        notes.append("Sararma orani yuksek; besin veya su stresi olabilir.")
    if health_score >= 75:
        notes.append("Bitki genel olarak saglikli gorunuyor.")
    if not notes:
        notes.append("Duzenli izleme onerilir.")

    return {
        "health_score": health_score,
        "health_status": health_status,
        "disease_risk": disease_risk,
        "leaf_color": leaf_color,
        "growth_stage": growth_stage,
        "growth_stage_label": stage_label,
        "color_analysis": {
            "green_ratio": round(green_ratio, 4),
            "yellow_ratio": round(yellow_ratio, 4),
            "brown_ratio": round(brown_ratio, 4),
        },
        "crop_name": crop_name,
        "crop_cycle_days": cycle_days,
        "estimated_days_to_harvest": remaining_days,
        "estimated_harvest_date": harvest_date.isoformat(),
        "notes": notes,
    }
