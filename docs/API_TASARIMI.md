# Akıllı Tarım Destek Sistemi — API Tasarım Belgesi

**Proje:** Akıllı Tarım Destek Sistemi  
**Grup:** Yapay Zeka Yoldaşları  
**Hazırlayan:** MERYEM ABDURRAHMAN (250541605@firat.edu.tr)  
**Tarih:** Mayıs 2026  
**Sürüm:** 1.0  

---

## 1. Genel Bakış

Bu belge, Akıllı Tarım Destek Sistemi'nin dış veri kaynaklarından veri alması ve tahminleme sonuçlarını diğer sistemlere göndermesi için kullanılacak API'lerin tasarımını tanımlamaktadır. Tüm API'ler RESTful mimari prensipleri ile JSON veri formatını kullanmaktadır.

**Temel URL:** `https://api.akilli-tarim.com/v1`

---

## 2. Kimlik Doğrulama ve Güvenlik

### 2.1 API Anahtarı (API Key)

Tüm isteklerde HTTP header'ında API anahtarı gönderilmelidir:

```
X-API-Key: your_api_key_here
```

### 2.2 OAuth 2.0

Üçüncü taraf sistemler için OAuth 2.0 kullanılır:

```json
POST /auth/token
Body: { "client_id": "...", "client_secret": "...", "grant_type": "client_credentials" }
Yanıt: { "access_token": "eyJ...", "token_type": "Bearer", "expires_in": 3600 }
```

### 2.3 Güvenlik Önlemleri

| Önlem | Açıklama |
|---|---|
| HTTPS/TLS | Tüm API istekleri şifrelenmiş HTTPS üzerinden iletilir |
| Rate Limiting | Dakikada maksimum 100 istek (429 hatası döner) |
| IP Kısıtlama | Yalnızca onaylı IP adreslerinden erişim izni |
| Token Süresi | OAuth token'ları 1 saat sonra geçersiz olur |
| Input Validation | Tüm giriş verileri doğrulanır, SQL injection engellenir |

---

## 3. API Uç Noktaları (Endpoints)

### 3.1 Hava Durumu Verisi

| Alan | Detay |
|---|---|
| **Endpoint** | `GET /data/weather` |
| **Açıklama** | Hava durumu API'sinden güncel veri çeker |
| **Kimlik Doğrulama** | API Key |
| **Parametreler** | `lat` (float), `lon` (float), `days` (int, 1-7) |

**Örnek Yanıt:**
```json
{
  "status": "success",
  "location": { "lat": 38.67, "lon": 39.22 },
  "data": [
    {
      "date": "2026-05-15",
      "temp_min": 12,
      "temp_max": 28,
      "humidity": 65,
      "rainfall_mm": 5.2,
      "wind_speed": 10
    }
  ]
}
```

---

### 3.2 Toprak Analizi Verisi

| Alan | Detay |
|---|---|
| **Endpoint** | `POST /data/soil` |
| **Açıklama** | Toprak analizi laboratuvarından veya sensörden veri alır |
| **Kimlik Doğrulama** | API Key |

**Örnek İstek:**
```json
{
  "field_id": "FIELD_001",
  "ph": 6.5,
  "nitrogen": 140,
  "phosphorus": 35,
  "potassium": 200,
  "moisture": 42.5
}
```

---

### 3.3 Bitki Sağlığı Sensör Verisi

| Alan | Detay |
|---|---|
| **Endpoint** | `POST /data/plant-health` |
| **Açıklama** | Bitki sağlığı sensörlerinden veri alır |
| **Kimlik Doğrulama** | API Key |

**Örnek İstek:**
```json
{
  "field_id": "FIELD_001",
  "sensor_id": "SENSOR_042",
  "leaf_color": "yellow",
  "disease_risk": 0.35,
  "image_url": "https://storage.akilli-tarim.com/images/img001.jpg"
}
```

---

### 3.4 Tahminleme ve Öneri

| Alan | Detay |
|---|---|
| **Endpoint** | `POST /predict/recommendation` |
| **Açıklama** | Hava, toprak ve bitki verilerini işleyerek ekim/gübreleme önerisi üretir |
| **Kimlik Doğrulama** | OAuth 2.0 Bearer Token |

**Örnek Yanıt:**
```json
{
  "status": "success",
  "field_id": "FIELD_001",
  "recommendation": {
    "planting_date": "2026-06-01",
    "fertilizer": { "type": "NPK 15-15-15", "amount_kg_per_ha": 250 },
    "confidence_score": 0.94,
    "notes": "Yağış beklentisi yüksek, sulama azaltılabilir."
  }
}
```

---

### 3.5 Sonuç Gönderimi (Dış Sistemler)

| Alan | Detay |
|---|---|
| **Endpoint** | `POST /export/farm-management` |
| **Açıklama** | Sonuçları çiftlik yönetim yazılımlarına veya tarım sigorta şirketlerine gönderir |
| **Kimlik Doğrulama** | OAuth 2.0 Bearer Token |

**Örnek İstek:**
```json
{
  "target_system": "FarmManager Pro",
  "field_id": "FIELD_001",
  "recommendation_id": "REC_2026_001",
  "callback_url": "https://farmmanager.com/webhook/results"
}
```

---

## 4. Hata Kodları

| HTTP Kodu | Hata Adı | Açıklama |
|---|---|---|
| 200 | OK | İstek başarılı |
| 201 | Created | Veri başarıyla oluşturuldu |
| 400 | Bad Request | Eksik veya hatalı parametre |
| 401 | Unauthorized | API anahtarı veya token geçersiz |
| 403 | Forbidden | Bu kaynağa erişim yetkisi yok |
| 404 | Not Found | İstenen kaynak bulunamadı |
| 429 | Too Many Requests | Rate limit aşıldı, 1 dakika bekleyin |
| 500 | Internal Server Error | Sunucu hatası, tekrar deneyin |

**Hata Yanıtı Formatı:**
```json
{
  "status": "error",
  "code": 401,
  "message": "Geçersiz API anahtarı. Lütfen X-API-Key header'ını kontrol edin.",
  "timestamp": "2026-05-15T18:00:00Z"
}
```

---

## Sürüm Geçmişi

| Sürüm | Tarih | Yazar | Değişiklik |
|---|---|---|---|
| 1.0 | 2026-05 | Meryem Abdurrahman | İlk oluşturma |
