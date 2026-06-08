# Akıllı Tarım Destek Sistemi - API Tasarımı ve Gereksinim Dokümanı

Bu doküman, "Akıllı Tarım Destek Sistemi" projesinin backend (sunucu tarafı) mimarisinde ihtiyaç duyulan API uç noktalarını (endpoints) ve bu uç noktaların tasarım detaylarını içermektedir.

---

## 1. Genel Bakış
Sistem, çiftçilerin tarlalarındaki verileri (nem, sıcaklık, toprak pH vb.) form arayüzünden girmelerini veya şehir seçerek otomatik hava durumu verisi çekmelerini sağlayarak, yapay zeka üzerinden akıllı sulama/gübreleme tavsiyeleri almalarını sağlamak üzere tasarlanmıştır. Projenin şu anki versiyonunda veri kalıcılığı (veritabanı) bulunmamakta olup, sistem anlık veri işleme prensibiyle (stateless) çalışmaktadır.

## 2. API Tasarım İlkeleri
* **Protokol:** RESTful API
* **Veri Formatı:** JSON
* **Temel URL:** `http://localhost:3000/api`

---

## 3. API Uç Noktaları (Endpoints)

Mevcut sistemde aşağıdaki 3 temel uç nokta bulunmaktadır:

### 3.1. Sistem Durum Kontrolü (`/status`)
Node.js backend servisinin ayakta olup olmadığını kontrol eder.

| Metot | Uç Nokta | Açıklama |
| :--- | :--- | :--- |
| `GET` | `/status` | Backend servisinin durumunu döner. |

### 3.2. AI Servis Durum Kontrolü (`/ai-status`)
Node.js üzerinden, Python tabanlı yapay zeka (Flask) servisinin çalışıp çalışmadığını kontrol eder.

| Metot | Uç Nokta | Açıklama |
| :--- | :--- | :--- |
| `GET` | `/ai-status` | AI servisinin bağlantı durumunu ve versiyon bilgilerini döner. |

### 3.3. Karar Destek ve Öneri Sistemi (`/predict`)
Kullanıcıdan gelen tarla verilerini AI servisine iletir ve çıkan sonucu kullanıcıya geri döner.

| Metot | Uç Nokta | Açıklama |
| :--- | :--- | :--- |
| `POST` | `/predict` | Hava ve toprak verilerini alıp analiz sonuçlarını (sulama kararı, gübre tavsiyesi, güven skoru) döner. |

---

## 4. Örnek Veri Yapıları

### Sensör/Form Verisi Gönderimi (Request Body - POST `/predict`)
```json
{
  "urun": "bugday",
  "sicaklik": 24.8,
  "nem": 60,
  "toprak_nemi": 42.5,
  "ph": 6.8,
  "nitrojen": 40,
  "fosfor": 60,
  "potasyum": 120,
  "bitki_sagligi": 70
}
```

### Karar Destek Yanıtı (Response Body - POST `/predict`)
```json
{
  "prediction": "Sulama yapılması önerilir.",
  "ozet": "Sulama yapılması önerilir. 2 adet uyarı tespit edildi. Gübreleme tavsiyesi mevcut.",
  "confidence": 0.85,
  "tf_confidence": 0.55,
  "confidence_factors": [
    {"factor": "Sıcaklık ideal aralıkta", "score": 1.0},
    {"factor": "Toprak pH ideal aralıkta", "score": 1.0}
  ],
  "warnings": [
    "Toprak nemi yetersiz (%42). İdeal: %50-%70"
  ],
  "recommendations": [
    "Sulama yapılması önerilir. Damla sulama sistemi verimlilik açısından idealdir."
  ],
  "gubre_tavsiyeleri": [
    "Azotlu gübre: Amonyum sülfat (%21) uygulanması önerilir."
  ],
  "urun_ad": "Buğday",
  "ai_technology": {
    "model": "TensorFlow v2.16.1",
    "type": "Keras Sequential Neural Network",
    "layers": "InputLayer(5) → Dense(16, ReLU) → Dense(1, Sigmoid)",
    "description": "5 girdi özelliğini değerlendiren yapay sinir ağı modeli ve kural tabanlı uzman sistemin birleştirilmiş analizi"
  }
}
```

---

## 5. Güvenlik ve Hata Yönetimi
1.  **Hata Kodları:** Standart HTTP kodları (200 OK, 400 Bad Request, 500 Internal Server Error, 503 Service Unavailable) kullanılır. AI servisine bağlanılamadığında 503 dönülür.
2.  **Stateless Yapı:** Sistemin şu anki durumunda kullanıcı hesabı zorunluluğu (Authentication/JWT) veya Rate Limiting bulunmamaktadır; bu özelliklerin veritabanı entegrasyonu aşamasında (Gelecek Sürüm) eklenmesi planlanmaktadır.
