const { Pool } = require('pg');

/**
 * Create a PostgreSQL connection pool using either DATABASE_URL or individual
 * host/port/user/password/database environment variables.
 *
 * When DATABASE_URL is set, SSL is enabled. Set DB_INSECURE_SSL=true to allow
 * self-signed certificates (rejectUnauthorized: false).
 */
function createPool() {
    const connectionString = process.env.DATABASE_URL;

    if (connectionString) {
        return new Pool({
            connectionString,
            ssl: process.env.DB_INSECURE_SSL === 'true'
                ? { rejectUnauthorized: false }
                : true,
        });
    }

    return new Pool({
        host: process.env.DB_HOST || 'localhost',
        port: process.env.DB_PORT || 5432,
        user: process.env.DB_USER || 'user',
        password: process.env.DB_PASSWORD || 'password',
        database: process.env.DB_NAME || 'marketdb',
    });
}

module.exports = createPool;
