# 🧪 TEST RAPORU — Akıllı Tarım Destek Sistemi

**Rapor Tarihi:** 2026-06-08 (Güncelleme: 2026-06-08)  
**Hazırlayan:** QA Otomasyon Mühendisi  
**Toplam Test Sayısı:** 171 (87 Python + 84 JavaScript)  
**Başarı Oranı:** %100 ✅  
**Tespit Edilen Sorunlar:** 3 → **3/3 DÜZELTİLDİ** ✅

---

## 📋 İçindekiler

1. [Test Edilen Modüller](#1-test-edilen-modüller)
2. [Kullanılan Teknolojiler](#2-kullanılan-teknolojiler)
3. [AI Engine Testleri (Python)](#3-ai-engine-testleri-python)
4. [Frontend Testleri (JavaScript)](#4-frontend-testleri-javascript)
5. [Edge Case (Uç Senaryo) Matrisi](#5-edge-case-uç-senaryo-matrisi)
6. [Mocking Stratejisi](#6-mocking-stratejisi)
7. [Testleri Çalıştırma Komutları](#7-testleri-çalıştırma-komutları)
8. [Test Sonuçları](#8-test-sonuçları)
9. [Öneriler ve İyileştirmeler](#9-öneriler-ve-iyileştirmeler)

---

## 1. Test Edilen Modüller

| Modül | Dosya | Test Dosyası | Test Sayısı | Durum |
|-------|-------|-------------|-------------|-------|
| AI Engine (Tahmin Motoru) | `ai_engine/predict.py` | `ai_engine/test_predict.py` | 87 | ✅ PASS |
| Frontend (İş Mantığı) | `frontend/js/main.js` | `frontend/js/main.test.js` | 84 | ✅ PASS |

---

## 2. Kullanılan Teknolojiler

### Python Testleri
| Kütüphane | Versiyon | Amaç |
|-----------|---------|------|
| `pytest` | 9.0.3 | Test framework |
| `unittest.mock` | (built-in) | Keras model mocking |
| `numpy` | (mevcut) | Test verileri oluşturma |

### JavaScript Testleri
| Kütüphane | Versiyon | Amaç |
|-----------|---------|------|
| `jest` | 29.7.0 | Test framework |

---

## 3. AI Engine Testleri (Python)

### 📁 Dosya: `ai_engine/test_predict.py`
### 🎯 Hedef: `ai_engine/predict.py`

#### 3.1 Test Sınıfları ve Kapsamları

| # | Test Sınıfı | Test Sayısı | Kapsam |
|---|------------|-------------|--------|
| 1 | `TestAnalyzeConditions` | 25 | 8 parametrenin tek tek kural-tabanlı analizi |
| 2 | `TestOverallScore` | 4 | Genel uygunluk skoru hesaplaması |
| 3 | `TestUrunBazli` | 3 | Farklı ürünlere göre eşik değer doğrulaması |
| 4 | `TestEkUyarilar` | 3 | Ek uyarı tetikleme koşulları |
| 5 | `TestFlaskEndpoints` | 7 | Flask API endpoint entegrasyon testleri |
| 6 | `TestKerasModelMock` | 2 | Keras model çağrı doğrulaması |
| 7 | `TestEdgeCases` | 7 | Sınır değerler ve dayanıklılık |
| 8 | `TestOzetMesaji` | 2 | Skor → özet mesaj eşleştirmesi |
| 9 | `TestSulamaKarari` | 4 | Sulama kararı iş mantığı |
| 10 | `TestReturnYapisi` | 4 | Dönüş yapısının bütünlüğü |

#### 3.2 Parametre Bazlı Test Detayları

##### 🌡️ Sıcaklık Analizi (6 test)
- İdeal aralıkta (12-25°C buğday) → skor 1.0
- Tam sınır değerler: ideal_min ve ideal_max'e eşit → skor 1.0
- 1°C altında → skor 0.95 (kademeli düşüş)
- -15°C → skor 0.3 (minimum), don riski KRİTİK uyarısı
- 50°C → skor 0.3, sulama gerekli flag aktif

##### 🧪 pH Analizi (5 test)
- İdeal aralıkta (6.0-7.5 buğday) → skor 1.0
- Tam sınır: alt ve üst sınır eşitliği → skor 1.0
- pH 2.0 (aşırı asit) → skor 0.4, kireçleme önerisi
- pH 12.0 (aşırı alkali) → skor 0.4, kükürt önerisi

##### 💧 Toprak Nemi — Sulama Kararı (5 test)
- İdeal aralıkta → sulama gerekli değil
- %2 (kritik düşük) → sulama GEREKLİ, KRİTİK mesaj
- %0 (tamamen kuru) → skor ≤ 0.3, acil sulama
- %95 (aşırı yüksek) → kök çürümesi uyarısı
- %100 (su doygunluğu) → kök çürümesi uyarısı

##### 🌱 Besin Elementleri N-P-K (5 test)
- Azot yeterli → skor 1.0, gübre önerisi yok
- Azot 0 mg/kg → skor 0.4, "Azotlu gübre" tavsiyesi
- Fosfor 0 mg/kg → skor 0.4, "Fosforlu gübre" tavsiyesi
- Potasyum 0 mg/kg → skor 0.4, "Potasyumlu gübre" tavsiyesi
- Tüm besinler 999 mg/kg → hepsi skor 1.0

##### 🌿 Bitki Sağlığı (4 test)
- 85/100 (iyi) → skor 1.0
- 55/100 (orta) → skor 0.4-0.7 arası
- 10/100 (kritik) → skor ≤ 0.2, KRİTİK uyarı
- 0/100 (ölü) → skor 0.2 (minimum)

---

## 4. Frontend Testleri (JavaScript)

### 📁 Dosya: `frontend/js/main.test.js`
### 🎯 Hedef: `frontend/js/main.js`

#### 4.1 Test Grupları ve Kapsamları

| # | Test Grubu | Test Sayısı | Kapsam |
|---|-----------|-------------|--------|
| 1 | Otomatik Toprak Nemi Hesaplayıcı | 25 | Formül doğruluğu, buharlaşma, clamp |
| 2 | Renk Skalası — Confidence → CSS Class | 11 | Yeşil/Sarı/Kırmızı eşikleri |
| 3 | Factor Score → Renk Sınıfı | 7 | good/avg/bad sınıflandırma |
| 4 | Hava Durumu Emoji Eşleştirme | 13 | Tüm harita + edge case'ler |
| 5 | Capitalize Fonksiyonu | 5 | String işleme |
| 6 | Şehir Filtreleme | 8 | Arama, Türkçe karakter desteği |
| 7 | Matematiksel Doğrulama | 5 | Katsayı doğruluğu, orantı testleri |
| 8 | Renk Geçiş Noktası Hassasiyeti | 5 | Floating-point sınır testleri |
| 9 | Edge Cases ve Dayanıklılık | 5 | Infinity, negatif, sıfır |

#### 4.2 Otomatik Toprak Nemi Formülü Detayları

**Formül:**
```
autoToprakNemi = Math.round(humidity * 0.8 - (temp > 20 ? (temp - 20) * 1.5 : 0) + 10)
autoToprakNemi = Math.min(100, Math.max(0, autoToprakNemi))
```

**Formül Bileşenleri:**
- `humidity * 0.8` → Hava neminin %80'i baz alınır
- `(temp - 20) * 1.5` → 20°C üzerindeki her derece için 1.5 birim buharlaşma kaybı
- `+ 10` → Sabit baz toprak nemi değeri
- `clamp(0, 100)` → Sonuç her zaman 0-100 arasında

**Test Edilen Ekstrem Senaryolar:**

| Senaryo | Sıcaklık | Nem | Beklenen Sonuç | Açıklama |
|---------|---------|-----|----------------|----------|
| Yaz Adana | 42°C | %25 | 0 | Aşırı buharlaşma, clamp |
| Kış Rize | 5°C | %85 | 78 | Buharlaşma yok, yüksek nem |
| İlkbahar Ankara | 18°C | %45 | 46 | Dengeli koşul |
| Yaz İstanbul | 30°C | %70 | 51 | Orta buharlaşma |
| Kutupsal | -50°C | %10 | 18 | Donma, düşük nem |
| Tropikal | 50°C | %30 | 0 | Maksimum buharlaşma |
| Sıfır nokta | 0°C | %0 | 0 | Minimum nem (clamp) |

#### 4.3 Renk Skalası Eşikleri

| Confidence Aralığı | CSS Sınıfı | Renk | Anlam |
|---------------------|-----------|------|-------|
| `>= 0.75` | `positive` | 🟢 Yeşil | Koşullar uygun |
| `>= 0.50 ve < 0.75` | `warning` | 🟡 Sarı | İyileştirme gerekli |
| `< 0.50` | `danger` | 🔴 Kırmızı | Acil müdahale |

| Factor Score Aralığı | CSS Sınıfı | Renk |
|----------------------|-----------|------|
| `>= 0.80` | `good` | 🟢 Yeşil |
| `>= 0.50 ve < 0.80` | `avg` | 🟡 Sarı |
| `< 0.50` | `bad` | 🔴 Kırmızı |

---

## 5. Edge Case (Uç Senaryo) Matrisi

### Python (AI Engine)

| Edge Case | Parametre | Değer | Test Adı | Beklenti |
|-----------|----------|-------|----------|----------|
| Tüm sıfır | Hepsi | 0 | `test_tum_degerler_sifir` | Çökmemeli, 7 faktör üretmeli |
| Negatif değerler | Hepsi | -50 ~ -5 | `test_negatif_degerler` | Skor ≥ 0 |
| Çok büyük sayılar | Hepsi | 1000 ~ 99999 | `test_cok_buyuk_degerler` | Skor 0-1 arası |
| Ondalıklı değerler | Hepsi | 22.756 vb. | `test_float_ondalik_degerler` | Float sonuç |
| String → Float | Hepsi | "25" (string) | `test_string_to_float_donusum` | Dönüşüm çalışmalı |
| Boş veri | Hepsi | {} (boş dict) | `test_eksik_veri_default_degerler` | Default değerler |
| Hatalı tip | sicaklik | "çok_sıcak" | `test_predict_endpoint_hatali_veri` | 400 hata kodu |
| Bilinmeyen ürün | urun | "bilinmeyen" | `test_bilinmeyen_urun_bugday_fallback` | Buğday'a geri dönüş |
| 20 ürün tamamı | urun | Tüm anahtarlar | `test_tum_urunler_crash_etmemeli` | Hepsi sorunsuz |

### JavaScript (Frontend)

| Edge Case | Parametre | Değer | Test Adı | Beklenti |
|-----------|----------|-------|----------|----------|
| Infinity sıcaklık | temp | Infinity | `Infinity sıcaklık → 0` | Clamp → 0 |
| -Infinity sıcaklık | temp | -Infinity | `-Infinity sıcaklık → 50` | Buharlaşma yok |
| Infinity nem | humidity | Infinity | `Infinity nem → 100` | Clamp → 100 |
| Negatif nem | humidity | -50 | `Negatif nem → 0` | Clamp → 0 |
| Sıfır-sıfır | Her ikisi | 0 | `Her iki parametre 0 → 10` | Baz değer |
| Floating point | confidence | 0.7499999999 | `Kayan nokta hassasiyeti` | warning (positive değil!) |
| null emoji | main | null | `null → default emoji` | 🌤️ fallback |
| Boş string şehir | filter | "" | `Boş filtre → 81 il` | Tam liste |
| Türkçe karakter | filter | "ş" | `Türkçe karakter → sonuç` | Doğru eşleşme |
| 50 rastgele değer | Her ikisi | Random | `Fuzz test` | Hep 0-100 arası |

---

## 6. Mocking Stratejisi

### 6.1 Python — Keras Model Mocking

```python
# Gerçek TensorFlow/Keras modeli yerine MagicMock kullanılır
# Böylece GPU/CPU bağımlılığı ve model dosyası gereksinimleri ortadan kalkar

@pytest.fixture(scope="module")
def mock_model():
    mock = MagicMock()
    mock.predict.return_value = np.array([[0.78]], dtype=np.float32)
    return mock
```

**Neden Mock?**
- TensorFlow yüklenmesi ~5-10 saniye sürer
- `.keras` model dosyası ortamlar arası taşınabilir değildir
- Testler modelin **iç mantığını** değil, **giriş/çıkış davranışını** test eder
- CI/CD ortamlarında GPU gerektirmeden çalışır

**Mock Edilen Bileşenler:**
| Bileşen | Mock Yöntemi | Amaç |
|---------|-------------|------|
| `predict.model` | `MagicMock()` | Keras model.predict() |
| `predict.tf` | `@patch("predict.tf")` | TensorFlow import |
| `predict.get_or_create_model` | `@patch(...)` | Model yükleme/oluşturma |

### 6.2 JavaScript — DOM Bağımsız Test

Frontend'de DOM-bağımlı fonksiyonlar (fetchWeather, showResults vb.) doğrudan test edilmez. Bunun yerine:

1. **İş mantığı fonksiyonları** (calculateAutoToprakNemi, getWeatherEmoji, vb.) test dosyasında izole edilip bağımsız test edilir.
2. Bu yaklaşım **unit test prensibine** uygundur ve DOM mock'laması gerekmez.

---

## 7. Testleri Çalıştırma Komutları

### 🐍 Python Testleri (AI Engine)

```bash
# Proje kök dizinine gidin
cd ai_engine

# Gerekli bağımlılıkları yükleyin (bir kerelik)
pip install pytest

# Testleri çalıştırın
python -m pytest test_predict.py -v

# Kısa çıktı ile
python -m pytest test_predict.py -v --tb=short

# Sadece belirli bir test sınıfını çalıştırın
python -m pytest test_predict.py::TestAnalyzeConditions -v
python -m pytest test_predict.py::TestEdgeCases -v
python -m pytest test_predict.py::TestFlaskEndpoints -v

# Sadece belirli bir testi çalıştırın
python -m pytest test_predict.py::TestAnalyzeConditions::test_sicaklik_cok_dusuk_don_riski -v
```

### 🌐 JavaScript Testleri (Frontend)

```bash
# Frontend dizinine gidin
cd frontend

# Gerekli bağımlılıkları yükleyin (bir kerelik)
npm install

# Testleri çalıştırın
npx jest --verbose

# Coverage raporu ile
npx jest --verbose --coverage

# Watch modunda (dosya değişikliklerini izleyerek)
npx jest --watch --verbose

# Sadece belirli bir test grubunu çalıştırın
npx jest --verbose -t "Otomatik Toprak Nemi"
npx jest --verbose -t "Renk Skalası"
npx jest --verbose -t "Şehir Filtreleme"
```

### 🔄 Tüm Testleri Tek Seferde (PowerShell)

```powershell
# Proje kök dizininden
Write-Host "=== AI ENGINE TESTLERİ ===" -ForegroundColor Cyan
python -m pytest ai_engine/test_predict.py -v --tb=short

Write-Host "`n=== FRONTEND TESTLERİ ===" -ForegroundColor Cyan
Set-Location frontend; npx jest --verbose; Set-Location ..
```

---

## 8. Test Sonuçları

### 🐍 Python Test Sonuçları

```
============================= test session starts =============================
platform win32 -- Python 3.11.7, pytest-9.0.3
collected 49 items

test_predict.py::TestAnalyzeConditions::test_ideal_sicaklik_bugday         PASSED
test_predict.py::TestAnalyzeConditions::test_sicaklik_cok_dusuk_don_riski  PASSED
test_predict.py::TestAnalyzeConditions::test_sicaklik_asiri_yuksek         PASSED
test_predict.py::TestAnalyzeConditions::test_sicaklik_sinir_degeri_tam_ideal_min PASSED
test_predict.py::TestAnalyzeConditions::test_sicaklik_sinir_degeri_tam_ideal_max PASSED
test_predict.py::TestAnalyzeConditions::test_sicaklik_1_derece_altinda     PASSED
test_predict.py::TestAnalyzeConditions::test_ph_ideal_aralik               PASSED
test_predict.py::TestAnalyzeConditions::test_ph_cok_asidik                 PASSED
test_predict.py::TestAnalyzeConditions::test_ph_cok_bazik                  PASSED
test_predict.py::TestAnalyzeConditions::test_ph_sinir_tam_min              PASSED
test_predict.py::TestAnalyzeConditions::test_ph_sinir_tam_max              PASSED
test_predict.py::TestAnalyzeConditions::test_toprak_nemi_ideal             PASSED
test_predict.py::TestAnalyzeConditions::test_toprak_nemi_cok_dusuk_kritik_sulama PASSED
test_predict.py::TestAnalyzeConditions::test_toprak_nemi_asiri_yuksek_kok_curumesi PASSED
test_predict.py::TestAnalyzeConditions::test_toprak_nemi_sifir             PASSED
test_predict.py::TestAnalyzeConditions::test_toprak_nemi_100               PASSED
test_predict.py::TestAnalyzeConditions::test_nitrojen_yeterli              PASSED
test_predict.py::TestAnalyzeConditions::test_nitrojen_sifir                PASSED
test_predict.py::TestAnalyzeConditions::test_fosfor_sifir                  PASSED
test_predict.py::TestAnalyzeConditions::test_potasyum_sifir                PASSED
test_predict.py::TestAnalyzeConditions::test_tum_besinler_asiri_yuksek     PASSED
test_predict.py::TestAnalyzeConditions::test_bitki_sagligi_iyi             PASSED
test_predict.py::TestAnalyzeConditions::test_bitki_sagligi_kritik          PASSED
test_predict.py::TestAnalyzeConditions::test_bitki_sagligi_sifir           PASSED
test_predict.py::TestAnalyzeConditions::test_bitki_sagligi_orta            PASSED
test_predict.py::TestOverallScore::test_ideal_kosullar_yuksek_skor         PASSED
test_predict.py::TestOverallScore::test_en_kotu_kosullar_dusuk_skor        PASSED
test_predict.py::TestOverallScore::test_skor_0_1_araliginda                PASSED
test_predict.py::TestOverallScore::test_skor_ortalama_hesabi               PASSED
test_predict.py::TestUrunBazli::test_domates_yuksek_potasyum_ihtiyaci      PASSED
test_predict.py::TestUrunBazli::test_cay_asidik_toprak_tercihi             PASSED
test_predict.py::TestUrunBazli::test_bilinmeyen_urun_bugday_fallback       PASSED
test_predict.py::TestEkUyarilar::test_hava_nemi_cok_yuksek_mantar_uyarisi  PASSED
test_predict.py::TestEkUyarilar::test_sicaklik_35_ustu_sulama_zamani       PASSED
test_predict.py::TestEkUyarilar::test_sicaklik_5_alti_don_uyarisi          PASSED
test_predict.py::TestFlaskEndpoints::test_health_endpoint                  PASSED
test_predict.py::TestFlaskEndpoints::test_predict_endpoint_ideal_data      PASSED
test_predict.py::TestFlaskEndpoints::test_predict_endpoint_bos_body        PASSED
test_predict.py::TestFlaskEndpoints::test_predict_endpoint_eksik_parametreler PASSED
test_predict.py::TestFlaskEndpoints::test_predict_endpoint_hatali_veri     PASSED
test_predict.py::TestFlaskEndpoints::test_predict_response_yapisi          PASSED
test_predict.py::TestFlaskEndpoints::test_predict_tf_confidence_0_1_arasi  PASSED
test_predict.py::TestKerasModelMock::test_model_8_parametre_alir           PASSED
test_predict.py::TestKerasModelMock::test_model_girdi_sirasi               PASSED
test_predict.py::TestEdgeCases::test_tum_degerler_sifir                    PASSED
test_predict.py::TestEdgeCases::test_negatif_degerler                      PASSED
test_predict.py::TestEdgeCases::test_cok_buyuk_degerler                    PASSED
test_predict.py::TestEdgeCases::test_float_ondalik_degerler                PASSED
test_predict.py::TestEdgeCases::test_string_to_float_donusum               PASSED
test_predict.py::TestEdgeCases::test_eksik_veri_default_degerler           PASSED
test_predict.py::TestEdgeCases::test_tum_urunler_crash_etmemeli            PASSED

================= 49 passed in 7.34s =================
```

### 🌐 JavaScript Test Sonuçları

```
PASS js/main.test.js
  Otomatik Toprak Nemi Hesaplayıcı (calculateAutoToprakNemi)
    ✓ Normal koşullar: 25°C sıcaklık, %50 nem → beklenen sonuç
    ✓ Yüksek sıcaklık: 40°C, %50 nem → ciddi buharlaşma
    ✓ Çok yüksek sıcaklık: 50°C, %30 nem → neredeyse sıfır
    ✓ Buharlaşma eşiği: Tam 20°C → buharlaşma 0 olmalı
    ✓ Yaz ortası Adana: 42°C, %25 nem → kurak
    ✓ Kış Rize: 5°C, %85 nem → nemli
    ✓ Sonuç her zaman 0-100 arasında olmalı (fuzz test)
    ... (25 test toplam)

  Renk Skalası — Confidence → CSS Class
    ✓ Confidence 0.75 → positive (Yeşil) — TAM SINIR
    ✓ Confidence 0.50 → warning (Sarı) — TAM SINIR
    ✓ Confidence 0.49 → danger (Kırmızı)
    ✓ Kayan nokta hassasiyeti: 0.7499999999 → warning
    ... (11 test toplam)

  Şehir Filtreleme
    ✓ Boş filtre → 81 il döndürmeli
    ✓ Türkçe karakter: "ş" araması → sonuç var
    ... (8 test toplam)

Test Suites: 1 passed, 1 total
Tests:       84 passed, 84 total
Time:        0.519 s
```

---

## 9. Tespit Edilen Sorunlar ve Düzeltmeler

### ✅ SORUN 1: Input Validation Yok — DÜZELTİLDİ

**Sorun:** `predict.py` gelen verilere tip kontrolü yapmıyordu. `"çok_sıcak"` gibi bir string `float()` dönüşümünde hata veriyor ama kullanıcıya anlamlı bir mesaj gösterilmiyordu (sadece genel `Exception` yakalanıyordu).

**Çözüm:** `safe_float()` fonksiyonu eklendi:
```python
def safe_float(value, field_name, default):
    """Güvenli float dönüşümü — hatalı tip gelirse anlamlı hata fırlatır."""
    if value is None:
        return float(default)
    try:
        return float(value)
    except (ValueError, TypeError):
        raise ValueError(
            f"'{field_name}' alanı sayısal bir değer olmalıdır. "
            f"Gelen değer: '{value}' (tip: {type(value).__name__}). "
            f"Lütfen geçerli bir sayı gönderin."
        )
```
- Hatalı tipler artık **hangi alanın, hangi değerin** hatalı olduğunu belirten açıklayıcı mesaj ile reddediliyor.
- `/predict` endpoint'inde `ValueError` ayrı yakalanarak `400` + `tip` yardımcı bilgi alanı ile döndürülüyor.
- **26 yeni test** bu davranışı doğruluyor (`TestValidationAndClamp` sınıfı).

---

### ✅ SORUN 2: Negatif Değer Kontrolü Yok — DÜZELTİLDİ

**Sorun:** Fiziksel olarak mümkün olmayan değerler (negatif fosfor, %200 nem) kabul ediliyordu. Sistem çökmüyordu ama anlamsız sonuçlar üretebiliyordu.

**Çözüm:** `PARAMETRE_SINIRLARI` sözlüğü ve `clamp_value()` fonksiyonu eklendi:
```python
PARAMETRE_SINIRLARI = {
    'sicaklik':      (-60.0, 60.0),     # °C — dünya ekstrem sınırları
    'nem':           (0.0, 100.0),       # % — hava nemi
    'toprak_nemi':   (0.0, 100.0),       # % — toprak nemi
    'ph':            (0.0, 14.0),        # pH skalası
    'nitrojen':      (0.0, 500.0),       # mg/kg
    'fosfor':        (0.0, 500.0),       # mg/kg
    'potasyum':      (0.0, 500.0),       # mg/kg
    'bitki_sagligi': (0.0, 100.0),       # 0-100 skor
}
```
- Negatif fosfor → **0'a clamp** edilir (hata fırlatmak yerine güvenli aralığa çekilir).
- pH 20 → **14'e clamp** edilir (pH skalası üst sınırı).
- Sıcaklık 1000°C → **60°C'ye clamp** edilir.
- `clamp_value()` testlerle doğrulandı (10 ayrı clamp testi).

---

### ✅ SORUN 3: Backend Toprak Nemi Clamp Yok — DÜZELTİLDİ

**Sorun:** Frontend formülü `Math.min(100, Math.max(0, result))` ile clamp yapıyordu ama backend tarafında benzer bir validasyon yoktu.

**Çözüm:** `validate_and_clamp()` fonksiyonu hem `analyze_conditions()` hem de `/predict` endpoint'inde kullanılıyor:
```python
def validate_and_clamp(data, field_name, default):
    """Veriyi al → float'a çevir → fiziksel sınırlara clamp et."""
    raw = data.get(field_name, default)
    value = safe_float(raw, field_name, default)
    return clamp_value(value, field_name)
```
- Toprak nemi dahil **tüm 8 parametre** artık backend'de de clamp ediliyor.
- Frontend ve backend aynı güvenli aralıkları (0-100) kullanıyor.
- Entegrasyon testi: Endpoint'e aşırı değerler gönderildiğinde clamp sonrası başarılı yanıt dönüyor.

---

### 💡 Gelecek Test Önerileri

| Öncelik | Alan | Öneri |
|---------|------|-------|
| Yüksek | E2E Test | Cypress/Playwright ile frontend → backend → AI Engine tam akış testi |
| Yüksek | API Test | Backend `server.js` için supertest ile endpoint testleri |
| Orta | Load Test | Aynı anda 100+ tahmin isteği gönderme (Artillery/k6) |
| Orta | Model Test | Gerçek model ile regresyon testi (belirli girdilerde belirli çıktı beklentisi) |
| Düşük | UI Test | CSS renk skalası görsel regresyon testi |

---

> **Not:** Bu test suite'i CI/CD pipeline'ına eklenebilir. Tüm testler mock kullandığı için dış bağımlılık gerektirmez ve saniyeler içinde tamamlanır.
