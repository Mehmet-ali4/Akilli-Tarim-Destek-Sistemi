# Akıllı Tarım Destek Sistemi - Veritabanı Tasarımı

Bu belge, projemizdeki yapay zeka tabanlı öneri sisteminin (hava durumu, toprak analizi ve bitki sağlığı verilerini kullanarak) ihtiyaç duyduğu ilişkisel veritabanı yapısını ve tablolar arası ilişkileri (ER Diagram Mantığı) detaylandırmaktadır.

## 1. Veritabanı Tabloları

### A. Kullanıcılar Tablosu (`Kullanicilar`)
Sisteme kayıt olan çiftçilerin temel bilgilerini tutar.

| Kolon Adı | Veri Tipi | Kısıtlama (Constraint) | Açıklama |
| :--- | :--- | :--- | :--- |
| `KullaniciID` | INT | **Primary Key**, Auto Increment | Çiftçinin benzersiz kimlik numarası. |
| `AdSoyad` | VARCHAR(100) | NOT NULL | Çiftçinin adı ve soyadı. |
| `Email` | VARCHAR(100) | UNIQUE, NOT NULL | Sisteme giriş e-postası. |
| `SifreHash` | VARCHAR(255) | NOT NULL | Güvenlik için şifrelenmiş parola. |

### B. Tarla Tablosu (`Tarlalar`)
Çiftçilere ait arazilerin fiziksel ve konum özelliklerini tutar.

| Kolon Adı | Veri Tipi | Kısıtlama (Constraint) | Açıklama |
| :--- | :--- | :--- | :--- |
| `TarlaID` | INT | **Primary Key**, Auto Increment | Tarlanın benzersiz numarası. |
| `KullaniciID` | INT | **Foreign Key** | Tarlanın ait olduğu çiftçi (`Kullanicilar` tablosuna bağlı). |
| `TarlaAdi` | VARCHAR(100) | NOT NULL | Örn: "Kuzey Yamacı Buğdaylığı". |
| `Konum_Enlem` | DECIMAL(10,8)| NOT NULL | Hava durumu API'si için enlem. |
| `Konum_Boylam`| DECIMAL(11,8)| NOT NULL | Hava durumu API'si için boylam. |
| `Ekilmis_Urun`| VARCHAR(50) | NULL | Tarlada anlık ekili olan ürün (Örn: Mısır). |

### C. Toprak Analizi Tablosu (`Toprak_Verileri`)
Sensörlerden veya manuel ölçümlerden gelen toprak değerlerinin loglandığı tablodur.

| Kolon Adı | Veri Tipi | Kısıtlama (Constraint) | Açıklama |
| :--- | :--- | :--- | :--- |
| `AnalizID` | INT | **Primary Key**, Auto Increment | Analizin benzersiz numarası. |
| `TarlaID` | INT | **Foreign Key** | Analizin yapıldığı tarla (`Tarlalar` tablosuna bağlı). |
| `Tarih` | DATE | NOT NULL | Ölçüm tarihi. |
| `PH_Degeri` | DECIMAL(4,2) | NULL | Toprağın asit/baz oranı. |
| `Nem_Orani` | DECIMAL(5,2) | NULL | Yüzdelik nem oranı. |
| `NPK_Degerleri`| VARCHAR(50) | NULL | Azot (N), Fosfor (P), Potasyum (K) değerleri. |

### D. Hava Durumu Tablosu (`Hava_Verileri`)
Ekim zamanı tahmini için kullanılan geçmiş ve anlık hava olayları.

| Kolon Adı | Veri Tipi | Kısıtlama (Constraint) | Açıklama |
| :--- | :--- | :--- | :--- |
| `HavaVeriID` | INT | **Primary Key**, Auto Increment | Veri kaydının benzersiz numarası. |
| `TarlaID` | INT | **Foreign Key** | Verinin ait olduğu tarla (`Tarlalar` tablosuna bağlı). |
| `Tarih` | DATE | NOT NULL | Veri tarihi. |
| `Sicaklik_Ort`| DECIMAL(4,2) | NULL | Günlük ortalama sıcaklık (°C). |
| `Yagis_Miktari`| DECIMAL(6,2) | NULL | Düşen günlük yağış miktarı (mm). |

### E. Yapay Zeka Önerileri Tablosu (`Sistem_Onerileri`)
Algoritmanın işlediği veriler sonucunda çiftçiye sunduğu aksiyon önerileri.

| Kolon Adı | Veri Tipi | Kısıtlama (Constraint) | Açıklama |
| :--- | :--- | :--- | :--- |
| `OneriID` | INT | **Primary Key**, Auto Increment | Önerinin benzersiz numarası. |
| `TarlaID` | INT | **Foreign Key** | Önerinin yapıldığı tarla (`Tarlalar` tablosuna bağlı). |
| `Olusturma_Trh`| DATE | NOT NULL | Önerinin sisteme düştüğü tarih. |
| `Oneri_Turu` | VARCHAR(50) | NOT NULL | Kategori (Örn: "Ekim Zamanı", "Gübreleme"). |
| `Oneri_Detayi`| TEXT | NOT NULL | Yapay zekanın oluşturduğu detaylı yönlendirme metni. |

---

## 2. Tablolar Arası İlişkiler (ER Mantığı)

Veritabanımız, **`Tarlalar`** tablosunun merkezde olduğu ilişkisel bir yapı üzerine kurulmuştur. 

* **1:N (Bire Çok) İlişkiler:**
    * **Çiftçi - Tarla:** 1 çiftçinin birden fazla tarlası olabilir. (`Kullanicilar.KullaniciID` -> `Tarlalar.KullaniciID`)
    * **Tarla - Toprak Analizi:** 1 tarlanın farklı tarihlerde alınmış birden fazla toprak analizi kaydı olabilir. (`Tarlalar.TarlaID` -> `Toprak_Verileri.TarlaID`)
    * **Tarla - Hava Durumu:** 1 tarla konumu için sisteme her gün yeni bir hava durumu verisi eklenir. (`Tarlalar.TarlaID` -> `Hava_Verileri.TarlaID`)
    * **Tarla - Sistem Önerisi:** Yapay zeka, 1 tarla için zaman içerisinde birden fazla gübreleme veya ekim önerisi üretebilir. (`Tarlalar.TarlaID` -> `Sistem_Onerileri.TarlaID`)
