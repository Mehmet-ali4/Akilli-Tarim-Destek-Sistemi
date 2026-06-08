/**
 * =============================================================================
 *  Akıllı Tarım Destek Sistemi — Frontend Test Suite
 *  Modül: frontend/js/main.js
 *  Test Framework: Jest + jsdom
 *  Yazar: QA Otomasyon Mühendisi
 *  Tarih: 2026-06-08
 * =============================================================================
 *  Bu test dosyası, main.js içindeki iş mantıklarını test eder:
 *    1. Otomatik toprak nemi hesaplama formülü (sıcaklık + buharlaşma etkisi)
 *    2. Renk skalası mantığı (confidence → Yeşil/Sarı/Kırmızı eşikleri)
 *    3. Hava durumu emoji eşleştirmesi
 *    4. Şehir arama/filtreleme mantığı
 *    5. Sınır değerler (edge cases)
 * =============================================================================
 */

// =====================================================================
//  YARDIMCI FONKSİYONLARI AYIKLA (main.js'den bağımsız test edilebilir hale getir)
//  main.js DOM-bağımlı olduğu için, formülleri burada izole ediyoruz.
// =====================================================================

/**
 * Otomatik Toprak Nemi Hesaplama Formülü
 * Kaynak: main.js satır 134
 * Formül: humidity * 0.8 - (temp > 20 ? (temp - 20) * 1.5 : 0) + 10
 * Clamp: Math.min(100, Math.max(0, result))
 */
function calculateAutoToprakNemi(humidity, temp) {
    let autoToprakNemi = Math.round(humidity * 0.8 - (temp > 20 ? (temp - 20) * 1.5 : 0) + 10);
    autoToprakNemi = Math.min(100, Math.max(0, autoToprakNemi));
    return autoToprakNemi;
}

/**
 * Renk Skalası Mantığı — Confidence Score → CSS Sınıfı
 * Kaynak: main.js satır 228-234
 * confidence >= 0.75 → 'positive' (Yeşil)
 * confidence >= 0.50 → 'warning' (Sarı)
 * confidence < 0.50  → 'danger' (Kırmızı)
 */
function getConfidenceColorClass(confidence) {
    if (confidence >= 0.75) return 'positive';
    if (confidence >= 0.50) return 'warning';
    return 'danger';
}

/**
 * Confidence Factor Score → Renk Sınıfı
 * Kaynak: main.js satır 250-252
 * score >= 0.8 → 'good' (Yeşil)
 * score >= 0.5 → 'avg' (Sarı/Turuncu)
 * score < 0.5  → 'bad' (Kırmızı)
 */
function getScoreClass(score) {
    if (score >= 0.8) return 'good';
    if (score >= 0.5) return 'avg';
    return 'bad';
}

/**
 * Hava Durumu Emoji Eşleştirme
 * Kaynak: main.js satır 150-157
 */
function getWeatherEmoji(main) {
    const map = {
        'Clear': '☀️', 'Clouds': '☁️', 'Rain': '🌧️',
        'Drizzle': '🌦️', 'Thunderstorm': '⛈️', 'Snow': '❄️',
        'Mist': '🌫️', 'Fog': '🌫️', 'Haze': '🌫️'
    };
    return map[main] || '🌤️';
}

/**
 * Capitalize fonksiyonu
 * Kaynak: main.js satır 159-161
 */
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Şehir Filtreleme Mantığı
 * Kaynak: main.js satır 43
 */
const sehirler = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya", "Ankara", "Antalya", "Artvin", "Aydın", "Balıkesir",
    "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli",
    "Diyarbakır", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari",
    "Hatay", "Isparta", "Mersin", "İstanbul", "İzmir", "Kars", "Kastamonu", "Kayseri", "Kırklareli", "Kırşehir",
    "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Kahramanmaraş", "Mardin", "Muğla", "Muş", "Nevşehir",
    "Niğde", "Ordu", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Tekirdağ", "Tokat",
    "Trabzon", "Tunceli", "Şanlıurfa", "Uşak", "Van", "Yozgat", "Zonguldak", "Aksaray", "Bayburt", "Karaman",
    "Kırıkkale", "Batman", "Şırnak", "Bartın", "Ardahan", "Iğdır", "Yalova", "Karabük", "Kilis", "Osmaniye", "Düzce"
];

function filterCities(filter) {
    return sehirler.filter(s => s.toLocaleLowerCase('tr').includes(filter.toLocaleLowerCase('tr')));
}


// =====================================================================
//  1. OTOMATİK TOPRAK NEMİ HESAPLAMASI
// =====================================================================

describe('Otomatik Toprak Nemi Hesaplayıcı (calculateAutoToprakNemi)', () => {

    // --- 1.1 Normal Koşullar ---
    
    test('Normal koşullar: 25°C sıcaklık, %50 nem → beklenen sonuç', () => {
        // 50*0.8 - (25-20)*1.5 + 10 = 40 - 7.5 + 10 = 42.5 → 43
        const result = calculateAutoToprakNemi(50, 25);
        expect(result).toBe(43);
    });

    test('Normal koşullar: 20°C sıcaklık, %60 nem → buharlaşma etkisi yok', () => {
        // 60*0.8 - 0 + 10 = 48 + 10 = 58
        const result = calculateAutoToprakNemi(60, 20);
        expect(result).toBe(58);
    });

    test('Normal koşullar: 15°C sıcaklık, %70 nem → buharlaşma yok, yüksek nem', () => {
        // 70*0.8 - 0 + 10 = 56 + 10 = 66
        const result = calculateAutoToprakNemi(70, 15);
        expect(result).toBe(66);
    });

    // --- 1.2 Sıcaklık Etkisi (Buharlaşma) ---

    test('Yüksek sıcaklık: 40°C, %50 nem → ciddi buharlaşma', () => {
        // 50*0.8 - (40-20)*1.5 + 10 = 40 - 30 + 10 = 20
        const result = calculateAutoToprakNemi(50, 40);
        expect(result).toBe(20);
    });

    test('Çok yüksek sıcaklık: 50°C, %30 nem → neredeyse sıfır', () => {
        // 30*0.8 - (50-20)*1.5 + 10 = 24 - 45 + 10 = -11 → clamp → 0
        const result = calculateAutoToprakNemi(30, 50);
        expect(result).toBe(0);
    });

    test('Buharlaşma eşiği: Tam 20°C → buharlaşma 0 olmalı', () => {
        // temp > 20 koşulu false (eşit, büyük değil)
        // 50*0.8 - 0 + 10 = 40 + 10 = 50
        const result = calculateAutoToprakNemi(50, 20);
        expect(result).toBe(50);
    });

    test('Buharlaşma başlangıcı: 21°C → minimal buharlaşma', () => {
        // 50*0.8 - (21-20)*1.5 + 10 = 40 - 1.5 + 10 = 48.5 → 49
        const result = calculateAutoToprakNemi(50, 21);
        expect(result).toBe(49);
    });

    // --- 1.3 Düşük Sıcaklıklar ---

    test('Soğuk hava: 0°C, %50 nem → buharlaşma yok', () => {
        // 50*0.8 - 0 + 10 = 40 + 10 = 50
        const result = calculateAutoToprakNemi(50, 0);
        expect(result).toBe(50);
    });

    test('Don sıcaklığı: -20°C, %80 nem → buharlaşma yok, yüksek nem', () => {
        // 80*0.8 - 0 + 10 = 64 + 10 = 74
        const result = calculateAutoToprakNemi(80, -20);
        expect(result).toBe(74);
    });

    test('Aşırı soğuk: -50°C, %10 nem → düşük ama pozitif', () => {
        // 10*0.8 - 0 + 10 = 8 + 10 = 18
        const result = calculateAutoToprakNemi(10, -50);
        expect(result).toBe(18);
    });

    // --- 1.4 Ekstrem Hava Nemi ---

    test('Hava nemi %0, 25°C → minimum toprak nemi', () => {
        // 0*0.8 - (25-20)*1.5 + 10 = 0 - 7.5 + 10 = 2.5 → 3
        const result = calculateAutoToprakNemi(0, 25);
        expect(result).toBe(3);
    });

    test('Hava nemi %100, 15°C → çok yüksek toprak nemi', () => {
        // 100*0.8 - 0 + 10 = 80 + 10 = 90
        const result = calculateAutoToprakNemi(100, 15);
        expect(result).toBe(90);
    });

    test('Hava nemi %100, 0°C → maksimum korunmuş nem', () => {
        // 100*0.8 - 0 + 10 = 90
        const result = calculateAutoToprakNemi(100, 0);
        expect(result).toBe(90);
    });

    // --- 1.5 Clamp Testleri (0-100 sınırları) ---

    test('Alt sınır clamp: Sonuç negatif olduğunda 0 döndürmeli', () => {
        // 0*0.8 - (60-20)*1.5 + 10 = 0 - 60 + 10 = -50 → clamp → 0
        const result = calculateAutoToprakNemi(0, 60);
        expect(result).toBe(0);
    });

    test('Üst sınır clamp: Sonuç 100\'ü aştığında 100 döndürmeli', () => {
        // 200*0.8 - 0 + 10 = 160 + 10 = 170 → clamp → 100
        // Not: Gerçekte hava nemi %100'ü geçmez ama formül dayanıklılığını test ediyoruz
        const result = calculateAutoToprakNemi(200, 0);
        expect(result).toBe(100);
    });

    test('Tam sınırda: Sonuç tam 0 olduğunda', () => {
        // humidity*0.8 - (temp-20)*1.5 + 10 = 0
        // Bu denklemi sağlayan değerler: humidity=0, temp=26.67
        // 0*0.8 - (27-20)*1.5 + 10 = -10.5 + 10 = -0.5 → 0 (round sonrası)
        const result = calculateAutoToprakNemi(0, 27);
        expect(result).toBe(0);
    });

    test('Tam sınırda: Sonuç tam 100 olduğunda', () => {
        // 100*0.8 + 10 = 90 → 100'e ulaşamaz normal koşulda
        // Ama 112.5 humidity ile: 112.5*0.8 + 10 = 100
        const result = calculateAutoToprakNemi(113, 0);
        expect(result).toBe(100);
    });

    // --- 1.6 Yuvarlama Testleri ---

    test('Math.round yuvarlama: .5 yukarı yuvarlanır', () => {
        // 50*0.8 - (21-20)*1.5 + 10 = 40 - 1.5 + 10 = 48.5 → 49
        const result = calculateAutoToprakNemi(50, 21);
        expect(result).toBe(49);
    });

    test('Math.round yuvarlama: .4 aşağı yuvarlanır', () => {
        // Kesin hesap yapalım: 51*0.8 = 40.8, (22-20)*1.5 = 3
        // 40.8 - 3 + 10 = 47.8 → 48
        const result = calculateAutoToprakNemi(51, 22);
        expect(result).toBe(48);
    });

    // --- 1.7 Gerçekçi Hava Durumu Senaryoları ---

    test('Yaz ortası Adana: 42°C, %25 nem → kurak', () => {
        // 25*0.8 - (42-20)*1.5 + 10 = 20 - 33 + 10 = -3 → 0
        const result = calculateAutoToprakNemi(25, 42);
        expect(result).toBe(0);
    });

    test('Kış Rize: 5°C, %85 nem → nemli', () => {
        // 85*0.8 - 0 + 10 = 68 + 10 = 78
        const result = calculateAutoToprakNemi(85, 5);
        expect(result).toBe(78);
    });

    test('İlkbahar Ankara: 18°C, %45 nem → ılıman', () => {
        // 45*0.8 - 0 + 10 = 36 + 10 = 46
        const result = calculateAutoToprakNemi(45, 18);
        expect(result).toBe(46);
    });

    test('Yaz İstanbul: 30°C, %70 nem → orta', () => {
        // 70*0.8 - (30-20)*1.5 + 10 = 56 - 15 + 10 = 51
        const result = calculateAutoToprakNemi(70, 30);
        expect(result).toBe(51);
    });

    // --- 1.8 Sonuç her zaman integer olmalı ---

    test('Sonuç her zaman integer olmalı', () => {
        const testCases = [
            [50, 25], [33, 17], [77, 31], [12, 8], [99, 44]
        ];
        testCases.forEach(([humidity, temp]) => {
            const result = calculateAutoToprakNemi(humidity, temp);
            expect(Number.isInteger(result)).toBe(true);
        });
    });

    test('Sonuç her zaman 0-100 arasında olmalı (fuzz test)', () => {
        // Rastgele 50 kombinasyon dene
        for (let i = 0; i < 50; i++) {
            const humidity = Math.random() * 150 - 25;  // -25 ile 125 arası
            const temp = Math.random() * 120 - 40;       // -40 ile 80 arası
            const result = calculateAutoToprakNemi(humidity, temp);
            expect(result).toBeGreaterThanOrEqual(0);
            expect(result).toBeLessThanOrEqual(100);
        }
    });
});


// =====================================================================
//  2. RENK SKALASI MANTIK TESTLERİ
// =====================================================================

describe('Renk Skalası — Confidence → CSS Class (getConfidenceColorClass)', () => {

    // --- 2.1 Yeşil Bölge (positive) ---

    test('Confidence 1.0 → positive (Yeşil)', () => {
        expect(getConfidenceColorClass(1.0)).toBe('positive');
    });

    test('Confidence 0.85 → positive (Yeşil)', () => {
        expect(getConfidenceColorClass(0.85)).toBe('positive');
    });

    test('Confidence 0.75 → positive (Yeşil) — TAM SINIR', () => {
        expect(getConfidenceColorClass(0.75)).toBe('positive');
    });

    // --- 2.2 Sarı Bölge (warning) ---

    test('Confidence 0.74 → warning (Sarı)', () => {
        expect(getConfidenceColorClass(0.74)).toBe('warning');
    });

    test('Confidence 0.60 → warning (Sarı)', () => {
        expect(getConfidenceColorClass(0.60)).toBe('warning');
    });

    test('Confidence 0.50 → warning (Sarı) — TAM SINIR', () => {
        expect(getConfidenceColorClass(0.50)).toBe('warning');
    });

    // --- 2.3 Kırmızı Bölge (danger) ---

    test('Confidence 0.49 → danger (Kırmızı)', () => {
        expect(getConfidenceColorClass(0.49)).toBe('danger');
    });

    test('Confidence 0.20 → danger (Kırmızı)', () => {
        expect(getConfidenceColorClass(0.20)).toBe('danger');
    });

    test('Confidence 0.0 → danger (Kırmızı)', () => {
        expect(getConfidenceColorClass(0.0)).toBe('danger');
    });

    // --- 2.4 Edge Cases ---

    test('Negatif confidence → danger', () => {
        expect(getConfidenceColorClass(-0.1)).toBe('danger');
    });

    test('Confidence 1.5 (hatalı yüksek) → positive', () => {
        expect(getConfidenceColorClass(1.5)).toBe('positive');
    });
});


// =====================================================================
//  3. CONFIDENCE FACTOR SCORE → RENK SINIFI
// =====================================================================

describe('Factor Score → Renk Sınıfı (getScoreClass)', () => {

    test('Score 1.0 → good', () => {
        expect(getScoreClass(1.0)).toBe('good');
    });

    test('Score 0.80 → good — TAM SINIR', () => {
        expect(getScoreClass(0.80)).toBe('good');
    });

    test('Score 0.79 → avg', () => {
        expect(getScoreClass(0.79)).toBe('avg');
    });

    test('Score 0.50 → avg — TAM SINIR', () => {
        expect(getScoreClass(0.50)).toBe('avg');
    });

    test('Score 0.49 → bad', () => {
        expect(getScoreClass(0.49)).toBe('bad');
    });

    test('Score 0.0 → bad', () => {
        expect(getScoreClass(0.0)).toBe('bad');
    });

    test('Score 0.30 → bad (minimum model output)', () => {
        expect(getScoreClass(0.30)).toBe('bad');
    });
});


// =====================================================================
//  4. HAVA DURUMU EMOJİ EŞLEŞTİRME
// =====================================================================

describe('Hava Durumu Emoji Eşleştirme (getWeatherEmoji)', () => {

    test('Clear → ☀️', () => {
        expect(getWeatherEmoji('Clear')).toBe('☀️');
    });

    test('Clouds → ☁️', () => {
        expect(getWeatherEmoji('Clouds')).toBe('☁️');
    });

    test('Rain → 🌧️', () => {
        expect(getWeatherEmoji('Rain')).toBe('🌧️');
    });

    test('Drizzle → 🌦️', () => {
        expect(getWeatherEmoji('Drizzle')).toBe('🌦️');
    });

    test('Thunderstorm → ⛈️', () => {
        expect(getWeatherEmoji('Thunderstorm')).toBe('⛈️');
    });

    test('Snow → ❄️', () => {
        expect(getWeatherEmoji('Snow')).toBe('❄️');
    });

    test('Mist → 🌫️', () => {
        expect(getWeatherEmoji('Mist')).toBe('🌫️');
    });

    test('Fog → 🌫️', () => {
        expect(getWeatherEmoji('Fog')).toBe('🌫️');
    });

    test('Haze → 🌫️', () => {
        expect(getWeatherEmoji('Haze')).toBe('🌫️');
    });

    test('Bilinmeyen durum → 🌤️ (default)', () => {
        expect(getWeatherEmoji('Tornado')).toBe('🌤️');
    });

    test('Boş string → 🌤️ (default)', () => {
        expect(getWeatherEmoji('')).toBe('🌤️');
    });

    test('null → 🌤️ (default, undefined key)', () => {
        expect(getWeatherEmoji(null)).toBe('🌤️');
    });

    test('Küçük harf "clear" → default (case-sensitive)', () => {
        expect(getWeatherEmoji('clear')).toBe('🌤️');
    });
});


// =====================================================================
//  5. CAPITALIZE FONKSİYONU
// =====================================================================

describe('Capitalize Fonksiyonu', () => {

    test('Normal string capitalize', () => {
        expect(capitalize('açık')).toBe('Açık');
    });

    test('Zaten büyük harf ile başlıyor', () => {
        expect(capitalize('Bulutlu')).toBe('Bulutlu');
    });

    test('Tek karakter', () => {
        expect(capitalize('a')).toBe('A');
    });

    test('Sayı ile başlıyor', () => {
        expect(capitalize('5gün')).toBe('5gün');
    });

    test('Boş string', () => {
        // charAt(0) = '' → ''.toUpperCase() = '' → '' + '' = ''
        expect(capitalize('')).toBe('');
    });
});


// =====================================================================
//  6. ŞEHİR FİLTRELEME MANTIĞI
// =====================================================================

describe('Şehir Filtreleme (filterCities)', () => {

    test('Boş filtre → 81 il döndürmeli', () => {
        const result = filterCities('');
        expect(result.length).toBe(81);
    });

    test('"Ankara" araması → sadece Ankara', () => {
        const result = filterCities('Ankara');
        expect(result).toContain('Ankara');
        expect(result.length).toBe(1);
    });

    test('"ist" araması → İstanbul', () => {
        const result = filterCities('ist');
        expect(result).toContain('İstanbul');
    });

    test('"an" araması → birden fazla sonuç (Adana, Ankara, Antalya, vs.)', () => {
        const result = filterCities('an');
        expect(result.length).toBeGreaterThan(1);
        expect(result).toContain('Ankara');
        expect(result).toContain('Antalya');
    });

    test('Büyük/küçük harf duyarsız: "ANKARA" → Ankara bulunmalı', () => {
        const result = filterCities('ANKARA');
        expect(result).toContain('Ankara');
    });

    test('Varolmayan şehir: "XYZ" → boş dizi', () => {
        const result = filterCities('XYZ');
        expect(result.length).toBe(0);
    });

    test('Türkçe karakter: "ş" araması → Şanlıurfa, Şırnak, Eskişehir, vs.', () => {
        const result = filterCities('ş');
        expect(result.length).toBeGreaterThan(0);
    });

    test('Kısmi eşleşme: "kara" → Afyonkarahisar, Karabük, Karaman, vs.', () => {
        const result = filterCities('kara');
        expect(result.length).toBeGreaterThan(1);
    });
});


// =====================================================================
//  7. TOPRAK NEMİ FORMÜLÜ — MATEMATİKSEL DOĞRULUK
// =====================================================================

describe('Toprak Nemi Formülü — Matematiksel Doğrulama', () => {

    test('Buharlaşma etkisi sıcaklıkla doğru orantılı', () => {
        const humidity = 60;
        const result20 = calculateAutoToprakNemi(humidity, 20);
        const result30 = calculateAutoToprakNemi(humidity, 30);
        const result40 = calculateAutoToprakNemi(humidity, 40);
        
        // Sıcaklık arttıkça toprak nemi düşmeli
        expect(result20).toBeGreaterThanOrEqual(result30);
        expect(result30).toBeGreaterThanOrEqual(result40);
    });

    test('Hava nemi toprak nemiyle doğru orantılı', () => {
        const temp = 25;
        const result30 = calculateAutoToprakNemi(30, temp);
        const result60 = calculateAutoToprakNemi(60, temp);
        const result90 = calculateAutoToprakNemi(90, temp);
        
        // Hava nemi arttıkça toprak nemi de artmalı
        expect(result30).toBeLessThanOrEqual(result60);
        expect(result60).toBeLessThanOrEqual(result90);
    });

    test('20°C altında sıcaklık değişimi toprak nemini etkilememeli', () => {
        const humidity = 60;
        const result0 = calculateAutoToprakNemi(humidity, 0);
        const result10 = calculateAutoToprakNemi(humidity, 10);
        const result20 = calculateAutoToprakNemi(humidity, 20);
        
        // 20°C ve altında hepsi aynı olmalı (buharlaşma etkisi yok)
        expect(result0).toBe(result10);
        expect(result10).toBe(result20);
    });

    test('Buharlaşma katsayısı doğru: her 1°C artış (>20°C) → 1.5 birim düşüş', () => {
        const humidity = 60;
        const base = calculateAutoToprakNemi(humidity, 20);
        const plus5 = calculateAutoToprakNemi(humidity, 25);
        
        // 5°C fark → 5*1.5 = 7.5 → round etkisiyle 7-8 fark
        const diff = base - plus5;
        expect(diff).toBeGreaterThanOrEqual(7);
        expect(diff).toBeLessThanOrEqual(8);
    });

    test('Hava nemi katsayısı doğru: her %10 artış → 8 birim artış', () => {
        const temp = 15; // buharlaşma yok
        const result50 = calculateAutoToprakNemi(50, temp);
        const result60 = calculateAutoToprakNemi(60, temp);
        
        // 10 * 0.8 = 8
        expect(result60 - result50).toBe(8);
    });
});


// =====================================================================
//  8. RENK SKALASI — TUTARLILIK ve GEÇİŞ NOKTALARI
// =====================================================================

describe('Renk Skalası — Geçiş Noktaları Hassasiyet Testi', () => {

    test('0.749 ve 0.750 arasındaki geçiş → warning → positive', () => {
        expect(getConfidenceColorClass(0.749)).toBe('warning');
        expect(getConfidenceColorClass(0.750)).toBe('positive');
    });

    test('0.499 ve 0.500 arasındaki geçiş → danger → warning', () => {
        expect(getConfidenceColorClass(0.499)).toBe('danger');
        expect(getConfidenceColorClass(0.500)).toBe('warning');
    });

    test('Tam sınırlarda doğru sınıf (0.0, 0.5, 0.75, 1.0)', () => {
        expect(getConfidenceColorClass(0.0)).toBe('danger');
        expect(getConfidenceColorClass(0.5)).toBe('warning');
        expect(getConfidenceColorClass(0.75)).toBe('positive');
        expect(getConfidenceColorClass(1.0)).toBe('positive');
    });

    test('Kayan nokta hassasiyeti: 0.7499999999 → warning', () => {
        expect(getConfidenceColorClass(0.7499999999)).toBe('warning');
    });

    test('Kayan nokta hassasiyeti: 0.7500000001 → positive', () => {
        expect(getConfidenceColorClass(0.7500000001)).toBe('positive');
    });
});


// =====================================================================
//  9. TOPRAK NEMİ — EDGE CASE'LER VE DAYANIKLILIK
// =====================================================================

describe('Toprak Nemi — Edge Cases ve Dayanıklılık', () => {

    test('Infinity sıcaklık → 0 (clamp)', () => {
        const result = calculateAutoToprakNemi(50, Infinity);
        expect(result).toBe(0);
    });

    test('Negatif infinity sıcaklık → buharlaşma yok, normal hesap', () => {
        // -Infinity > 20 false → buharlaşma etkisi yok
        // 50*0.8 + 10 = 50
        const result = calculateAutoToprakNemi(50, -Infinity);
        expect(result).toBe(50);
    });

    test('Infinity nem → 100 (clamp)', () => {
        const result = calculateAutoToprakNemi(Infinity, 25);
        expect(result).toBe(100);
    });

    test('Her iki parametre 0 → minimum baz değer (10)', () => {
        // 0*0.8 - 0 + 10 = 10
        const result = calculateAutoToprakNemi(0, 0);
        expect(result).toBe(10);
    });

    test('Negatif nem → düşük sonuç ama clamp ile 0 minimum', () => {
        // -50*0.8 + 10 = -40 + 10 = -30 → clamp → 0
        const result = calculateAutoToprakNemi(-50, 10);
        expect(result).toBe(0);
    });
});
