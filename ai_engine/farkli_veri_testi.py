import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

def feature_engineering_uygula(df):
    """İyileştirme Tekniği: Var olan verilerden 'Kuraklık İndeksi' üretilmesi"""
    # Sıcaklık arttıkça ve nem düştükçe kuraklık indeksi artar
    df['kuraklik_indeksi'] = df['temperature'] / (df['soil_moisture'] + 1)
    return df

print("--- 1. ANA VERİ SETİ İLE EĞİTİM (Normal İklim) ---")
np.random.seed(42)
n_samples = 200

# Normal iklim şartlarını simüle eden eğitim verisi
train_df = pd.DataFrame({
    'soil_moisture': np.random.uniform(20, 80, n_samples),
    'temperature': np.random.uniform(15, 35, n_samples),
    'humidity': np.random.uniform(40, 80, n_samples),
    'ph_level': np.random.uniform(6.0, 7.5, n_samples),
})

# Hedef Değişken (Aksiyonlar)
conditions = [
    (train_df['soil_moisture'] < 35),
    (train_df['ph_level'] < 6.2) | (train_df['ph_level'] > 7.3)
]
choices = ['Sulama Yap', 'Gubre/Ilac Uygula']
train_df['Aksiyon'] = np.select(conditions, choices, default='Durum Normal')

# İyileştirme Tekniğini Uygulama
train_df = feature_engineering_uygula(train_df)

X_train = train_df.drop('Aksiyon', axis=1)
y_train = train_df['Aksiyon']

# Modelin Eğitilmesi
rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
rf_model.fit(X_train, y_train)
print("Model ana veri setiyle başarıyla eğitildi ve yeni özellikleri öğrendi.\n")

print("--- 2. FARKLI VERİ SETİ ÜZERİNDE TEST (Kurak İklim Simülasyonu) ---")
# Modelin daha önce HİÇ GÖRMEDİĞİ, sıcaklıkların yüksek, nemin düşük olduğu yepyeni bir veri seti
test_n_samples = 50
test_df = pd.DataFrame({
    'soil_moisture': np.random.uniform(5, 40, test_n_samples),   # Çok daha kuru bir toprak
    'temperature': np.random.uniform(28, 45, test_n_samples),    # Çok daha sıcak bir hava
    'humidity': np.random.uniform(10, 40, test_n_samples),       # Çok düşük ortam nemi
    'ph_level': np.random.uniform(5.5, 8.0, test_n_samples),
})

# Gerçekte olması gereken sonuçlar (Ground Truth)
test_conditions = [
    (test_df['soil_moisture'] < 35),
    (test_df['ph_level'] < 6.2) | (test_df['ph_level'] > 7.3)
]
test_df['Gercek_Aksiyon'] = np.select(test_conditions, choices, default='Durum Normal')

# Farklı veri setine de aynı iyileştirme tekniğini uyguluyoruz
test_df = feature_engineering_uygula(test_df)

X_test_yeni = test_df.drop('Gercek_Aksiyon', axis=1)
y_test_gercek = test_df['Gercek_Aksiyon']

# Modelin tahmini ve Analiz
y_pred_yeni = rf_model.predict(X_test_yeni)
acc_yeni = accuracy_score(y_test_gercek, y_pred_yeni)

print(f"Farklı (Kurak) Veri Setindeki Başarı Oranı: %{acc_yeni * 100:.2f}")
print("\nSonuç Analizi (Classification Report):")
print(classification_report(y_test_gercek, y_pred_yeni, zero_division=0))
