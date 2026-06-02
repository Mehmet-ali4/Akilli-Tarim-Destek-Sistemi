const OWM_BASE = 'https://api.openweathermap.org/data/2.5';

/**
 * Belirli koordinatlar için anlık hava durumunu getirir.
 */
async function fetchCurrentWeather(lat, lon, apiKey) {
    const url = `${OWM_BASE}/weather?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric&lang=tr`;
    const res = await fetch(url, { signal: AbortSignal.timeout(8000) });

    if (!res.ok) {
        const body = await res.text();
        throw new Error(`OpenWeatherMap hatası (${res.status}): ${body}`);
    }

    const data = await res.json();
    return parseCurrentWeather(data);
}

/**
 * 5 günlük / 3 saatlik tahmin getirir (ilk 4 zaman dilimi = yaklaşık 24 saat).
 * Günlere gruplandırılmış 3 günlük özet döner.
 */
async function fetchForecast(lat, lon, apiKey) {
    const url = `${OWM_BASE}/forecast?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric&lang=tr&cnt=24`;
    const res = await fetch(url, { signal: AbortSignal.timeout(8000) });

    if (!res.ok) {
        const body = await res.text();
        throw new Error(`OpenWeatherMap tahmin hatası (${res.status}): ${body}`);
    }

    const data = await res.json();
    return parseForecast(data.list);
}

function parseCurrentWeather(data) {
    return {
        sehir: data.name,
        sicaklik: Math.round(data.main.temp),
        hissedilen: Math.round(data.main.feels_like),
        nem: data.main.humidity,
        basinc: data.main.pressure,
        ruzgar_hiz: Math.round((data.wind?.speed || 0) * 3.6), // m/s → km/h
        gorunurluk: data.visibility ? Math.round(data.visibility / 1000) : null,
        durum: data.weather[0]?.description || '',
        ikon: data.weather[0]?.icon || '01d',
        yagis_1s: data.rain?.['1h'] || data.rain?.['3h'] || 0,
        bulutluluk: data.clouds?.all || 0,
        gunes_dogus: data.sys?.sunrise ? new Date(data.sys.sunrise * 1000).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Istanbul' }) : null,
        gunes_batis: data.sys?.sunset ? new Date(data.sys.sunset * 1000).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Istanbul' }) : null,
    };
}

function parseForecast(list) {
    const gunler = {};

    for (const item of list) {
        const tarih = new Date(item.dt * 1000)
            .toLocaleDateString('tr-TR', { weekday: 'short', month: 'short', day: 'numeric', timeZone: 'Europe/Istanbul' });

        if (!gunler[tarih]) {
            gunler[tarih] = { sicakliklar: [], nemler: [], yagislar: [], ikonlar: [], durumlar: [] };
        }

        gunler[tarih].sicakliklar.push(item.main.temp);
        gunler[tarih].nemler.push(item.main.humidity);
        gunler[tarih].yagislar.push(item.rain?.['3h'] || 0);
        gunler[tarih].ikonlar.push(item.weather[0]?.icon || '01d');
        gunler[tarih].durumlar.push(item.weather[0]?.description || '');
    }

    return Object.entries(gunler).slice(0, 3).map(([gun, v]) => ({
        gun,
        max_sicaklik: Math.round(Math.max(...v.sicakliklar)),
        min_sicaklik: Math.round(Math.min(...v.sicakliklar)),
        ort_nem: Math.round(v.nemler.reduce((a, b) => a + b, 0) / v.nemler.length),
        toplam_yagis: Math.round(v.yagislar.reduce((a, b) => a + b, 0) * 10) / 10,
        ikon: v.ikonlar[Math.floor(v.ikonlar.length / 2)],
        durum: v.durumlar[Math.floor(v.durumlar.length / 2)],
    }));
}

module.exports = { fetchCurrentWeather, fetchForecast };
