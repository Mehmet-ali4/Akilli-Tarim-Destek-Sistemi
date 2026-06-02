const API_BASE = "http://localhost:3000/api";
let currentTarlalar = [];

function formatDateTime(value) {
    if (!value || value === "-") return "-";
    const d = new Date(value);
    if (isNaN(d.getTime())) return value;
    return d.toLocaleString("tr-TR", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "Europe/Istanbul"
    });
}

async function apiRequest(path, options = {}) {
    const token = getToken();
    const response = await fetch(`${API_BASE}${path}`, {
        headers: {
            "Content-Type": "application/json",
            ...(token ? { "Authorization": `Bearer ${token}` } : {}),
            ...(options.headers || {})
        },
        ...options
    });

    const payload = await response.json();
    if (response.status === 401) {
        logout();
        return;
    }
    if (!response.ok) {
        throw new Error(payload.message || "İstek başarısız oldu.");
    }

    return payload;
}

function getConfidenceClass(confidence) {
    if (confidence === null || confidence === undefined) {
        return "confidence-neutral";
    }
    if (confidence >= 0.8) {
        return "confidence-high";
    }
    if (confidence >= 0.5) {
        return "confidence-medium";
    }
    return "confidence-low";
}

function formatConfidence(confidence) {
    if (confidence === null || confidence === undefined) {
        return "-";
    }
    return `%${(confidence * 100).toFixed(1)}`;
}

function renderStatus(data) {
    const statusContent = document.getElementById("status-content");

    function badge(condition, okLabel = "Çalışıyor", failLabel = "Bağlantı yok") {
        return condition
            ? `<span class="badge badge-success">${okLabel}</span>`
            : `<span class="badge badge-error">${failLabel}</span>`;
    }

    const dbOk = data.database === "connected";
    const aiOk = data.ai === "running";

    statusContent.innerHTML = `
        <div class="status-item">
            <span class="status-label">Backend</span>
            ${badge(true)}
        </div>
        <div class="status-item">
            <span class="status-label">Veritabanı</span>
            ${badge(dbOk, "Bağlı", "Bağlantı yok")}
        </div>
        <div class="status-item">
            <span class="status-label">AI Servisi</span>
            ${badge(aiOk, "Çalışıyor", "Kapalı")}
        </div>
    `;
}

function renderTarlalar(tarlalar) {
    currentTarlalar = tarlalar;

    const options = tarlalar.map((tarla) => `
        <option value="${tarla.TarlaID}">
            ${tarla.TarlaAdi} (${tarla.Ekilmis_Urun || "Ürün belirtilmedi"})
        </option>
    `).join("");

    const analysisSelect = document.getElementById("tarla-select");
    if (analysisSelect) analysisSelect.innerHTML = options;

    const recFilter = document.getElementById("rec-tarla-filter");
    if (recFilter) recFilter.innerHTML = `<option value="all">Tüm Tarlalar</option>` + options;

    const weatherSelect = document.getElementById("weather-tarla-select");
    if (weatherSelect) weatherSelect.innerHTML = `<option value="">Tarla Seç...</option>` + options;

    const gecmisSelect = document.getElementById("gecmis-tarla-select");
    if (gecmisSelect) gecmisSelect.innerHTML = `<option value="">Tarla Seç...</option>` + options;
}

// ── Hava Durumu ─────────────────────────────────────────────────────────────

function owmIconUrl(icon) {
    return `https://openweathermap.org/img/wn/${icon}@2x.png`;
}

function renderWeather(data) {
    const el = document.getElementById("weather-content");
    const { anlik: a, tahmin, tarla_adi } = data;

    const forecastCards = tahmin.map((g) => `
        <div class="forecast-card">
            <div class="forecast-day">${g.gun}</div>
            <img src="${owmIconUrl(g.ikon)}" alt="${g.durum}" class="forecast-icon">
            <div class="forecast-temp">
                <span class="temp-max">${g.max_sicaklik}°</span>
                <span class="temp-min">${g.min_sicaklik}°</span>
            </div>
            <div class="forecast-detail">${g.durum}</div>
            <div class="forecast-detail">💧 ${g.ort_nem}%  🌧 ${g.toplam_yagis}mm</div>
        </div>
    `).join("");

    el.innerHTML = `
        <div class="weather-widget">
            <div class="weather-current">
                <div class="weather-main">
                    <img src="${owmIconUrl(a.ikon)}" alt="${a.durum}" class="weather-icon-lg">
                    <div>
                        <div class="weather-city">📍 ${tarla_adi} — ${a.sehir || ""}</div>
                        <div class="weather-temp">${a.sicaklik}°C</div>
                        <div class="weather-desc">${a.durum}</div>
                    </div>
                </div>
                <div class="weather-details">
                    <div class="weather-detail-item">🌡 Hissedilen <strong>${a.hissedilen}°C</strong></div>
                    <div class="weather-detail-item">💧 Nem <strong>${a.nem}%</strong></div>
                    <div class="weather-detail-item">💨 Rüzgar <strong>${a.ruzgar_hiz} km/h</strong></div>
                    <div class="weather-detail-item">☁ Bulutluluk <strong>${a.bulutluluk}%</strong></div>
                    <div class="weather-detail-item">🌧 Yağış <strong>${a.yagis_1s} mm</strong></div>
                    <div class="weather-detail-item">🔵 Basınç <strong>${a.basinc} hPa</strong></div>
                    ${a.gunes_dogus ? `<div class="weather-detail-item">🌅 Doğuş <strong>${a.gunes_dogus}</strong></div>` : ""}
                    ${a.gunes_batis ? `<div class="weather-detail-item">🌇 Batış <strong>${a.gunes_batis}</strong></div>` : ""}
                </div>
                <div class="weather-autofill">
                    <button type="button" id="autofill-weather-btn" class="btn-autofill">
                        ⬇ Hava Verisini Analiz Formuna Aktar
                    </button>
                </div>
            </div>
            <div class="weather-forecast">
                ${forecastCards}
            </div>
        </div>
    `;

    document.getElementById("autofill-weather-btn").addEventListener("click", () => {
        const tempInput = document.getElementById("temperature");
        const humInput = document.getElementById("humidity");
        if (tempInput) tempInput.value = a.sicaklik;
        if (humInput) humInput.value = a.nem;
        document.getElementById("predict-form").scrollIntoView({ behavior: "smooth" });
    });
}

async function fetchWeather() {
    const select = document.getElementById("weather-tarla-select");
    const tarlaId = select?.value;
    const btn = document.getElementById("fetch-weather-btn");

    if (!tarlaId) {
        alert("Lütfen bir tarla seçin.");
        return;
    }

    btn.disabled = true;
    btn.textContent = "Yükleniyor...";
    document.getElementById("weather-content").innerHTML = `<p class="section-desc">Hava durumu alınıyor...</p>`;

    try {
        const payload = await apiRequest(`/tarlalar/${tarlaId}/hava`);
        renderWeather(payload.data);
    } catch (err) {
        document.getElementById("weather-content").innerHTML = `
            <p class="error-text">${err.message}</p>
        `;
    } finally {
        btn.disabled = false;
        btn.textContent = "Hava Durumunu Getir";
    }
}

const ANALYSIS_TYPE_META = {
    sulama:       { label: "Sulama",        cls: "type-sulama" },
    gubre:        { label: "Gübre/İlaç",    cls: "type-gubre" },
    sulama_gubre: { label: "Sulama + Gübre",cls: "type-sulama-gubre" },
    bitki_sagligi:{ label: "Bitki Sağlığı", cls: "type-bitki" },
    normal:       { label: "Normal",         cls: "type-normal" },
    diger:        { label: "Diğer",          cls: "type-diger" }
};

function getAnalysisBadge(analysisType) {
    const meta = ANALYSIS_TYPE_META[analysisType] || ANALYSIS_TYPE_META.diger;
    return `<span class="type-badge ${meta.cls}">${meta.label}</span>`;
}

function renderAddFieldResult(result, isError = false) {
    const panel = document.getElementById("add-field-result");
    const content = document.getElementById("add-field-result-content");

    panel.classList.remove("hidden");

    if (isError) {
        content.innerHTML = `
            <p class="error-text"><strong>Hata:</strong> ${result}</p>
        `;
    } else {
        content.innerHTML = `
            <p><strong>Tarla Başarıyla Eklendi!</strong></p>
            <p><strong>Tarla ID:</strong> ${result.TarlaID}</p>
            <p><strong>Tarla Adı:</strong> ${result.TarlaAdi}</p>
            <p><strong>Konum:</strong> ${result.Konum_Enlem}, ${result.Konum_Boylam}</p>
            ${result.Ekilmis_Urun ? `<p><strong>Ekili Ürün:</strong> ${result.Ekilmis_Urun}</p>` : ""}
        `;
    }
}

async function submitAddField(event) {
    event.preventDefault();

    const form = event.target;
    const button = document.getElementById("add-field-btn");
    button.disabled = true;
    button.textContent = "Ekleniyor...";

    try {
        const body = {
            tarla_adi: form.tarla_adi.value,
            konum_enlem: parseFloat(form.konum_enlem.value),
            konum_boylam: parseFloat(form.konum_boylam.value),
            ekilmis_urun: form.ekilmis_urun?.value || null
        };

        const token = getToken();
        const response = await fetch(`${API_BASE}/tarlalar`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                ...(token ? { "Authorization": `Bearer ${token}` } : {})
            },
            body: JSON.stringify(body)
        });

        const payload = await response.json();
        if (!response.ok) {
            throw new Error(payload.message || "Tarla ekleme başarısız oldu.");
        }

        renderAddFieldResult(payload.data);
        form.reset();

        // Tarla listesini yenile
        await loadTarlalar();
    } catch (error) {
        renderAddFieldResult(error.message, true);
    } finally {
        button.disabled = false;
        button.textContent = "Tarlayı Ekle";
    }
}

function renderResult(result) {
    const panel = document.getElementById("result-panel");
    const block = document.getElementById("sensor-result-block");
    const content = document.getElementById("sensor-result-content");
    const confidenceClass = getConfidenceClass(result.confidence);

    panel.classList.remove("hidden");
    block.classList.remove("hidden");

    const actionList = (result.actions || []);
    const actionsHtml = actionList.length
        ? actionList.map((a) => `<span class="action-tag">${a}</span>`).join(" ")
        : "<span class='action-tag action-tag-normal'>Durum Normal</span>";

    content.innerHTML = `
        <p><strong>Karar:</strong> ${result.prediction}</p>
        <p><strong>Aksiyonlar:</strong> ${actionsHtml}</p>
        <p><strong>Güven Skoru:</strong>
            <span class="confidence-badge ${confidenceClass}">${formatConfidence(result.confidence)}</span>
        </p>
        ${result.saved_records ? `
            <p class="saved-note">✓ Analiz ID: ${result.saved_records.analiz_id} &nbsp;|&nbsp; Öneri ID: ${result.saved_records.oneri_id}</p>
        ` : ""}
    `;
}

function renderRecommendations(oneriler) {
    const tbody = document.getElementById("recommendations-body");
    const tarlaFilter = document.getElementById("rec-tarla-filter");
    const typeFilter = document.getElementById("rec-type-filter");

    const selectedTarla = tarlaFilter ? tarlaFilter.value : "all";
    const selectedType = typeFilter ? typeFilter.value : "all";

    let filtered = oneriler;
    if (selectedTarla !== "all") {
        filtered = filtered.filter((o) => String(o.tarla_id) === selectedTarla);
    }
    if (selectedType !== "all") {
        filtered = filtered.filter((o) => o.analysis_type === selectedType);
    }

    if (!filtered.length) {
        tbody.innerHTML = `<tr><td colspan="6">Seçilen filtreye uygun öneri bulunamadı.</td></tr>`;
        return;
    }

    tbody.innerHTML = filtered.map((oneri) => {
        const confidenceClass = getConfidenceClass(oneri.guven_skoru);
        const actions = (oneri.aksiyonlar || []).join(" • ") || "-";
        const tarlaAdi = oneri.tarla_adi || `Tarla #${oneri.tarla_id}`;
        const typeBadge = getAnalysisBadge(oneri.analysis_type);

        const tarih = formatDateTime(oneri.olusturma_tarihi);

        return `
            <tr>
                <td><strong>${tarlaAdi}</strong></td>
                <td class="date-cell">${tarih}</td>
                <td>${typeBadge}</td>
                <td>${oneri.ozet}</td>
                <td class="actions-cell">${actions}</td>
                <td>
                    <span class="confidence-badge ${confidenceClass}">
                        ${formatConfidence(oneri.guven_skoru)}
                    </span>
                </td>
            </tr>
        `;
    }).join("");
}

async function loadStatus() {
    const payload = await apiRequest("/status");
    renderStatus(payload.data);
}

async function loadTarlalar() {
    const payload = await apiRequest("/tarlalar");
    renderTarlalar(payload.data);
    return payload.data;
}

let allOneriler = [];

async function loadRecommendations() {
    const payload = await apiRequest("/oneriler");
    allOneriler = payload.data || [];
    renderRecommendations(allOneriler);
    // Harita markerlarını güncel öneri renkleriyle yenile
    if (typeof renderMap === "function" && currentTarlalar.length) {
        renderMap(currentTarlalar, allOneriler);
    }
}

function setupImagePreview() {
    const fileInput = document.getElementById("field-image");
    const preview = document.getElementById("image-preview");
    const previewImg = document.getElementById("preview-img");

    fileInput.addEventListener("change", () => {
        const file = fileInput.files[0];
        if (!file) {
            preview.classList.add("hidden");
            return;
        }

        previewImg.src = URL.createObjectURL(file);
        preview.classList.remove("hidden");
    });
}

async function submitAnalysis(event) {
    event.preventDefault();

    const form = event.target;
    const button = document.getElementById("analyze-btn");
    const fileInput = document.getElementById("field-image");
    const file = fileInput?.files[0];

    button.disabled = true;
    button.textContent = "Analiz ediliyor...";
    clearResultPanel();

    try {
        // Eğer fotoğraf varsa, önce fotoğraf analizini yap
        if (file) {
            const formData = new FormData();
            formData.append("image", file);
            formData.append("tarla_id", form.tarla_id.value);

            const imageResponse = await fetch(`${API_BASE}/plant-health/analyze`, {
                method: "POST",
                body: formData
            });

            const imagePayload = await imageResponse.json();
            if (!imageResponse.ok) {
                throw new Error(imagePayload.message || "Görüntü analizi başarısız oldu.");
            }

            // Görüntü analiz sonucunu göster
            renderImageResult(imagePayload.data);
        }

        // Toprak verisi analizini yap
        const body = {
            tarla_id: Number(form.tarla_id.value),
            soil_moisture: Number(form.soil_moisture.value),
            temperature: Number(form.temperature.value),
            humidity: Number(form.humidity.value),
            ph_level: Number(form.ph_level.value),
            npk_degerleri: form.npk_degerleri.value || null
        };

        const response = await fetch(`${API_BASE}/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });

        const payload = await response.json();
        if (!response.ok) {
            throw new Error(payload.message || "Tahmin isteği başarısız oldu.");
        }

        renderResult(payload.data);
        await loadRecommendations();
    } catch (error) {
        alert(error.message);
    } finally {
        button.disabled = false;
        button.textContent = "Analiz Et ve Kaydet";
    }
}

function renderImageResult(result) {
    const panel = document.getElementById("result-panel");
    const block = document.getElementById("image-result-block");
    const content = document.getElementById("image-result-content");
    const healthClass = result.health_score >= 75
        ? "confidence-high"
        : result.health_score >= 50
            ? "confidence-medium"
            : "confidence-low";

    panel.classList.remove("hidden");
    block.classList.remove("hidden");

    content.innerHTML = `
        <p><strong>Sağlık Skoru:</strong>
            <span class="confidence-badge ${healthClass}">${result.health_score}/100 (${result.health_status})</span>
        </p>
        <p><strong>Hastalık Riski:</strong> ${formatConfidence(result.disease_risk)}</p>
        <p><strong>Yaprak Rengi:</strong> ${result.leaf_color}</p>
        <p><strong>Gelişim Dönemi:</strong> ${result.growth_stage_label}</p>
        <p><strong>Tahmini Hasat Tarihi:</strong> <strong>${result.estimated_harvest_date}</strong> (${result.estimated_days_to_harvest} gün)</p>
        <p><strong>Ürün Döngüsü:</strong> ${result.crop_cycle_days} gün</p>
        <p><strong>Notlar:</strong> ${(result.notes || []).join(" ")}</p>
        ${result.saved_records ? `
            <p class="saved-note">✓ Öneri ID: ${result.saved_records.oneri_id}</p>
        ` : ""}
    `;
}

function clearResultPanel() {
    document.getElementById("result-panel").classList.add("hidden");
    document.getElementById("sensor-result-block").classList.add("hidden");
    document.getElementById("image-result-block").classList.add("hidden");
    document.getElementById("sensor-result-content").innerHTML = "";
    document.getElementById("image-result-content").innerHTML = "";
}

document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("analysis-form");
    const addFieldForm = document.getElementById("add-field-form");
    const refreshButton = document.getElementById("refresh-recommendations");
    const recTarlaFilter = document.getElementById("rec-tarla-filter");
    const recTypeFilter = document.getElementById("rec-type-filter");
    const fetchWeatherBtn = document.getElementById("fetch-weather-btn");

    form.addEventListener("submit", submitAnalysis);
    if (addFieldForm) addFieldForm.addEventListener("submit", submitAddField);
    setupImagePreview();
    refreshButton.addEventListener("click", loadRecommendations);
    recTarlaFilter.addEventListener("change", () => renderRecommendations(allOneriler));
    recTypeFilter.addEventListener("change", () => renderRecommendations(allOneriler));
    if (fetchWeatherBtn) fetchWeatherBtn.addEventListener("click", fetchWeather);

    const fetchGecmisBtn = document.getElementById("fetch-gecmis-btn");
    if (fetchGecmisBtn) fetchGecmisBtn.addEventListener("click", fetchGecmis);

    const loadRaporBtn = document.getElementById("load-rapor-btn");
    if (loadRaporBtn) loadRaporBtn.addEventListener("click", loadModelRapor);

    const refreshMapBtn = document.getElementById("refresh-map-btn");
    if (refreshMapBtn) refreshMapBtn.addEventListener("click", refreshMap);

    try {
        await loadStatus();
        const tarlalar = await loadTarlalar();
        currentTarlalar = tarlalar;
        await loadRecommendations();
        // Tarlalar ve öneriler yüklendikten sonra haritayı render et
        initMap();
        renderMap(currentTarlalar, allOneriler);
    } catch (error) {
        document.getElementById("status-content").innerHTML = `
            <p class="error-text">Backend'e bağlanılamadı. Sunucunun çalıştığından emin olun.</p>
        `;
    }
});
