# 🌾 Akıllı Tarım Destek Sistemi

Yapay zeka ve anlık hava durumu verilerini birleştirerek çiftçilere **sulama, gübreleme ve bitki sağlığı** konularında kişiselleştirilmiş öneriler sunan karar destek sistemidir. Türkiye'nin 81 ili ve 20 farklı tarım ürünü için optimize edilmiştir.

---

## ✨ Öne Çıkan Özellikler

| Özellik | Açıklama |
|---------|----------|
| 🧠 **8-Parametreli AI Tahmin Motoru** | Sıcaklık, nem, toprak nemi, pH, azot, fosfor, potasyum ve bitki sağlığı verilerini değerlendiren Keras sinir ağı + kural-tabanlı uzman sistem |
| 🌡️ **Akıllı Toprak Nemi Hesaplayıcı** | Sıcaklık ve buharlaşma etkisine duyarlı otomatik toprak nemi simülasyonu — hava durumu verisinden anında hesaplama |
| 🎨 **Renk Skalalı Güven Arayüzü** | Genel uygunluk skoru (overall_score) ve parametre bazlı confidence kırılımı ile Yeşil → Sarı → Kırmızı görsel geri bildirim |
| 🌦️ **Anlık Hava Durumu Entegrasyonu** | OpenWeatherMap API ile seçilen şehrin güncel sıcaklık ve nem verilerini otomatik çekme |
| 🛡️ **Girdi Doğrulama & Güvenli Aralık** | Tüm 8 parametre için fiziksel sınır kontrolü (clamp) ve anlamlı hata mesajları |
| 📋 **Detaylı Tarımsal Öneriler** | Ürün bazlı gübreleme tavsiyeleri, sulama kararı ve don/sıcaklık uyarıları |

---

## 🛠️ Teknoloji Yığını

**Yapay Zeka & Backend**

| Teknoloji | Kullanım |
|-----------|----------|
| Python 3.11 | AI servis dili |
| TensorFlow / Keras | Derin öğrenme modeli |
| Flask | AI API servisi |
| NumPy | Veri işleme |
| Node.js / Express | Backend API gateway |
| Axios | Servisler arası iletişim |

**Frontend**

| Teknoloji | Kullanım |
|-----------|----------|
| HTML5 | Sayfa yapısı |
| CSS3 | Glassmorphism UI tasarımı |
| JavaScript (Vanilla) | İş mantığı ve API iletişimi |

---

## 📁 Proje Yapısı

```
Akilli-Tarim-Destek-Sistemi/
│
├── ai_engine/                # 🧠 Yapay Zeka Motoru
│   ├── predict.py            #    Flask API + Keras model + kural-tabanlı analiz
│   ├── tarim_modeli.keras    #    Eğitilmiş model dosyası
│   ├── requirements.txt      #    Python bağımlılıkları
│   └── test_predict.py       #    AI engine test suite (87 test)
│
├── backend/                  # ⚙️ Node.js API Gateway
│   ├── server.js             #    Express sunucu — AI servisi ile köprü
│   └── package.json          #    Node.js bağımlılıkları
│
├── frontend/                 # 🎨 Kullanıcı Arayüzü
│   ├── index.html            #    Ana sayfa
│   ├── css/style.css         #    Glassmorphism stil dosyası
│   ├── js/main.js            #    İş mantığı (toprak nemi hesaplama, renk skalası)
│   └── js/main.test.js       #    Frontend test suite (84 test)
│
├── docs/                     # 📚 Proje Dokümantasyonu
├── .env                      #    Ortam değişkenleri (API anahtarları)
├── TEST_RAPORU.md            #    Detaylı test raporu
└── README.md                 #    ← Buradasınız
```

---

## 🚀 Kurulum ve Çalıştırma

### Ön Gereksinimler

- **Python** 3.10+
- **Node.js** 18+
- **npm** 9+

### 1 → Projeyi klonlayın

```bash
git clone https://github.com/Mehmet-ali4/Akilli-Tarim-Destek-Sistemi.git
cd Akilli-Tarim-Destek-Sistemi
```

### 2 → AI Engine'i başlatın

```bash
cd ai_engine
pip install -r requirements.txt
python predict.py
```
> AI servisi `http://localhost:5000` adresinde çalışacaktır.

### 3 → Backend'i başlatın

Yeni bir terminal açın:

```bash
cd backend
npm install
node server.js
```
> Backend `http://localhost:3000` adresinde çalışacaktır.

### 4 → Frontend'i açın

`frontend/index.html` dosyasını tarayıcınızda açın veya bir Live Server ile sunun.

---

## 🧪 Testler

Proje **171 otomatik test** ile korunmaktadır.

```bash
# AI Engine testleri (Python — pytest)
cd ai_engine
python -m pytest test_predict.py -v

# Frontend testleri (JavaScript — Jest)
cd frontend
npm install
npx jest --verbose
```

| Modül | Framework | Test Sayısı | Durum |
|-------|-----------|:-----------:|:-----:|
| AI Engine | pytest | 87 | ✅ |
| Frontend | Jest | 84 | ✅ |

Detaylı test kapsamı için → [`TEST_RAPORU.md`](TEST_RAPORU.md)

---

## 👥 Geliştirici Ekip

| İsim | Rol |
|------|-----|
| **Mehmet Ali KIRAÇÇAKALI** | Geliştirici |
| **Meryem ABDURRAHMAN** | Geliştirici |
| **Kaan Mert KEKLİK** | Geliştirici |
| **Ceylan DAĞILMA** | Geliştirici |
| **Arda Özcan ÇİFCİ** | Geliştirici |
| **Melik Buğra KARA** | Geliştirici |
---

## 📄 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.
