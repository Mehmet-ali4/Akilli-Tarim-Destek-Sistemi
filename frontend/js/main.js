document.addEventListener("DOMContentLoaded", () => {
    console.log("Akıllı Tarım Destek Sistemi - Frontend Hazır.");

    // ===== 81 İller Listesi =====
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

    // ===== Slider Value Updates =====
    const sliders = [
        { id: 'toprak_nemi', valId: 'toprak-nemi-val', suffix: '' },
        { id: 'ph', valId: 'ph-val', suffix: '' },
        { id: 'nitrojen', valId: 'nitrojen-val', suffix: '' },
        { id: 'fosfor', valId: 'fosfor-val', suffix: '' },
        { id: 'potasyum', valId: 'potasyum-val', suffix: '' },
        { id: 'bitki_sagligi', valId: 'bitki-sagligi-val', suffix: '' }
    ];

    sliders.forEach(s => {
        const slider = document.getElementById(s.id);
        const valDisplay = document.getElementById(s.valId);
        if (slider && valDisplay) {
            slider.addEventListener('input', () => {
                valDisplay.textContent = slider.value + s.suffix;
            });
        }
    });

    // ===== City Search Dropdown =====
    const sehirInput = document.getElementById('sehir-input');
    const cityDropdown = document.getElementById('city-dropdown');
    let currentCity = "";

    function renderCityList(filter = "") {
        cityDropdown.innerHTML = '';
        const filtered = sehirler.filter(s => s.toLocaleLowerCase('tr').includes(filter.toLocaleLowerCase('tr')));
        
        if (filtered.length === 0) {
            const noRes = document.createElement('div');
            noRes.className = 'search-item no-result';
            noRes.textContent = 'Sonuç bulunamadı';
            cityDropdown.appendChild(noRes);
            return;
        }

        filtered.forEach(sehir => {
            const div = document.createElement('div');
            div.className = 'search-item';
            div.textContent = sehir;
            div.addEventListener('mousedown', () => { // click yerine mousedown çünkü blur önce tetikleniyor
                sehirInput.value = sehir;
                cityDropdown.classList.remove('show');
                currentCity = sehir;
                fetchWeather(sehir);
            });
            cityDropdown.appendChild(div);
        });
    }

    sehirInput.addEventListener('focus', () => {
        renderCityList(sehirInput.value);
        cityDropdown.classList.add('show');
    });

    sehirInput.addEventListener('input', (e) => {
        renderCityList(e.target.value);
    });

    sehirInput.addEventListener('blur', () => {
        cityDropdown.classList.remove('show');
    });

    // ===== Weather API & Auto-Soil Moisture =====
    const WEATHER_API_KEY = '48ef722bd039d1a2e28624068fe56138';
    const weatherLabel = document.getElementById('weather-label');
    const weatherDetail = document.getElementById('weather-detail');
    const weatherIcon = document.querySelector('.weather-icon');
    
    let currentWeather = { sicaklik: 25, nem: 50 };

    async function fetchWeather(city) {
        if (!city) return;
        try {
            weatherDetail.textContent = 'Yükleniyor...';
            
            // 1. Önce sehrin kesin koordinatlarını (lat, lon) Geocoding API ile alalım
            // Bu yöntem Google vb. servislerle uyuşmazlığı (İl merkezi yerine ilçe/kırsal koordinatı gelmesi) çözer
            const geoUrl = `https://api.openweathermap.org/geo/1.0/direct?q=${encodeURIComponent(city)},TR&limit=1&appid=${WEATHER_API_KEY}`;
            const geoRes = await fetch(geoUrl);
            const geoData = await geoRes.json();
            
            if (!geoRes.ok || !geoData || geoData.length === 0) {
                weatherLabel.textContent = `Anlık Hava — ${city}`;
                weatherDetail.textContent = 'Şehir bulunamadı';
                weatherIcon.textContent = '❓';
                return;
            }
            
            const lat = geoData[0].lat;
            const lon = geoData[0].lon;

            // 2. Koordinatlarla hava durumunu çekelim
            const url = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${WEATHER_API_KEY}&units=metric&lang=tr`;
            const res = await fetch(url);

            if (!res.ok) {
                weatherLabel.textContent = `Anlık Hava — ${city}`;
                weatherDetail.textContent = 'Hava durumu bulunamadı';
                weatherIcon.textContent = '❓';
                return;
            }

            const data = await res.json();
            const temp = Math.round(data.main.temp);
            const humidity = data.main.humidity;
            const desc = data.weather[0].description;
            const icon = getWeatherEmoji(data.weather[0].main);

            currentWeather = { sicaklik: temp, nem: humidity };
            weatherIcon.textContent = icon;
            weatherLabel.textContent = `Anlık Hava — ${city}`;
            weatherDetail.textContent = `${temp}°C | Nem: %${humidity} | ${capitalize(desc)}`;

            // Otomatik toprak nemi ayarı (sıcaklık ve hava nemi bazlı daha gerçekçi bir simülasyon)
            // Yüksek sıcaklık buharlaşmayı artırır (toprak nemini düşürür), yüksek hava nemi ise nemi korur.
            // Kullanıcı bu değeri yine manuel değiştirebilir
            let autoToprakNemi = Math.round(humidity * 0.8 - (temp > 20 ? (temp - 20) * 1.5 : 0) + 10);
            autoToprakNemi = Math.min(100, Math.max(0, autoToprakNemi));
            const tnSlider = document.getElementById('toprak_nemi');
            const tnVal = document.getElementById('toprak-nemi-val');
            tnSlider.value = autoToprakNemi;
            tnVal.textContent = autoToprakNemi;
            
            console.log(`Hava nemi: %${humidity} -> Otomatik Toprak Nemi: %${autoToprakNemi}`);

        } catch (err) {
            console.error('Hava durumu hatası:', err);
            weatherDetail.textContent = 'Bağlantı hatası';
            weatherIcon.textContent = '⚠️';
        }
    }

    function getWeatherEmoji(main) {
        const map = {
            'Clear': '☀️', 'Clouds': '☁️', 'Rain': '🌧️',
            'Drizzle': '🌦️', 'Thunderstorm': '⛈️', 'Snow': '❄️',
            'Mist': '🌫️', 'Fog': '🌫️', 'Haze': '🌫️'
        };
        return map[main] || '🌤️';
    }

    function capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    // ===== Form Submission =====
    const form = document.getElementById('predict-form');
    const btnAnalyze = document.getElementById('btn-analyze');
    const placeholder = document.getElementById('results-placeholder');
    const resultContent = document.getElementById('result-content');

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (!currentCity) {
                alert("Lütfen önce listeden bir şehir seçin.");
                return;
            }

            btnAnalyze.classList.add('loading');

            const data = {
                urun: document.getElementById('urun-tipi').value,
                sicaklik: currentWeather.sicaklik,
                nem: currentWeather.nem,
                toprak_nemi: parseFloat(document.getElementById('toprak_nemi').value),
                ph: parseFloat(document.getElementById('ph').value),
                nitrojen: parseFloat(document.getElementById('nitrojen').value),
                fosfor: parseFloat(document.getElementById('fosfor').value),
                potasyum: parseFloat(document.getElementById('potasyum').value),
                bitki_sagligi: parseFloat(document.getElementById('bitki_sagligi').value)
            };

            try {
                const response = await fetch('http://localhost:3000/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    throw new Error("Sunucu hatası: " + response.status);
                }

                const result = await response.json();

                if (result.error) {
                    showError(result.error);
                } else {
                    showResults(result, data);
                }
            } catch (err) {
                console.error(err);
                showError(err.message);
            } finally {
                btnAnalyze.classList.remove('loading');
            }
        });
    }

    function showResults(result, inputData) {
        placeholder.style.display = 'none';
        resultContent.classList.add('visible');

        // 1. Genel Değerlendirme Özeti
        const ozetEl = document.getElementById('res-ozet');
        ozetEl.textContent = result.ozet || result.prediction;
        ozetEl.className = 'result-value';
        // Genel uygunluk skoruna göre renklendirme (yüksek = iyi koşullar)
        if (result.confidence >= 0.75) {
            ozetEl.classList.add('positive');
        } else if (result.confidence >= 0.50) {
            ozetEl.classList.add('warning');
        } else {
            ozetEl.classList.add('danger');
        }

        // 2. Güven Skoru & Kırılımı (Confidence Breakdown)
        const confPercent = Math.round(result.confidence * 100);
        document.getElementById('res-confidence-text').textContent = `%${confPercent} Genel Uygunluk Skoru`;
        const barFill = document.getElementById('confidence-bar-fill');
        barFill.style.width = '0%';
        setTimeout(() => { barFill.style.width = confPercent + '%'; }, 100);

        const breakdownDiv = document.getElementById('confidence-breakdown');
        breakdownDiv.innerHTML = '';
        if (result.confidence_factors && result.confidence_factors.length > 0) {
            result.confidence_factors.forEach(f => {
                const item = document.createElement('div');
                item.className = 'breakdown-item';
                
                let scoreClass = 'bad';
                if (f.score >= 0.8) scoreClass = 'good';
                else if (f.score >= 0.5) scoreClass = 'avg';
                
                item.innerHTML = `<span>${f.factor}</span> <span class="score ${scoreClass}">%${Math.round(f.score * 100)}</span>`;
                breakdownDiv.appendChild(item);
            });
        }

        // 3. Hava Durumu Bilgisi
        document.getElementById('res-weather').textContent = `${currentCity}: ${currentWeather.sicaklik}°C, Nem: %${currentWeather.nem}`;

        // 4. Seçili Ürün
        document.getElementById('res-crop').textContent = result.urun_ad || document.getElementById('urun-tipi').value;

        // 5. Uyarılar
        const warningBox = document.getElementById('warnings-section');
        const warningsDiv = document.getElementById('res-warnings');
        if (result.warnings && result.warnings.length > 0) {
            warningBox.style.display = 'block';
            warningsDiv.innerHTML = `<ul class="warning-list">${result.warnings.map(w => `<li>${w}</li>`).join('')}</ul>`;
        } else {
            warningBox.style.display = 'none';
        }

        // 6. Gübreleme Tavsiyeleri
        const gubreDiv = document.getElementById('res-gubre');
        if (result.gubre_tavsiyeleri && result.gubre_tavsiyeleri.length > 0) {
            gubreDiv.innerHTML = `<ul class="fertilizer-list">${result.gubre_tavsiyeleri.map(g => `<li>${g}</li>`).join('')}</ul>`;
        } else {
            gubreDiv.textContent = "Mevcut besin değerleri yeterli görünmektedir.";
        }

        // 7. Genel Öneriler
        const recDiv = document.getElementById('res-recommendation');
        if (result.recommendations && result.recommendations.length > 0) {
            recDiv.innerHTML = `<ul style="list-style-type:none; padding:0; margin:0; line-height:1.6;">${result.recommendations.map(r => `<li style="margin-bottom:6px;">🔹 ${r}</li>`).join('')}</ul>`;
        } else {
            recDiv.textContent = "Mevcut koşullar idealdir.";
        }


    }

    function showError(message) {
        placeholder.style.display = 'none';
        resultContent.classList.add('visible');
        document.getElementById('res-ozet').textContent = 'Hata: ' + message;
        document.getElementById('res-ozet').className = 'result-value danger';
        document.getElementById('res-confidence-text').textContent = '—';
        document.getElementById('confidence-bar-fill').style.width = '0%';
        document.getElementById('res-weather').textContent = '—';
        document.getElementById('res-crop').textContent = '—';
        document.getElementById('res-recommendation').textContent = 'Lütfen AI servisinin çalıştığından emin olun ve tekrar deneyin.';
        document.getElementById('warnings-section').style.display = 'none';
    }
});
