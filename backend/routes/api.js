const express = require('express');
const axios = require('axios');
const db = require('../config/db');

const router = express.Router();

const MODEL_SERVICE_URL = process.env.MODEL_SERVICE_URL || 'http://localhost:8001';

// GET all markets
router.get('/markets', async (req, res, next) => {
    try {
        const result = await db.query('SELECT * FROM markets');
        res.json(result.rows);
    } catch (err) {
        next(err);
    }
});

// GET specific market by ID
router.get('/market/:id', async (req, res, next) => {
    try {
        const { id } = req.params;
        const marketResult = await db.query('SELECT * FROM markets WHERE id = $1', [id]);
        if (marketResult.rows.length === 0) {
            return res.status(404).json({ error: 'Market not found' });
        }
        
        const priceResult = await db.query(
            'SELECT * FROM prices WHERE market_id = $1 ORDER BY date DESC LIMIT 30', 
            [id]
        );
        
        res.json({
            ...marketResult.rows[0],
            prices: priceResult.rows
        });
    } catch (err) {
        next(err);
    }
});

// GET recommended market predictions
router.get('/recommend', async (req, res, next) => {
    try {
        const { commodity, lat, lon } = req.query;
        
        if (!commodity || !lat || !lon) {
            return res.status(400).json({ error: 'Missing commodity, lat, or lon query parameters' });
        }

        // Call the Python FastAPI model service
        const pythonResponse = await axios.post(`${MODEL_SERVICE_URL}/predict`, {
            commodity: commodity.toLowerCase(),
            lat: parseFloat(lat),
            lon: parseFloat(lon)
        });

        // The python response is assumed to be something like { best_market: "Pune APMC", predicted_price: 25.4 }
        res.json(pythonResponse.data);

    } catch (err) {
        if (err.response) {
            return res.status(err.response.status).json(err.response.data);
        }
        next(err);
    }
});

module.exports = router;
