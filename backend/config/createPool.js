const { Pool } = require('pg');

/**
 * Create a PostgreSQL connection pool using either DATABASE_URL or individual
 * host/port/user/password/database environment variables.
 *
 * SSL is opt-in: set DB_SSL=true to enable it for DATABASE_URL connections.
 * Set DB_INSECURE_SSL=true to additionally disable certificate verification
 * (useful for self-signed certs in non-production environments).
 * By default SSL is disabled so local Postgres instances work without extra config.
 */
function createPool() {
    const connectionString = process.env.DATABASE_URL;

    if (connectionString) {
        const useSsl = process.env.DB_SSL === 'true';
        let sslConfig = false;
        if (useSsl) {
            sslConfig = process.env.DB_INSECURE_SSL === 'true'
                ? { rejectUnauthorized: false }
                : { rejectUnauthorized: true };
        }

        return new Pool({
            connectionString,
            ssl: sslConfig,
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
