const createPool = require('./createPool');

const pool = createPool();

module.exports = {
    query: (text, params) => pool.query(text, params),
};
