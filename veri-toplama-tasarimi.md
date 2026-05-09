# Akıllı Tarım Destek Sistemi - Veri Toplama ve Entegrasyon Tasarım Belgesi

## 1. Veri Kaynakları, Formatlar ve Toplama Sıklığı

| Veri Tipi | Veri Kaynağı | Veri Formatı | Toplama Sıklığı | Entegrasyon Yöntemi (Java & SQL) |
| :--- | :--- | :--- | :--- | :--- |
| **Hava Durumu** | OpenWeatherMap API | JSON | 3 Saatte Bir | Java HttpClient ile HTTP GET isteği atılarak alınır, SQL tablosuna yazılır. |
| **Toprak Analizi** | IoT Sensörleri | JSON / Csv | 30 Dakikada Bir | Sensörlerden gelen veriler Gateway üzerinden dinlenir. |
| **Bitki Sağlığı** | Kullanıcı Girdisi / Harici Görüntü İşleme API'si | Multipart (Görsel) / JSON | Günlük (veya Manuel) | Fotoğraflar AI servisine gönderilir, dönen sağlık skoru (JSON) SQL veri tabanına kaydedilir. |

## 2. Olası Hataları Ele Alma Stratejileri (Error Handling)

*   **API Bağlantı Hataları:** Hava durumu API'sine erişilemediğinde Java tarafında `try-catch` blokları ve *Retry* mekanizması kurulacaktır. 3 başarısız denemeden sonra sistem, SQL'de kayıtlı olan son geçerli veriyi kullanacaktır.
*   **Sensör Verisi Kesintisi:** Sensörlerden veri gelmezse, "Sensör bağlantı hatası" fırlatılacak ve kullanıcı uyarılacaktır.
*   **Veri Formatı Uyuşmazlıkları:** Hatalı veriler reddedilip hata log dosyasına (`error_logs` tablosuna) yazılacaktır.

## 3. Veri Toplama Süreci Akış Diyagramı

```mermaid
graph TD;
    A[Zamanlayıcı / Scheduler Tetiklenmesi] --> B{Veri Kaynağı Seçimi};
    
    B -->|Hava Durumu API| C[REST API GET İsteği];
    B -->|Toprak Sensörleri| D[Sensör Verisi Okuma];
    B -->|Bitki Sağlığı| E[Kullanıcı Görsel Yüklemesi];

    C --> F{Yanıt Başarılı mı?};
    F -->|Evet| G[JSON Verisini Parse Et];
    F -->|Hayır| H[Logla ve Son Geçerli Veriyi Kullan];

    D --> I{Sensör Aktif mi?};
    I -->|Evet| J[Veriyi Doğrula / Validate];
    I -->|Hayır| K[Sistem Uyarısı Üret];

    E --> L[AI Analiz API'sine Gönder];
    L --> M[Sağlık Skorunu Al];

    G --> N[Standart Veri Modeline Dönüştür];
    J --> N;
    M --> N;

    N --> O[(SQL Veri Tabanına Kaydet)];
    H --> O;
    
    O --> P[Akıllı Tarım Analiz Motorunu Çalıştır];
