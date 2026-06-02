const { pool } = require('./pool');

async function findUserByEmail(email) {
    const result = await pool.query(
        `SELECT "KullaniciID", "AdSoyad", "Email", "SifreHash"
         FROM "Kullanicilar"
         WHERE "Email" = $1`,
        [email]
    );
    return result.rows[0] || null;
}

async function findUserById(id) {
    const result = await pool.query(
        `SELECT "KullaniciID", "AdSoyad", "Email"
         FROM "Kullanicilar"
         WHERE "KullaniciID" = $1`,
        [id]
    );
    return result.rows[0] || null;
}

async function createUser({ adSoyad, email, sifreHash }) {
    const result = await pool.query(
        `INSERT INTO "Kullanicilar" ("AdSoyad", "Email", "SifreHash")
         VALUES ($1, $2, $3)
         RETURNING "KullaniciID", "AdSoyad", "Email"`,
        [adSoyad, email, sifreHash]
    );
    return result.rows[0];
}

module.exports = { findUserByEmail, findUserById, createUser };
