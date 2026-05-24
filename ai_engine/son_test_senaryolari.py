import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings('ignore') # Konsol kirliliğini önlemek için

def model_hazirla():
    """Önceki aşamalardaki optimize edilmiş modeli hızlıca eğitip hazırlar."""
    np.random.seed(42)
    df = pd.DataFrame({
        'soil_moisture': np.random.uniform(10, 90, 200),
        'temperature': np.random.uniform(15, 40, 200),
        'humidity': np.random.uniform(30, 80, 200),
        'ph_level': np.random.uniform(5.5, 8.0, 200),
    })
    
    conditions = [
        (df['soil_moisture'] < 35),
        (df['ph_level'] < 6.0) | (df['ph_level'] > 7.5)
    ]
    df['Aksiyon'] = np.select(conditions, ['Sulama Yap', 'Gubre/Ilac Uygula'], default='Durum Normal')
    
    X = df.drop('Aksiyon', axis=1)
    y = df['Aksiyon']
    
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X, y)
    return model

def senaryo_testi_ve_hata_kontrolu(model, senaryo_adi, sensor_verisi):
    """Farklı veri senaryolarını test eder ve veri hatalarını anında düzeltir."""
    print(f"\n[{senaryo_adi}]")
    print(f"Gelen Ham Veri:\n{sensor_verisi}")
    
    try:
        # HATA DÜZELTME ADIMI: Veride boş (NaN) değer varsa sistem çökmesin diye güvenli değer ataması yapıyoruz
        if sensor_verisi.isnull().values.any():
            print("--> SİSTEM UYARISI: Sensörden eksik veri (NaN) geldi! Hata düzeltiliyor (Güvenli Medyan Ataması)...")
            # Eksik yerleri mantıklı varsayılanlarla doldur (Hata Düzeltme)
            sensor_verisi = sensor_verisi.fillna({'soil_moisture': 50, 'temperature': 25, 'humidity': 50, 'ph_level': 7.0})
        
        # Mantıksal Sınır Kontrolü (Örn: -500 derece olamaz)
        if (sensor_verisi['temperature'] > 70).any() or (sensor_verisi['temperature'] < -50).any():
            print("--> SİSTEM UYARISI: İmkansız sıcaklık değeri tespit edildi! Sensör kalibrasyon hatası. Değerler sınırlandırılıyor...")
            sensor_verisi['temperature'] = np.clip(sensor_verisi['temperature'], -50, 70)
            
        tahmin = model.predict(sensor_verisi)
        print(f"--> YAPAY ZEKA KARARI: {tahmin[0]}")
        
    except Exception as e:
        print(f"KRİTİK HATA ENGELLENDİ: Yapay Zeka motoru çökmekten kurtarıldı. Hata detayı: {e}")

if __name__ == "__main__":
    aktif_model = model_hazirla()
    print("Sistem Stres Testleri Başlatılıyor...")

    # SENARYO 1: İdeal Şartlar (Beklenen: Durum Normal)
    senaryo1 = pd.DataFrame({'soil_moisture': [60], 'temperature': [24], 'humidity': [55], 'ph_level': [6.5]})
    senaryo_testi_ve_hata_kontrolu(aktif_model, "Senaryo 1: Bahar Ayı İdeal Şartlar", senaryo1)

    # SENARYO 2: Aşırı Kuraklık (Beklenen: Sulama Yap)
    senaryo2 = pd.DataFrame({'soil_moisture': [15], 'temperature': [42], 'humidity': [20], 'ph_level': [6.8]})
    senaryo_testi_ve_hata_kontrolu(aktif_model, "Senaryo 2: Ağustos Ayı Aşırı Kuraklık", senaryo2)

    # SENARYO 3: Sensör Arızası / Kopukluk (Beklenen: Hatayı yakalayıp çökmeden karar vermesi)
    senaryo3 = pd.DataFrame({'soil_moisture': [np.nan], 'temperature': [22], 'humidity': [np.nan], 'ph_level': [9.5]}) # Toprak nemi koptu, pH çok asidik
    senaryo_testi_ve_hata_kontrolu(aktif_model, "Senaryo 3: IoT Sensör Bağlantı Kopukluğu ve Uç Değer", senaryo3)
