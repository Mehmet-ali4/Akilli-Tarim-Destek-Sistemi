import json
from pathlib import Path

import joblib
import numpy as np
import optuna
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.metrics import (
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

from veri_onisleme import preprocess_data

RANDOM_STATE = 42
N_TRIALS = 50
ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"


def build_dataset(n_samples=800):
    """Sentetik tarım verisi oluşturur ve aksiyon etiketlerini üretir."""
    rng = np.random.default_rng(RANDOM_STATE)
    data_dict = {
        "soil_moisture": rng.uniform(8, 95, n_samples),
        "temperature": rng.uniform(5, 42, n_samples),
        "humidity": rng.uniform(20, 95, n_samples),
        "ph_level": rng.uniform(5.0, 8.8, n_samples),
    }
    df = preprocess_data(data_dict)

    needs_irrigation = df["soil_moisture"] < 35
    needs_fertilizer = (df["ph_level"] < 6.0) | (df["ph_level"] > 7.5)
    conditions = [
        needs_irrigation & needs_fertilizer,
        needs_irrigation,
        needs_fertilizer,
    ]
    choices = ["Sulama + Gubre/Ilac Uygula", "Sulama Yap", "Gubre/Ilac Uygula"]
    df["Aksiyon"] = np.select(conditions, choices, default="Durum Normal")
    return df


def add_features(df):
    """Domain tabanli yeni ozellikler ekler."""
    features = df.copy()

    # --- Mevcut ozellikler ---
    features["temp_humidity_interaction"] = features["temperature"] * features["humidity"]
    features["moisture_temp_ratio"] = features["soil_moisture"] / (features["temperature"] + 1e-3)
    features["ph_deviation"] = (features["ph_level"] - 6.8).abs()
    features["low_moisture_flag"] = (features["soil_moisture"] < 35).astype(int)
    features["high_temp_flag"] = (features["temperature"] > 32).astype(int)

    # --- Yeni tarimsal ozellikler ---

    # VPD (Buharlaşma Basıncı Açığı, kPa)
    # Es(T) = 0.6108 * exp(17.27*T / (T+237.3)) — Doyma buhar basıncı
    # VPD = Es * (1 - RH/100) — Gerçek açık (bitki su stresinin en doğru göstergesi)
    es = 0.6108 * np.exp(17.27 * features["temperature"] / (features["temperature"] + 237.3))
    features["vpd"] = es * (1.0 - features["humidity"] / 100.0)

    # Isı İndeksi (°C) — Steadman basitleştirilmiş
    # Yüksek VPD + yüksek sıcaklık kombinasyonunu yakalar
    features["heat_index"] = (
        features["temperature"] + 0.33 * (features["humidity"] / 100.0 * es) - 4.0
    )

    # pH Kategorisi: 0=asidik(<6.0), 1=optimal(6.0-7.5), 2=bazik(>7.5)
    features["ph_category"] = np.select(
        [features["ph_level"] < 6.0, features["ph_level"] > 7.5],
        [0, 2],
        default=1
    )

    # Kuraklık Stresi Skoru [0,1] — nem açığı × sıcaklık baskısı
    moisture_deficit = np.clip((35.0 - features["soil_moisture"]) / 35.0, 0, 1)
    temp_pressure = np.clip((features["temperature"] - 20.0) / 22.0, 0, 1)
    features["drought_stress"] = moisture_deficit * temp_pressure

    return features


def tune_lightgbm(X_train, y_train):
    """Macro F1 odakli 5-fold Optuna optimizasyonu yapar."""
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    def objective(trial):
        model = LGBMClassifier(
            objective="multiclass",
            n_estimators=trial.suggest_int("n_estimators", 100, 700),
            learning_rate=trial.suggest_float("learning_rate", 1e-3, 0.2, log=True),
            num_leaves=trial.suggest_int("num_leaves", 16, 128),
            max_depth=trial.suggest_int("max_depth", 3, 12),
            min_child_samples=trial.suggest_int("min_child_samples", 10, 80),
            subsample=trial.suggest_float("subsample", 0.6, 1.0),
            colsample_bytree=trial.suggest_float("colsample_bytree", 0.6, 1.0),
            reg_lambda=trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
            verbosity=-1,
        )
        scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="f1_macro", n_jobs=-1)
        return float(np.mean(scores))

    study = optuna.create_study(direction="maximize", study_name="lgbm_macro_f1")
    study.optimize(objective, n_trials=N_TRIALS, show_progress_bar=False)
    return study.best_params, float(study.best_value)


def build_xgb_model(y_train):
    """XGBoost modelini API uyumlu kurar."""
    num_classes = len(np.unique(y_train))
    return XGBClassifier(
        objective="multi:softprob",
        eval_metric="mlogloss",
        num_class=num_classes,
        random_state=RANDOM_STATE,
        n_estimators=350,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=2.0,
        n_jobs=-1,
    )


def evaluate_model(model, X_test, y_test, class_names):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    return {
        "macro_f1": float(f1_score(y_test, y_pred, average="macro")),
        "macro_precision": float(precision_score(y_test, y_pred, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(y_test, y_pred, average="macro", zero_division=0)),
        "roc_auc_ovr": float(roc_auc_score(y_test, y_proba, multi_class="ovr", average="macro")),
        "classification_report": classification_report(
            y_test,
            y_pred,
            labels=list(range(len(class_names))),
            target_names=class_names,
            zero_division=0,
        ),
    }


def optimize_model():
    print("--- 1) Veri hazırlığı ve özellik mühendisliği ---")
    df = build_dataset()
    X = add_features(df.drop(columns=["Aksiyon"]))
    y = df["Aksiyon"]
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    class_names = label_encoder.classes_.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_encoded,
        test_size=0.2,
        stratify=y_encoded,
        random_state=RANDOM_STATE,
    )

    print("--- 2) LightGBM Optuna (50 trial, Stratified 5-Fold) ---")
    best_lgbm_params, best_lgbm_cv = tune_lightgbm(X_train, y_train)
    lgbm_model = LGBMClassifier(
        objective="multiclass",
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbosity=-1,
        **best_lgbm_params,
    )
    lgbm_model.fit(X_train, y_train)
    lgbm_metrics = evaluate_model(lgbm_model, X_test, y_test, class_names)

    print("--- 3) XGBoost alternatif model ---")
    xgb_model = build_xgb_model(y_train)
    xgb_model.fit(X_train, y_train)
    xgb_metrics = evaluate_model(xgb_model, X_test, y_test, class_names)

    print("--- 4) En iyi modeli seçme (ana metrik: Macro F1) ---")
    if xgb_metrics["macro_f1"] > lgbm_metrics["macro_f1"]:
        best_name = "XGBoost"
        best_model = xgb_model
        best_metrics = xgb_metrics
    else:
        best_name = "LightGBM"
        best_model = lgbm_model
        best_metrics = lgbm_metrics

    ARTIFACT_DIR.mkdir(exist_ok=True)
    joblib.dump(best_model, ARTIFACT_DIR / "best_model.joblib")
    joblib.dump(list(X.columns), ARTIFACT_DIR / "feature_columns.joblib")
    joblib.dump(label_encoder, ARTIFACT_DIR / "label_encoder.joblib")

    # Feature importance — normalize edilmiş önem skoru (toplam = 1.0)
    raw_importances = best_model.feature_importances_
    total = raw_importances.sum() or 1.0
    feature_importances = sorted(
        [
            {"feature": col, "importance": round(float(imp / total), 6)}
            for col, imp in zip(list(X.columns), raw_importances)
        ],
        key=lambda x: x["importance"],
        reverse=True,
    )

    report = {
        "main_metric": "macro_f1",
        "validation": "Stratified 5-Fold CV + hold-out test",
        "class_names": class_names,
        "lightgbm_best_cv_macro_f1": best_lgbm_cv,
        "lightgbm_best_params": best_lgbm_params,
        "lightgbm_test_metrics": lgbm_metrics,
        "xgboost_test_metrics": xgb_metrics,
        "selected_model": best_name,
        "selected_model_test_metrics": best_metrics,
        "feature_importances": feature_importances,
    }
    with open(ARTIFACT_DIR / "evaluation_report.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print(f"Seçilen model: {best_name}")
    print(f"Macro F1: {best_metrics['macro_f1']:.4f}")
    print("Rapor dosyası: ai_engine/artifacts/evaluation_report.json")
    print("Model dosyası: ai_engine/artifacts/best_model.joblib")


if __name__ == "__main__":
    optimize_model()
