import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

def optimize_model():
    """
    Farklı makine öğrenmesi algoritmalarını dener, en iyisini seçer
    ve GridSearchCV ile hiperparametre optimizasyonu yapar.
    """
    print("--- 1. VERİ SETİ HAZIRLIĞI ---")
    # Kodun hatasız çalışması için simüle edilmiş 200 satırlık temiz tarım verisi
    np.random.seed(42)
    n_samples = 200
    df = pd.DataFrame({
        'soil_moisture': np.random.uniform(10, 90, n_samples),
        'temperature': np.random.uniform(10, 40, n_samples),
        'humidity': np.random.uniform(30, 90, n_samples),
        'ph_level': np.random.uniform(5.5, 8.5, n_samples),
    })
    
    # Sensör verilerine göre hedefleri (Aksiyonları) belirliyoruz (Paydaş Raporuna İstinaden)
    conditions = [
        (df['soil_moisture'] < 35),                                # Nem %35 altındaysa Sulama
        (df['ph_level'] < 6.0) | (df['ph_level'] > 7.5)            # pH bozuksa Gübre/İlaç
    ]
    choices = ['Sulama Yap', 'Gubre/Ilac Uygula']
    df['Aksiyon'] = np.select(conditions, choices, default='Durum Normal')

    # Bağımsız değişkenler (X) ve Hedef değişken (y)
    X = df.drop('Aksiyon', axis=1)
    y = df['Aksiyon']

    # Veriyi Eğitim (%80) ve Test (%20) olarak bölüyoruz
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("--- 2. FARKLI ALGORİTMALARIN DENENMESİ ---")
    models = {
        "Logistic Regression": LogisticRegression(max_iter=500),
        "Support Vector Machine (SVM)": SVC(),
        "Random Forest Classifier": RandomForestClassifier(random_state=42)
    }

    best_model_name = ""
    best_accuracy = 0

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"{name} Başarı Oranı: %{acc * 100:.2f}")
        
        if acc > best_accuracy:
            best_accuracy = acc
            best_model_name = name

    print(f"\nEn Başarılı Algoritma: {best_model_name} (Bu model optimize edilecek)")

    print("\n--- 3. SON OPTİMİZASYON (GridSearchCV) ---")
    # Random Forest için hiperparametre haritası (Daha fazla ağaç, farklı derinlikler)
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5]
    }

    rf_model = RandomForestClassifier(random_state=42)
    
    # GridSearchCV, tüm kombinasyonları deneyerek en iyi ayarı bulur
    grid_search = GridSearchCV(estimator=rf_model, param_grid=param_grid, cv=3, n_jobs=-1, verbose=0)
    grid_search.fit(X_train, y_train)

    best_rf = grid_search.best_estimator_
    final_pred = best_rf.predict(X_test)
    final_acc = accuracy_score(y_test, final_pred)

    print(f"Optimizasyon Sonrası Bulunan En İyi Parametreler: {grid_search.best_params_}")
    print(f"Final Model Başarı Oranı: %{final_acc * 100:.2f}")
    print("\nDetaylı Sınıflandırma Raporu:")
    print(classification_report(y_test, final_pred))

if __name__ == "__main__":
    optimize_model()
