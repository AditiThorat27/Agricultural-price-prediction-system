const { Pool } = require('pg');

/**
 * Create a PostgreSQL connection pool using either DATABASE_URL or individual
 * host/port/user/password/database environment variables.
 *
 * SSL is opt-in when DATABASE_URL is used:
 *   DB_SSL=true            – enable SSL with full certificate verification
 *   DB_INSECURE_SSL=true   – enable SSL but skip certificate verification
 *                            (useful for self-signed certs in staging)
 *   (default)              – no SSL (safe for local/dev Postgres)
 */
function createPool() {
    const connectionString = process.env.DATABASE_URL;

    if (connectionString) {
        let sslConfig = false;
        if (process.env.DB_INSECURE_SSL === 'true') {
            sslConfig = { rejectUnauthorized: false };
        } else if (process.env.DB_SSL === 'true') {
            sslConfig = { rejectUnauthorized: true };
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
