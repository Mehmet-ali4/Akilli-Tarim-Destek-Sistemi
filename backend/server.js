const express = require('express');
const cors = require('cors');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:5000';

app.use(cors());
app.use(express.json());

// Basit bir test rotası
app.get('/api/status', (req, res) => {
    res.json({ status: 'success', message: 'Akıllı Tarım Backend Çalışıyor!' });
});

// AI servisinin durumunu kontrol et
app.get('/api/ai-status', async (req, res) => {
    try {
        const response = await axios.get(`${AI_SERVICE_URL}/health`, { timeout: 5000 });
        res.json({ status: 'online', ai_service: response.data });
    } catch (err) {
        res.json({ status: 'offline', message: 'AI servisi çalışmıyor. Lütfen Python servisini başlatın.' });
    }
});

// AI tahmin rotası - Python servisine yönlendirir
app.post('/api/predict', async (req, res) => {
    try {
        console.log('Tahmin isteği alındı:', req.body);
        
        // Python AI servisine isteği ilet
        const response = await axios.post(`${AI_SERVICE_URL}/predict`, req.body, {
            headers: { 'Content-Type': 'application/json' },
            timeout: 30000 // 30 saniye timeout (model ilk yüklemede yavaş olabilir)
        });
        
        console.log('AI servisinden cevap:', response.data);
        res.json(response.data);
        
    } catch (err) {
        console.error('AI servisi hatası:', err.message);
        
        if (err.code === 'ECONNREFUSED') {
            res.status(503).json({ 
                error: 'AI servisi çalışmıyor. Lütfen Python servisini başlatın.',
                detail: 'python predict.py komutuyla AI servisini başlatın.'
            });
        } else if (err.response) {
            // AI servisi hata döndürdü
            res.status(err.response.status).json(err.response.data);
        } else {
            res.status(500).json({ error: 'Beklenmeyen bir hata oluştu: ' + err.message });
        }
    }
});

app.listen(PORT, () => {
    console.log(`Backend sunucu http://localhost:${PORT} portunda çalışıyor.`);
    console.log(`AI servisi adresi: ${AI_SERVICE_URL}`);
});
