# Akıllı Tarım Destek Sistemi - API Tasarımı ve Gereksinim Dokümanı

Bu doküman, "Akıllı Tarım Destek Sistemi" projesinin backend (sunucu tarafı) mimarisinde ihtiyaç duyulan API uç noktalarını (endpoints) ve bu uç noktaların tasarım detaylarını içermektedir.

---

## 1. Genel Bakış
Sistem, çiftçilerin tarlalarındaki verileri (nem, sıcaklık, toprak pH vb.) IoT cihazları üzerinden takip etmelerini, geçmişe dönük analiz yapmalarını ve sistemden akıllı sulama/gübreleme tavsiyeleri almalarını sağlamak üzere tasarlanmıştır.

## 2. API Tasarım İlkeleri
* **Protokol:** RESTful API
* **Veri Formatı:** JSON
* **Kimlik Doğrulama:** JWT (JSON Web Token)
* **Temel URL:** `https://api.akillitarim.com/v1`

---

## 3. API Uç Noktaları (Endpoints)

### 3.1. Kimlik Doğrulama ve Kullanıcı Yönetimi (`/auth`)
Kullanıcıların sisteme güvenli giriş yapmasını sağlar.

| Metot | Uç Nokta | Açıklama |
| :--- | :--- | :--- |
| `POST` | `/auth/register` | Yeni çiftçi/danışman kaydı oluşturur. |
| `POST` | `/auth/login` | Giriş yapar ve JWT token döner. |
| `GET` | `/auth/profile` | Giriş yapmış kullanıcının bilgilerini getirir. |
| `PUT` | `/auth/update` | Kullanıcı profil bilgilerini günceller. |

### 3.2. Tarla ve Arazi Yönetimi (`/fields`)
Çiftçiye ait farklı tarlaların koordinat ve ürün bazlı yönetimi.

| Metot | Uç Nokta | Açıklama |
| :--- | :--- | :--- |
| `GET` | `/fields` | Kullanıcıya ait tüm tarlaları listeler. |
| `POST` | `/fields` | Yeni bir tarla tanımı (isim, konum, ürün tipi) ekler. |
| `GET` | `/fields/{id}` | Belirli bir tarlanın detaylarını ve mevcut durumunu getirir. |
| `DELETE` | `/fields/{id}` | Belirli bir tarlayı sistemden siler. |

### 3.3. Sensör Verileri ve IoT Entegrasyonu (`/sensors`)
IoT cihazlarından gelen verilerin işlendiği bölümdür.


| Metot | Uç Nokta | Açıklama |
| :--- | :--- | :--- |
| `POST` | `/sensors/data` | IoT cihazından gelen anlık veriyi (nem, sıcaklık vb.) kaydeder. |
| `GET` | `/sensors/{fieldId}/history` | Belirli bir tarlanın geçmiş sensör verilerini (grafik için) getirir. |
| `GET` | `/sensors/status` | Bağlı olan sensörlerin pil ve bağlantı durumunu kontrol eder. |

### 3.4. Karar Destek ve Öneri Sistemi (`/recommendations`)
Toplanan verilerin analiz edilerek kullanıcıya tavsiye sunulduğu kısımdır.

| Metot | Uç Nokta | Açıklama |
| :--- | :--- | :--- |
| `GET` | `/recommendations/irrigation` | Sensör verilerine göre sulama gerekip gerekmediğini döner. |
| `GET` | `/recommendations/fertilizer` | Toprak analizine göre gübreleme önerisi sunar. |
| `GET` | `/recommendations/weather` | Harici servislerden alınan hava durumuna göre don veya fırtına uyarısı yapar. |

---

## 4. Örnek Veri Yapıları

### Sensör Verisi Gönderimi (Request Body)
```json
{
  "device_id": "SN-98721",
  "field_id": 102,
  "timestamp": "2026-03-25T14:30:00Z",
  "data": {
    "soil_moisture": 42.5,
    "temperature": 24.8,
    "humidity": 60,
    "ph_level": 6.8
  }
}
```

### Karar Destek Yanıtı (Response Body)
```json
{
  "field_id": 102,
  "status": "Warning",
  "recommendation": "Toprak nemi %45'in altına düştü. Bugün saat 18:00'den sonra sulama yapılması önerilir.",
  "forecast": "Gelecek 24 saat içinde yağış beklenmiyor."
}
```

---

## 5. Güvenlik ve Hata Yönetimi
1.  **Hata Kodları:** Standart HTTP kodları (200 OK, 201 Created, 401 Unauthorized, 404 Not Found, 500 Internal Server Error) kullanılır.
2.  **Rate Limiting:** IoT cihazlarının aşırı veri gönderimiyle sistemi yormaması için cihaz başına dakika sınırı uygulanmalıdır.
3.  **Data Validation:** Gelen sensör verileri mantıksal aralıklar (örn: sıcaklık -50 ile +70 arası) dışında ise reddedilmelidir.
