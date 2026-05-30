// Aktif Chart örneklerini takip eder (yeniden render'da destroy için)
const activeCharts = {};

function destroyChart(id) {
    if (activeCharts[id]) {
        activeCharts[id].destroy();
        delete activeCharts[id];
    }
}

function createLineChart(canvasId, labels, datasets, yLabel) {
    destroyChart(canvasId);
    const ctx = document.getElementById(canvasId).getContext("2d");
    activeCharts[canvasId] = new Chart(ctx, {
        type: "line",
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            plugins: {
                legend: { position: "top" },
                tooltip: { callbacks: { label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y ?? "-"}` } }
            },
            scales: {
                x: {
                    ticks: { maxRotation: 45, font: { size: 11 } },
                    grid: { color: "rgba(0,0,0,0.06)" }
                },
                y: {
                    title: { display: !!yLabel, text: yLabel || "" },
                    grid: { color: "rgba(0,0,0,0.06)" },
                    beginAtZero: false
                }
            }
        }
    });
}

function renderToprakCharts(data) {
    const el = document.getElementById("gecmis-content");

    if (!data.kayitlar || data.kayitlar.length === 0) {
        el.innerHTML = `<p class="section-desc">Bu tarla için henüz toprak verisi kaydedilmemiş.</p>`;
        return;
    }

    const labels = data.kayitlar.map((r) => r.tarih);
    const nemData = data.kayitlar.map((r) => r.nem);
    const phData  = data.kayitlar.map((r) => r.ph);

    el.innerHTML = `
        <p class="chart-title">${data.tarla_adi} — Son ${data.kayitlar.length} Kayıt</p>
        <div class="charts-grid">
            <div class="chart-box">
                <h4>Toprak Nemi (%)</h4>
                <div class="chart-wrap">
                    <canvas id="chart-nem"></canvas>
                </div>
            </div>
            <div class="chart-box">
                <h4>Toprak pH Değeri</h4>
                <div class="chart-wrap">
                    <canvas id="chart-ph"></canvas>
                </div>
            </div>
        </div>
    `;

    createLineChart("chart-nem", labels, [
        {
            label: "Nem (%)",
            data: nemData,
            borderColor: "#2196f3",
            backgroundColor: "rgba(33,150,243,0.1)",
            borderWidth: 2,
            pointRadius: 4,
            fill: true,
            tension: 0.3
        }
    ], "Nem (%)");

    createLineChart("chart-ph", labels, [
        {
            label: "pH",
            data: phData,
            borderColor: "#4caf50",
            backgroundColor: "rgba(76,175,80,0.1)",
            borderWidth: 2,
            pointRadius: 4,
            fill: true,
            tension: 0.3
        }
    ], "pH");
}

// ── Model Raporu ──────────────────────────────────────────────────────────

const FEATURE_LABELS = {
    soil_moisture:             "Toprak Nemi",
    temperature:               "Sıcaklık",
    humidity:                  "Nem",
    ph_level:                  "pH Değeri",
    temp_humidity_interaction: "Sıcaklık × Nem",
    moisture_temp_ratio:       "Nem / Sıcaklık",
    ph_deviation:              "pH Sapması",
    low_moisture_flag:         "Düşük Nem Bayrağı",
    high_temp_flag:            "Yüksek Sıcaklık Bayrağı",
    vpd:                       "VPD (Buhar Basıncı Açığı)",
    heat_index:                "Isı İndeksi",
    ph_category:               "pH Kategorisi",
    drought_stress:            "Kuraklık Stresi",
};

function renderModelRapor(data) {
    const el = document.getElementById("model-rapor-content");
    const m = data.selected_model_test_metrics;

    // Metrik kartları
    const metricsHtml = `
        <div class="rapor-metrics">
            <div class="metric-card">
                <div class="metric-value">${(m.macro_f1 * 100).toFixed(1)}%</div>
                <div class="metric-label">Macro F1</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${(m.macro_precision * 100).toFixed(1)}%</div>
                <div class="metric-label">Precision</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${(m.macro_recall * 100).toFixed(1)}%</div>
                <div class="metric-label">Recall</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${(m.roc_auc_ovr * 100).toFixed(1)}%</div>
                <div class="metric-label">ROC-AUC</div>
            </div>
        </div>
        <p class="rapor-sub">
            Seçilen Model: <strong>${data.selected_model}</strong> &nbsp;|&nbsp;
            Doğrulama: <strong>${data.validation}</strong>
        </p>
    `;

    // Özellik önemi için etiketleri dönüştür
    const importances = (data.feature_importances || []).slice(0, 13);
    const labels = importances.map((f) => FEATURE_LABELS[f.feature] || f.feature);
    const values = importances.map((f) => parseFloat((f.importance * 100).toFixed(2)));

    el.innerHTML = `
        ${metricsHtml}
        <div class="chart-box" style="margin-top:1.5rem">
            <h4>Özellik Önemi (Feature Importance)</h4>
            <div class="chart-wrap" style="height:${Math.max(260, importances.length * 28)}px">
                <canvas id="chart-feature-importance"></canvas>
            </div>
        </div>
    `;

    destroyChart("chart-feature-importance");
    const ctx = document.getElementById("chart-feature-importance").getContext("2d");
    activeCharts["chart-feature-importance"] = new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Önem (%)",
                data: values,
                backgroundColor: values.map((_, i) =>
                    `hsl(${130 - i * 8}, 60%, ${55 + i * 2}%)`
                ),
                borderRadius: 4,
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => ` %${ctx.parsed.x.toFixed(2)} önem`
                    }
                }
            },
            scales: {
                x: {
                    title: { display: true, text: "Önem (%)" },
                    grid: { color: "rgba(0,0,0,0.06)" },
                    beginAtZero: true,
                },
                y: {
                    ticks: { font: { size: 12 } },
                    grid: { display: false }
                }
            }
        }
    });
}

async function loadModelRapor() {
    const btn = document.getElementById("load-rapor-btn");
    btn.disabled = true;
    btn.textContent = "Yükleniyor...";
    document.getElementById("model-rapor-content").innerHTML = `<p class="section-desc">Rapor yükleniyor...</p>`;

    try {
        const payload = await apiRequest("/model/rapor");
        renderModelRapor(payload.data);
    } catch (err) {
        document.getElementById("model-rapor-content").innerHTML = `<p class="error-text">${err.message}</p>`;
    } finally {
        btn.disabled = false;
        btn.textContent = "Raporu Yükle";
    }
}

async function fetchGecmis() {
    const tarlaSelect = document.getElementById("gecmis-tarla-select");
    const limitSelect = document.getElementById("gecmis-limit-select");
    const btn = document.getElementById("fetch-gecmis-btn");
    const tarlaId = tarlaSelect?.value;
    const limit = limitSelect?.value || 20;

    if (!tarlaId) {
        alert("Lütfen bir tarla seçin.");
        return;
    }

    btn.disabled = true;
    btn.textContent = "Yükleniyor...";
    document.getElementById("gecmis-content").innerHTML = `<p class="section-desc">Veriler yükleniyor...</p>`;

    try {
        const payload = await apiRequest(`/tarlalar/${tarlaId}/toprak-gecmisi?limit=${limit}`);
        renderToprakCharts(payload.data);
    } catch (err) {
        document.getElementById("gecmis-content").innerHTML = `<p class="error-text">${err.message}</p>`;
    } finally {
        btn.disabled = false;
        btn.textContent = "Grafikleri Yükle";
    }
}
