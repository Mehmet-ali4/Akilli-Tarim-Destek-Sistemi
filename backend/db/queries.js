const { pool } = require('./pool');

async function getTarlaById(tarlaId) {
    const result = await pool.query(
        `SELECT "TarlaID", "KullaniciID", "TarlaAdi", "Konum_Enlem", "Konum_Boylam", "Ekilmis_Urun"
         FROM "Tarlalar"
         WHERE "TarlaID" = $1`,
        [tarlaId]
    );
    return result.rows[0] || null;
}

async function listTarlalar() {
    const result = await pool.query(
        `SELECT "TarlaID", "KullaniciID", "TarlaAdi", "Konum_Enlem", "Konum_Boylam", "Ekilmis_Urun"
         FROM "Tarlalar"
         ORDER BY "TarlaID"`
    );
    return result.rows;
}

async function insertTarla({ kullaniciId, tarlaAdi, konumEnlem, konumBoylam, ekilmisUrun }) {
    const result = await pool.query(
        `INSERT INTO "Tarlalar" ("KullaniciID", "TarlaAdi", "Konum_Enlem", "Konum_Boylam", "Ekilmis_Urun")
         VALUES ($1, $2, $3, $4, $5)
         RETURNING "TarlaID", "KullaniciID", "TarlaAdi", "Konum_Enlem", "Konum_Boylam", "Ekilmis_Urun"`,
        [kullaniciId, tarlaAdi, konumEnlem, konumBoylam, ekilmisUrun || null]
    );
    return result.rows[0];
}

async function deleteTarla(tarlaId) {
    const result = await pool.query(
        `DELETE FROM "Tarlalar"
         WHERE "TarlaID" = $1
         RETURNING "TarlaID"`,
        [tarlaId]
    );
    return result.rows[0] || null;
}

async function insertToprakVerisi({ tarlaId, phDegeri, nemOrani, npkDegerleri }) {
    const result = await pool.query(
        `INSERT INTO "Toprak_Verileri" ("TarlaID", "Tarih", "PH_Degeri", "Nem_Orani", "NPK_Degerleri")
         VALUES ($1, CURRENT_DATE, $2, $3, $4)
         RETURNING "AnalizID", "TarlaID", "Tarih", "PH_Degeri", "Nem_Orani", "NPK_Degerleri"`,
        [tarlaId, phDegeri, nemOrani, npkDegerleri || null]
    );
    return result.rows[0];
}

async function insertSistemOnerisi({ tarlaId, oneriTuru, oneriDetayi }) {
    const result = await pool.query(
        `INSERT INTO "Sistem_Onerileri" ("TarlaID", "Olusturma_Trh", "Oneri_Turu", "Oneri_Detayi")
         VALUES ($1, NOW(), $2, $3)
         RETURNING "OneriID", "TarlaID", "Olusturma_Trh", "Oneri_Turu", "Oneri_Detayi"`,
        [tarlaId, oneriTuru, oneriDetayi]
    );
    return result.rows[0];
}

async function listToprakGecmisi(tarlaId, limit = 30) {
    const result = await pool.query(
        `SELECT "AnalizID", "Tarih", "PH_Degeri", "Nem_Orani", "NPK_Degerleri"
         FROM "Toprak_Verileri"
         WHERE "TarlaID" = $1
         ORDER BY "Tarih" ASC, "AnalizID" ASC
         LIMIT $2`,
        [tarlaId, limit]
    );
    return result.rows.map((r) => ({
        tarih: r.Tarih instanceof Date
            ? r.Tarih.toISOString().split('T')[0]
            : String(r.Tarih).split('T')[0],
        ph: r.PH_Degeri !== null ? parseFloat(r.PH_Degeri) : null,
        nem: r.Nem_Orani !== null ? parseFloat(r.Nem_Orani) : null,
        npk: r.NPK_Degerleri || null
    }));
}

function formatOneriDetayi(oneriDetayi) {
    try {
        const parsed = JSON.parse(oneriDetayi);
        if (parsed && typeof parsed === 'object') {
            if (parsed.health_score !== undefined) {
                return {
                    summary: `Saglik: ${parsed.health_score}/100, Hasat: ${parsed.estimated_harvest_date}`,
                    prediction: parsed.health_status || null,
                    actions: parsed.notes || [],
                    confidence: parsed.health_score ? parsed.health_score / 100 : null,
                    input: parsed,
                    is_json: true,
                    analysis_type: 'bitki_sagligi'
                };
            }

            return {
                summary: parsed.prediction || oneriDetayi,
                prediction: parsed.prediction || null,
                actions: Array.isArray(parsed.actions) ? parsed.actions : [],
                confidence: parsed.confidence ?? null,
                input: parsed.input || null,
                is_json: true,
                analysis_type: 'sulama'
            };
        }
    } catch (error) {
        // Manuel metin kayitlari JSON degil.
    }

    return {
        summary: oneriDetayi,
        prediction: null,
        actions: [],
        confidence: null,
        input: null,
        is_json: false
    };
}

function resolveAnalysisType(oneriTuru, detailAnalysisType) {
    const lower = (oneriTuru || '').toLowerCase();
    if (lower.includes('bitki') || lower.includes('saglik')) return 'bitki_sagligi';
    if (lower.includes('sulama') && lower.includes('gubre')) return 'sulama_gubre';
    if (lower.includes('gubre') || lower.includes('gubreleme')) return 'gubre';
    if (lower.includes('sulama')) return 'sulama';
    if (lower.includes('normal')) return 'normal';
    return detailAnalysisType || 'diger';
}

function formatOneriRow(row) {
    const detail = formatOneriDetayi(row.Oneri_Detayi);
    const analysisType = resolveAnalysisType(row.Oneri_Turu, detail.analysis_type);
    return {
        oneri_id: row.OneriID,
        tarla_id: row.TarlaID,
        tarla_adi: row.TarlaAdi || null,
        olusturma_tarihi: row.Olusturma_Trh,
        oneri_turu: row.Oneri_Turu,
        analysis_type: analysisType,
        ozet: detail.summary,
        tahmin: detail.prediction,
        aksiyonlar: detail.actions,
        guven_skoru: detail.confidence,
        girdi_verisi: detail.input,
        detay_tipi: detail.is_json ? 'json' : 'metin'
    };
}

async function listOnerilerByTarla(tarlaId) {
    const result = await pool.query(
        `SELECT so."OneriID", so."TarlaID", t."TarlaAdi",
                so."Olusturma_Trh", so."Oneri_Turu", so."Oneri_Detayi"
         FROM "Sistem_Onerileri" so
         JOIN "Tarlalar" t ON t."TarlaID" = so."TarlaID"
         WHERE so."TarlaID" = $1
         ORDER BY so."Olusturma_Trh" DESC, so."OneriID" DESC`,
        [tarlaId]
    );
    return result.rows.map(formatOneriRow);
}

async function listAllOneriler() {
    const result = await pool.query(
        `SELECT so."OneriID", so."TarlaID", t."TarlaAdi",
                so."Olusturma_Trh", so."Oneri_Turu", so."Oneri_Detayi"
         FROM "Sistem_Onerileri" so
         JOIN "Tarlalar" t ON t."TarlaID" = so."TarlaID"
         ORDER BY so."Olusturma_Trh" DESC, so."OneriID" DESC`
    );
    return result.rows.map(formatOneriRow);
}

function mapPredictionToOneriTuru(prediction) {
    if (prediction === 'Sulama + Gubre/Ilac Uygula') {
        return 'Sulama ve Gubreleme';
    }
    if (prediction === 'Sulama Yap') {
        return 'Sulama';
    }
    if (prediction === 'Gubre/Ilac Uygula') {
        return 'Gubreleme';
    }
    return 'Durum Normal';
}

module.exports = {
    getTarlaById,
    listTarlalar,
    insertTarla,
    deleteTarla,
    insertToprakVerisi,
    insertSistemOnerisi,
    listOnerilerByTarla,
    listAllOneriler,
    listToprakGecmisi,
    mapPredictionToOneriTuru,
    formatOneriRow
};
