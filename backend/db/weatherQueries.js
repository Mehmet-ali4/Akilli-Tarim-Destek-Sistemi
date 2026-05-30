const { pool } = require('./pool');

async function insertHavaVerisi({ tarlaId, tarih, sicaklikOrt, yagisMiktari }) {
    const result = await pool.query(
        `INSERT INTO "Hava_Verileri" ("TarlaID", "Tarih", "Sicaklik_Ort", "Yagis_Miktari")
         VALUES ($1, $2, $3, $4)
         ON CONFLICT ON CONSTRAINT "uq_hava_tarla_tarih" DO UPDATE
           SET "Sicaklik_Ort" = EXCLUDED."Sicaklik_Ort",
               "Yagis_Miktari" = EXCLUDED."Yagis_Miktari"
         RETURNING "HavaVeriID", "TarlaID", "Tarih", "Sicaklik_Ort", "Yagis_Miktari"`,
        [tarlaId, tarih, sicaklikOrt, yagisMiktari]
    );
    return result.rows[0];
}

async function getHavaGecmisi(tarlaId, limit = 7) {
    const result = await pool.query(
        `SELECT "HavaVeriID", "Tarih", "Sicaklik_Ort", "Yagis_Miktari"
         FROM "Hava_Verileri"
         WHERE "TarlaID" = $1
         ORDER BY "Tarih" DESC
         LIMIT $2`,
        [tarlaId, limit]
    );
    return result.rows;
}

module.exports = { insertHavaVerisi, getHavaGecmisi };
