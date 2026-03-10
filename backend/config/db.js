const { Pool } = require('pg');

const connectionString = process.env.DATABASE_URL;

const pool = connectionString
    ? new Pool({
        connectionString,
        ssl: process.env.NODE_ENV === 'development'
            ? { rejectUnauthorized: false }
            : true,
    })
    : new Pool({
        host: process.env.DB_HOST || 'localhost',
        port: process.env.DB_PORT || 5432,
        user: process.env.DB_USER || 'user',
        password: process.env.DB_PASSWORD || 'password',
        database: process.env.DB_NAME || 'marketdb',
    });

module.exports = {
    query: (text, params) => pool.query(text, params),
};
