# Akıllı Tarım Destek Sistemi (Smart Ag-Tech)

Bu proje, çiftçilerin toprak analiz verilerini takip etmesini ve OpenWeatherMap API ile hava durumuna göre sulama planlaması yapmasını sağlar.

## 🛠 Geliştirme Ortamı Kurulumu

### 1. Gereksinimler
- **IDE:** Visual Studio Code (Önerilen eklentiler: *ESLint, Prettier, Live Server*)
- **Runtime:** Node.js (v18.x veya üzeri)
- **Paket Yöneticisi:** npm (Node.js ile birlikte gelir)

### 2. Kullanılan Kütüphaneler ve Araçlar
- **Frontend:** HTML5, CSS3, JavaScript (ES6+)
- **HTTP İstemcisi:** [Axios](https://axios-http.com/) (OpenWeatherMap API istekleri için)
- **Kullanıcı Arayüzü:** Vanilla JS ile özel yazılmış bileşenler, CSS değişkenleri ile dinamik tema.

### 3. Başlangıç
1. Projeyi bilgisayarınıza klonlayın: `git clone [repo-url]`
2. İlgili branch'e geçin.
3. Bağımlılıkları yükleyin: `npm install`
4. `.env.example` dosyasını `.env` olarak kopyalayın ve API anahtarınızı ekleyin.

### 4. Yapay Zeka (AI) Entegrasyonu
Projemiz Python tabanlı bir makine öğrenmesi motoru ve kural tabanlı bir uzman sistem barındırmaktadır.
- **Model:** `TensorFlow` ve `Keras` kullanılarak oluşturulan Sinir Ağı (Neural Network) modeli ve tarımsal ideal aralıkları değerlendiren kural motoru.
- **İletişim:** Node.js backend'i, Python makine öğrenmesi motorunu bir Flask API üzerinden tetiklemektedir.

