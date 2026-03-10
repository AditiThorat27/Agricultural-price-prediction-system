require('dotenv').config();
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');

const dbConfig = require('./config/db');
const apiRoutes = require('./routes/api');

const app = express();
const PORT = process.env.PORT || 8000;

app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

app.use('/api', apiRoutes);

// Global Error Handler
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something broke!' });
});

app.listen(PORT, () => {
    console.log(`Node backend running on port ${PORT}`);
});
