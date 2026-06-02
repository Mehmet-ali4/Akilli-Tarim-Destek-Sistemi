const { Pool } = require('pg');

const pool = new Pool({
    host: process.env.DB_HOST || 'localhost',
    port: Number(process.env.DB_PORT || 5432),
    database: process.env.DB_NAME || 'akilli_tarim',
    user: process.env.DB_USER || 'postgres',
    password: process.env.DB_PASSWORD || ''
});

async function checkConnection() {
    const client = await pool.connect();
    try {
        await client.query('SELECT 1');
        return true;
    } finally {
        client.release();
    }
}

module.exports = { pool, checkConnection };
