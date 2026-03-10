require('dotenv').config({ path: require('path').resolve(__dirname, '..', '.env') });

const fs = require('fs');
const path = require('path');
const createPool = require('../config/createPool');

const pool = createPool();

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