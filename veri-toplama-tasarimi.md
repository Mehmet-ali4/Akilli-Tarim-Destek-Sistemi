# Akıllı Tarım Destek Sistemi - Veri Toplama ve İşleme Tasarımı

Bu doküman, sistemin çalışması için gerekli olan verilerin toplanması, doğrulanması ve işlenmesi aşamalarını açıklamaktadır.

---

## 1. Veri Kaynakları
Mevcut sistem, çalışabilmek için iki temel veri kaynağı kullanmaktadır:

### 1.1. Manuel Kullanıcı Girişi (Form Verileri)
Kullanıcı, tarla koşullarını temsil eden sensör ve toprak değerlerini frontend arayüzü üzerinden sisteme girer. İlerleyen versiyonlarda bu değerlerin IoT cihazlarından (IoT Hub / MQTT) otomatik olarak çekilmesi planlanmaktadır, ancak v1.0 sürümünde veriler kullanıcı tarafından sağlanır.

*   **Sıcaklık (°C):** Havanın mevcut sıcaklığı (Hava durumu API'sinden çekilen veri ile otomatik doldurulabilir)
*   **Nem (%):** Havanın bağıl nem oranı
*   **Toprak Nemi (%):** Topraktaki nem oranı (Hesaplanabilir veya manuel girilir)
*   **pH:** Toprağın asitlik derecesi (Manuel giriş)
*   **Azot, Fosfor, Potasyum (N, P, K):** Topraktaki temel besin elementleri (mg/kg) (Manuel giriş)
*   **Bitki Sağlığı Skoru (0-100):** Kullanıcının gözlemlerine dayalı sağlık skoru

### 1.2. Dış API Verileri (OpenWeatherMap)
Kullanıcı bir şehir seçtiğinde veya "Konumumu Bul" (Geolocation) özelliğini kullandığında, sistem anlık hava durumu verilerini çekmek için OpenWeatherMap API'sini kullanır.

*   **Protokol:** HTTP GET (Axios kullanılarak)
*   **Alınan Veriler:** Sıcaklık (°C) ve Hava Nemi (%)

---

## 2. Veri Akışı ve İşleme Mimarisi

Sistemin veri işleme mimarisi anlık analiz (stateless) prensibine dayanmaktadır.

1.  **Veri Toplama:** Frontend (JavaScript) arayüzündeki form aracılığıyla kullanıcı tarafından girilen veriler (veya API'den çekilen hava durumu bilgileri) toplanır.
2.  **Veri Formatlama:** Form verileri JSON nesnesine dönüştürülür.
3.  **İletim:** Frontend, JSON verisini Node.js Backend API'sine (`POST /api/predict`) Axios ile iletir.
4.  **Backend Proxy:** Node.js backend, gelen veriyi doğrudan (veya gerekirse formatlayarak) Python tabanlı Yapay Zeka (Flask) servisine iletir.
5.  **Yapay Zeka Analizi:**
    *   Python Flask servisi, TensorFlow modeli ve kural tabanlı uzman sistem aracılığıyla gelen verileri analiz eder.
    *   İdeal bitki koşullarıyla (ürüne göre) karşılaştırır.
    *   Sulama kararı, gübre tavsiyesi ve genel durum skorunu hesaplar.
6.  **Yanıt:** AI servisi analiz sonucunu Node.js backend'ine, oradan da frontend'e JSON olarak döndürür ve kullanıcı arayüzünde gösterilir.

---

## 3. Gelecek Vizyonu (Veri Toplama)
Projenin sonraki sürümlerinde (v2.x) sistemin aşağıdaki şekilde evrilmesi planlanmaktadır:
*   **IoT Entegrasyonu:** Tarlaya yerleştirilecek sensörlerin (toprak nemi, pH, sıcaklık) MQTT protokolü ile doğrudan sunucuya bağlanması.
*   **Otomatik Veri Toplama (Cron Jobs):** Sensör verilerinin 3 saatte bir otomatik okunup veritabanına kaydedilmesi.
*   **Veri Kalıcılığı:** Toplanan verilerin SQL/NoSQL veritabanında saklanarak zaman serisi analizi ve geçmişe dönük raporlama yapılması.
