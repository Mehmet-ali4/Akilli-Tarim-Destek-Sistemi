from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, request

from image_analysis import analyze_plant_image
from veri_onisleme import preprocess_data

app = Flask(__name__)

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "best_model.joblib"
FEATURE_COLUMNS_PATH = ARTIFACT_DIR / "feature_columns.joblib"
LABEL_ENCODER_PATH = ARTIFACT_DIR / "label_encoder.joblib"
REQUIRED_FIELDS = ["soil_moisture", "temperature", "humidity", "ph_level"]

model = joblib.load(MODEL_PATH)
feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
label_encoder = joblib.load(LABEL_ENCODER_PATH) if LABEL_ENCODER_PATH.exists() else None


def add_features(df):
    """Egitim pipeline'i ile birebir ayni ozellikleri uretir."""
    features = df.copy()

    features["temp_humidity_interaction"] = features["temperature"] * features["humidity"]
    features["moisture_temp_ratio"] = features["soil_moisture"] / (features["temperature"] + 1e-3)
    features["ph_deviation"] = (features["ph_level"] - 6.8).abs()
    features["low_moisture_flag"] = (features["soil_moisture"] < 35).astype(int)
    features["high_temp_flag"] = (features["temperature"] > 32).astype(int)

    es = 0.6108 * np.exp(17.27 * features["temperature"] / (features["temperature"] + 237.3))
    features["vpd"] = es * (1.0 - features["humidity"] / 100.0)
    features["heat_index"] = features["temperature"] + 0.33 * (features["humidity"] / 100.0 * es) - 4.0
    features["ph_category"] = np.select(
        [features["ph_level"] < 6.0, features["ph_level"] > 7.5],
        [0, 2],
        default=1
    )
    moisture_deficit = np.clip((35.0 - features["soil_moisture"]) / 35.0, 0, 1)
    temp_pressure = np.clip((features["temperature"] - 20.0) / 22.0, 0, 1)
    features["drought_stress"] = moisture_deficit * temp_pressure

    return features


def validate_payload(payload):
    for key in REQUIRED_FIELDS:
        if key not in payload:
            raise ValueError(f"Eksik alan: {key}")


def make_response(status_code, error_name, message, data=None):
    payload = {
        "code": status_code,
        "error": error_name,
        "message": message,
    }
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


def to_actions(prediction_label):
    if prediction_label == "Sulama + Gubre/Ilac Uygula":
        return ["Sulama Yap", "Gubre/Ilac Uygula"]
    if prediction_label == "Sulama Yap":
        return ["Sulama Yap"]
    if prediction_label == "Gubre/Ilac Uygula":
        return ["Gubre/Ilac Uygula"]
    return []


@app.route("/health", methods=["GET"])
def health():
    return make_response(200, None, "AI servisi çalışıyor", {"status": "ok"})


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        if not data:
            return make_response(400, "Bad Request", "Eksik veya hatalı parametre")

        if isinstance(data, dict):
            validate_payload(data)
            records = [data]
        elif isinstance(data, list):
            for record in data:
                validate_payload(record)
            records = data
        else:
            return make_response(400, "Bad Request", "Eksik veya hatalı parametre")

        input_df = pd.DataFrame(records)
        clean_df = preprocess_data(input_df.to_dict(orient="list"))
        engineered_df = add_features(clean_df)
        model_input = engineered_df[feature_columns]

        predictions = model.predict(model_input).tolist()
        if label_encoder is not None and predictions and isinstance(predictions[0], (int, float)):
            predictions = label_encoder.inverse_transform([int(value) for value in predictions]).tolist()
        probabilities = model.predict_proba(model_input).max(axis=1).tolist()

        response = []
        for index, prediction in enumerate(predictions):
            response.append(
                {
                    "prediction": prediction,
                    "actions": to_actions(prediction),
                    "confidence": round(float(probabilities[index]), 4),
                }
            )

        if isinstance(data, dict):
            return make_response(200, "OK", "İstek başarılı", response[0])
        return make_response(200, "OK", "İstek başarılı", response)

    except ValueError:
        return make_response(400, "Bad Request", "Eksik veya hatalı parametre")
    except Exception as error:
        return make_response(
            500,
            "Internal Server Error",
            "Sunucu hatası, tekrar deneyin",
            {"details": str(error)},
        )


@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    try:
        if "image" not in request.files:
            return make_response(400, "Bad Request", "Eksik veya hatalı parametre")

        image_file = request.files["image"]
        if not image_file.filename:
            return make_response(400, "Bad Request", "Eksik veya hatalı parametre")

        crop_name = request.form.get("crop_name")
        analysis = analyze_plant_image(image_file.read(), crop_name)
        return make_response(200, "OK", "İstek başarılı", analysis)

    except Exception as error:
        return make_response(
            500,
            "Internal Server Error",
            "Sunucu hatası, tekrar deneyin",
            {"details": str(error)},
        )


if __name__ == "__main__":
    app.run(port=5000, debug=True)
