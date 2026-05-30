let leafletMap = null;
let markerLayer = null;

const ONERI_RENK = {
    sulama:        { color: "#2196f3", emoji: "💧" },
    gubre:         { color: "#ff9800", emoji: "🌿" },
    sulama_gubre:  { color: "#9c27b0", emoji: "💧🌿" },
    bitki_sagligi: { color: "#4caf50", emoji: "🍃" },
    normal:        { color: "#4caf50", emoji: "✅" },
    diger:         { color: "#9e9e9e", emoji: "📍" }
};

function resolveMarkerColor(tarlalar, oneriler) {
    // Her tarla için en son öneri türüne göre renk belirle
    const renkMap = {};
    for (const tarla of tarlalar) {
        renkMap[tarla.TarlaID] = "diger";
    }
    // En son öneri (oneriler zaten DESC sıralı geliyor)
    for (const o of oneriler) {
        if (renkMap[o.tarla_id] === "diger") {
            renkMap[o.tarla_id] = o.analysis_type || "diger";
        }
    }
    return renkMap;
}

function makeMarkerIcon(type) {
    const meta = ONERI_RENK[type] || ONERI_RENK.diger;
    const svg = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 42" width="32" height="42">
            <path d="M16 0 C7.16 0 0 7.16 0 16 C0 28 16 42 16 42 C16 42 32 28 32 16 C32 7.16 24.84 0 16 0Z"
                  fill="${meta.color}" stroke="white" stroke-width="2"/>
            <text x="16" y="21" font-size="13" text-anchor="middle" dominant-baseline="middle">${meta.emoji}</text>
        </svg>`;

    return L.divIcon({
        html: svg,
        className: "",
        iconSize: [32, 42],
        iconAnchor: [16, 42],
        popupAnchor: [0, -44]
    });
}

function buildPopupHtml(tarla, analysisType) {
    const meta = ONERI_RENK[analysisType] || ONERI_RENK.diger;
    const urun = tarla.Ekilmis_Urun || "Belirtilmedi";
    const lat  = parseFloat(tarla.Konum_Enlem).toFixed(5);
    const lon  = parseFloat(tarla.Konum_Boylam).toFixed(5);

    return `
        <div class="map-popup">
            <div class="popup-title">${tarla.TarlaAdi}</div>
            <div class="popup-row">🌾 <strong>Ürün:</strong> ${urun}</div>
            <div class="popup-row">📍 <strong>Konum:</strong> ${lat}, ${lon}</div>
            <div class="popup-row">
                <strong>Son Durum:</strong>
                <span style="color:${meta.color};font-weight:bold">${meta.emoji} ${analysisType}</span>
            </div>
            <div class="popup-actions">
                <button onclick="document.getElementById('tarla-select').value='${tarla.TarlaID}';
                                 document.getElementById('predict-form').scrollIntoView({behavior:'smooth'})"
                        class="popup-btn">Analiz Et</button>
                <button onclick="document.getElementById('weather-tarla-select').value='${tarla.TarlaID}';
                                 document.getElementById('weather-section').scrollIntoView({behavior:'smooth'})"
                        class="popup-btn">Hava Durumu</button>
            </div>
        </div>
    `;
}

function initMap() {
    if (leafletMap) return;

    leafletMap = L.map("tarla-map", { zoomControl: true }).setView([39.0, 35.0], 6);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 18
    }).addTo(leafletMap);

    markerLayer = L.layerGroup().addTo(leafletMap);
}

function renderMap(tarlalar, oneriler) {
    if (!leafletMap) initMap();

    // Haritayı zorla yeniden boyutlandır (gizliyken oluşturulduysa)
    setTimeout(() => leafletMap.invalidateSize(), 100);

    markerLayer.clearLayers();

    if (!tarlalar || tarlalar.length === 0) return;

    const renkMap = resolveMarkerColor(tarlalar, oneriler || []);
    const bounds = [];

    for (const tarla of tarlalar) {
        const lat = parseFloat(tarla.Konum_Enlem);
        const lon = parseFloat(tarla.Konum_Boylam);

        if (isNaN(lat) || isNaN(lon)) continue;

        const analysisType = renkMap[tarla.TarlaID] || "diger";
        const marker = L.marker([lat, lon], { icon: makeMarkerIcon(analysisType) });
        marker.bindPopup(buildPopupHtml(tarla, analysisType), { maxWidth: 240 });
        markerLayer.addLayer(marker);
        bounds.push([lat, lon]);
    }

    if (bounds.length === 1) {
        leafletMap.setView(bounds[0], 13);
    } else if (bounds.length > 1) {
        leafletMap.fitBounds(bounds, { padding: [40, 40] });
    }
}

// main.js'ten çağrılacak
function refreshMap() {
    if (!currentTarlalar || currentTarlalar.length === 0) return;
    renderMap(currentTarlalar, allOneriler);
    document.getElementById("map-section").scrollIntoView({ behavior: "smooth" });
}
