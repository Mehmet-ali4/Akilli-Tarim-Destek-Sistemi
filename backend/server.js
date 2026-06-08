const express = require('express');
const cors = require('cors');
const axios = require('axios');
require('dotenv').config();

// Veritabanı bağlantısını ve tabloları başlat
const db = require('./db/database');

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

        // Veritabanına kaydetme işlemleri
        const tarla_id = req.body.tarla_id || 1; // Şimdilik varsayılan 1
        const bugun = new Date().toISOString().split('T')[0];
        const npk = `${req.body.nitrojen || 0}-${req.body.fosfor || 0}-${req.body.potasyum || 0}`;

        // Toprak verilerini kaydet
        db.run(`INSERT INTO Toprak_Verileri (TarlaID, Tarih, PH_Degeri, Nem_Orani, NPK_Degerleri) VALUES (?, ?, ?, ?, ?)`, 
            [tarla_id, bugun, req.body.ph, req.body.toprak_nemi, npk], (err) => {
                if(err) console.error("Toprak verisi kaydedilemedi:", err.message);
            });

        // Hava verilerini kaydet
        db.run(`INSERT INTO Hava_Verileri (TarlaID, Tarih, Sicaklik_Ort) VALUES (?, ?, ?)`,
            [tarla_id, bugun, req.body.sicaklik], (err) => {
                if(err) console.error("Hava verisi kaydedilemedi:", err.message);
            });

        // AI önerisini kaydet
        const oneri_detayi = response.data.ozet || response.data.prediction || "AI analizi tamamlandı.";
        db.run(`INSERT INTO Sistem_Onerileri (TarlaID, Olusturma_Trh, Oneri_Turu, Oneri_Detayi) VALUES (?, ?, ?, ?)`,
            [tarla_id, bugun, 'AI Analizi', oneri_detayi], (err) => {
                if(err) console.error("Öneri kaydedilemedi:", err.message);
            });

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

// Geçmiş önerileri getiren endpoint
app.get('/api/gecmis-oneriler', (req, res) => {
    const tarla_id = req.query.tarla_id || 1;
    db.all(`SELECT * FROM Sistem_Onerileri WHERE TarlaID = ? ORDER BY OneriID DESC LIMIT 10`, [tarla_id], (err, rows) => {
        if (err) {
            console.error('Veritabanı okuma hatası:', err.message);
            return res.status(500).json({ error: 'Geçmiş öneriler alınamadı.' });
        }
        res.json({ status: 'success', data: rows });
    });
});

app.listen(PORT, () => {
    console.log(`Backend sunucu http://localhost:${PORT} portunda çalışıyor.`);
    console.log(`AI servisi adresi: ${AI_SERVICE_URL}`);
});
