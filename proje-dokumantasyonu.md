# Akıllı Tarım Destek Sistemi - Kapsamlı Proje Dokümantasyonu

Bu dokümantasyon, "Akıllı Tarım Destek Sistemi" projesinin araştırma, tasarım, geliştirme, test ve entegrasyon aşamalarını içeren tüm süreçleri detaylandırmak amacıyla hazırlanmıştır. Proje, modern veri analitiği, makine öğrenmesi ve bulut altyapılarını kullanarak tarımsal verimliliği artırmayı hedefleyen uçtan uca bir sistemdir.

---

## 1. Proje Tanımı ve Paydaş Analizi

### 1.1. Projenin Amacı ve Kapsamı
Akıllı Tarım Destek Sistemi; hava durumu verileri, toprak analizleri, sensör çıktıları (nem, sıcaklık vb.) ve bitki sağlığı bilgilerini bir araya getirerek çiftçilere optimize edilmiş ekim zamanı ve gübreleme önerileri sunan yapay zeka destekli bir platformdur. Projenin temel amacı; kaynak israfını önlemek, ürün verimliliğini artırmak ve tarımsal sürdürülebilirliğe katkı sağlamaktır.

### 1.2. Paydaş Analizi ve Gereksinimler
Sistemin tasarımı ve geliştirilmesi sürecinde hedef kitleyi oluşturan temel paydaşların ihtiyaçları analiz edilmiştir:
* **Çiftçiler:** Kolay anlaşılır arayüz, anlık hava durumu uyarıları ve nokta atışı gübreleme/sulama tavsiyeleri.
* **Ziraat Mühendisleri:** Detaylı veri analitiği panelleri, geçmişe dönük toprak analiz raporları ve model tahmin çıktılarının teknik detayları.
* **Tarım Kooperatifleri:** Bölgesel bazda verimlilik analizleri ve toplu veri izleme yetenekleri.

---

## 2. Teknoloji Seçimi ve Altyapı Planlaması

Sistemin uzun vadeli ölçeklenebilirlik, maliyet ve performans kriterleri göz önünde bulundurularak teknik altyapı şu şekilde planlanmıştır:

* **Programlama Dili ve Yapay Zeka Kütüphaneleri:** Projenin çekirdeğini oluşturan veri işleme ve makine öğrenmesi modelleri için **Python**, **Scikit-learn** ve **Pandas** kütüphaneleri tercih edilmiştir. API servisi için **Flask** kullanılmıştır.
* **Bulut Altyapısı (Cloud Infrastructure):** Uygulamanın bulut ortamına taşınması için AWS veya benzeri platformlar (ECS, RDS, API Gateway) hedeflenmektedir.
* **Sürüm Kontrolü ve İş Birliği:** Kod tabanının yönetimi için **Git/GitHub** aktif olarak kullanılmaktadır.

---

## 3. Veri Yönetimi ve Ön İşleme (Data Preprocessing)

### 3.1. Kullanılan Veri Özellikleri (Features)
Sistem, karar mekanizmasını çalıştırabilmek için aşağıdaki temel parametreleri kullanmaktadır:
* `soil_moisture` (Toprak Nemi)
* `temperature` (Hava/Yüzey Sıcaklığı)
* `humidity` (Havadaki Nem Oranı)
* `ph_level` (Toprağın pH Seviyesi)

*Ayrıca veri seti zaman damgası (`timestamp`) ile saatlik olarak (örn: 2026-03-25 14:30:00) kayıt altına alınmaktadır.*

### 3.2. Veri Ön İşleme ve Hata Toleransı
Toplanan ham verilerin makine öğrenmesi modellerine beslenmeden önce tabi tutulduğu adımlar:
1. **Eksik Veri Tamamlama (Missing Value Imputation):** Sensör bağlantı kopukluklarından kaynaklanan eksik veriler (NaN), sistemin çökmesini engellemek adına **"Güvenli Medyan Ataması"** yöntemiyle otomatik olarak doldurulmaktadır.
2. **Hedef Sınıflar (Target Classes):** Veri seti modelleme için 3 ana aksiyon sınıfına ayrılmıştır: `Durum Normal`, `Gubre/Ilac Uygula` ve `Sulama Yap`.

---

## 4. Model Geliştirme, Test Değerleri ve Eğitim Sonuçları

### 4.1. Tahminleme Algoritmaları ve Karşılaştırma
Sistemin beyni olacak yapay zeka modelinin seçimi için birden fazla algoritma test edilmiş ve aşağıdaki başarı oranları elde edilmiştir:
* **Logistic Regression Başarı Oranı:** %72.50
* **Support Vector Machine (SVM) Başarı Oranı:** %50.00
* **Random Forest Classifier Başarı Oranı:** %100.00

*Sonuç:* En yüksek başarıyı gösteren **Random Forest Classifier** algoritması projenin ana modeli olarak seçilmiş ve optimizasyon aşamasına geçilmiştir.

### 4.2. Hiperparametre Optimizasyonu (GridSearchCV)
Seçilen Random Forest modelinin performansını en üst düzeye çıkarmak ve aşırı öğrenmeyi kontrol altında tutmak için `GridSearchCV` uygulanmıştır. Bulunan en iyi parametreler şunlardır:
* `max_depth`: None
* `min_samples_split`: 2
* `n_estimators`: 50

### 4.3. Final Test Sonuçları ve Sınıflandırma Raporu (Classification Report)
Optimize edilen model üzerinde yapılan son testlerde (40 örneklem üzerinden) **%100 (1.00) Accuracy (Doğruluk)** oranına ulaşılmıştır. Sınıflandırma metrikleri (Precision, Recall, F1-Score) tüm sınıflar için mükemmel seviyededir (1.00).

| Sınıf (Class) | Precision | Recall | F1-Score | Support (Örnek Sayısı) |
| :--- | :---: | :---: | :---: | :---: |
| **Durum Normal** | 1.00 | 1.00 | 1.00 | 8 |
| **Gubre/Ilac Uygula** | 1.00 | 1.00 | 1.00 | 19 |
| **Sulama Yap** | 1.00 | 1.00 | 1.00 | 13 |
| *Genel (Accuracy/Avg)* | *1.00* | *1.00* | *1.00* | *40* |

---

## 5. Sistem Mimarisi ve API Entegrasyonu

Modelin karar verme yeteneği diğer platformlara entegre edilebilmesi için **Flask** tabanlı bir REST API (`predict.py`) olarak servis edilmektedir. Sistem şu anda `http://127.0.0.1:5000` üzerinden geliştirme ortamında (development mode) test edilmektedir.

---

## 6. Sistem Stres Testleri ve Uç Senaryolar

Modelin farklı iklim ve sensör arıza senaryolarındaki tepkileri test edilmiş ve başarılı sonuçlar alınmıştır.

**[Senaryo 1: Bahar Ayı İdeal Şartlar]**
* *Gelen Ham Veri:* Nem: 60, Sıcaklık: 24, Rutubet: 55, pH: 6.5
* *Yapay Zeka Kararı:* **Durum Normal**

**[Senaryo 2: Ağustos Ayı Aşırı Kuraklık]**
* *Gelen Ham Veri:* Nem: 15, Sıcaklık: 42, Rutubet: 20, pH: 6.8
* *Yapay Zeka Kararı:* **Sulama Yap**

**[Senaryo 3: IoT Sensör Bağlantı Kopukluğu ve Uç Değer]**
* *Gelen Ham Veri:* Nem: NaN, Sıcaklık: 22, Rutubet: NaN, pH: 9.5
* *Sistem Davranışı:* Sensörden eksik veri (NaN) geldiği tespit edildi ve "Güvenli Medyan Ataması" ile düzeltildi.
* *Yapay Zeka Kararı:* **Gubre/Ilac Uygula** (Yüksek pH sebebiyle müdahale kararı).

*(Not: Model ayrıca tamamen farklı bir veri seti ile "Kurak İklim Simülasyonu" üzerinden test edilmiş ve orada da 50 test verisinde %100 başarı oranını korumuştur.)*

---

## 7. Proje Yönetimi ve Takım Görev Dağılım Matrisi

| Ekip Üyesi | Sorumlu Olduğu Temel Görevler |
| :--- | :--- |
| **Melik Buğra Kara** | Proje Yönetimi, İş Akışı Planlaması, Bulut Altyapısı Tasarımı, Sürüm Kontrolü ve Entegrasyon Yönetimi, Genel Dokümantasyon |
| **Arda Özcan Çifci** | Teknoloji Seçimi, Veritabanı Şeması Tasarımı, Özellik Mühendisliği ve Model Performans İyileştirme Araştırmaları |
| **Mehmet Ali Kıraççakalı** | Tahminleme Algoritmalarının Seçimi, Temel/Gelişmiş Model Geliştirme, Hiperparametre Optimizasyonu, Ölçeklenebilirlik Testleri |
| **Meryem Abdurrahman** | Proje Dokümantasyon Standartları, API Entegrasyon Tasarımı, Literatür Taraması, Final Sunumu ve Değerlendirme |
| **Ceylan Dağılma** | Veri Kaynakları Araştırması, Veri Görselleştirme/Analiz Raporlama, Kullanıcı Arayüzü Tasarımı, Çapraz Doğrulama Çalışmaları |
| **Kaan Mert Keklik** | Proje Paydaş Analizi, Veri Toplama Modülü Tasarımı, Veri Ön İşleme Adımları, Model Optimizasyonu, Son Testler |
