require('dotenv').config({ path: require('path').resolve(__dirname, '..', '.env') });

const fs = require('fs');
const path = require('path');
const { Pool } = require('pg');

const pool = process.env.DATABASE_URL
    ? new Pool({
        connectionString: process.env.DATABASE_URL,
        ssl: {
            rejectUnauthorized: false,
        },
    })
    : new Pool({
        host: process.env.DB_HOST || 'localhost',
        port: process.env.DB_PORT || 5432,
        user: process.env.DB_USER || 'user',
        password: process.env.DB_PASSWORD || 'password',
        database: process.env.DB_NAME || 'marketdb',
    });

async function initDb() {
    const schemaPath = path.resolve(__dirname, '..', '..', 'db', 'schema.sql');
    const seedPath = path.resolve(__dirname, '..', '..', 'db', 'seed.sql');

    const schemaSql = fs.readFileSync(schemaPath, 'utf8');
    const seedSql = fs.readFileSync(seedPath, 'utf8');

    await pool.query(schemaSql);
    await pool.query(seedSql);

    console.log('Database schema and seed applied successfully.');
}

initDb()
    .catch((error) => {
        console.error('Failed to initialize database:', error);
        process.exitCode = 1;
    })
    .finally(async () => {
        await pool.end();
    });