const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
require('dotenv').config();

const { checkConnection } = require('./db/pool');
const {
    getTarlaById,
    listTarlalar,
    insertTarla,
    deleteTarla,
    insertToprakVerisi,
    insertSistemOnerisi,
    listOnerilerByTarla,
    listAllOneriler,
    listToprakGecmisi,
    mapPredictionToOneriTuru
} = require('./db/queries');
const { findUserByEmail, findUserById, createUser } = require('./db/auth');
const { fetchCurrentWeather, fetchForecast } = require('./services/weather');
const { insertHavaVerisi, getHavaGecmisi } = require('./db/weatherQueries');

const JWT_SECRET = process.env.JWT_SECRET || 'akilli_tarim_gizli';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '7d';
const OPENWEATHER_API_KEY = process.env.OPENWEATHER_API_KEY || '';

const app = express();
const PORT = process.env.PORT || 3000;
const multer = require('multer');
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://127.0.0.1:5000/predict';
const AI_IMAGE_URL = process.env.AI_IMAGE_URL || 'http://127.0.0.1:5000/analyze-image';
const upload = multer({
    storage: multer.memoryStorage(),
    limits: { fileSize: 5 * 1024 * 1024 }
});
const API_KEY = process.env.API_KEY;

const rateLimitStore = new Map();
const RATE_LIMIT = 60;
const RATE_WINDOW_MS = 60 * 1000;

app.use(cors());
app.use(express.json());

function sendResponse(res, status, errorName, message, data) {
    const payload = {
        code: status,
        error: errorName,
        message
    };

    if (data !== undefined) {
        payload.data = data;
    }

    return res.status(status).json(payload);
}

function apiKeyAuth(req, res, next) {
    if (!API_KEY) {
        return next();
    }

    const key = req.headers['x-api-key'];
    if (!key || key !== API_KEY) {
        return sendResponse(res, 401, 'Unauthorized', 'API anahtarı veya token geçersiz');
    }

    return next();
}

function jwtAuth(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.startsWith('Bearer ')
        ? authHeader.slice(7)
        : null;

    if (!token) {
        return sendResponse(res, 401, 'Unauthorized', 'API anahtarı veya token geçersiz');
    }

    try {
        req.user = jwt.verify(token, JWT_SECRET);
        return next();
    } catch {
        return sendResponse(res, 401, 'Unauthorized', 'API anahtarı veya token geçersiz');
    }
}

function rateLimiter(req, res, next) {
    const identifier = req.ip || req.connection.remoteAddress || 'unknown';
    const now = Date.now();
    const record = rateLimitStore.get(identifier) || { count: 0, start: now };

    if (now - record.start >= RATE_WINDOW_MS) {
        record.count = 0;
        record.start = now;
    }

    record.count += 1;
    rateLimitStore.set(identifier, record);

    if (record.count > RATE_LIMIT) {
        return sendResponse(res, 429, 'Too Many Requests', 'Rate limit aşıldı, 1 dakika bekleyin');
    }

    return next();
}

function buildAiPayload(body) {
    return {
        soil_moisture: body.soil_moisture,
        temperature: body.temperature,
        humidity: body.humidity,
        ph_level: body.ph_level
    };
}

function validatePredictPayload(body) {
    const requiredFields = ['soil_moisture', 'temperature', 'humidity', 'ph_level'];
    for (const field of requiredFields) {
        if (body[field] === undefined || body[field] === null) {
            throw new Error(`Eksik alan: ${field}`);
        }
    }
}

app.use(express.static(require('path').join(__dirname, '..', 'frontend')));

// Auth endpoint'leri rate limit ve API key'den muaf
app.post('/api/auth/register', async (req, res) => {
    try {
        const { ad_soyad, email, sifre } = req.body;

        if (!ad_soyad || !email || !sifre) {
            return sendResponse(res, 400, 'Bad Request', 'Eksik veya hatalı parametre. ad_soyad, email ve sifre zorunludur.');
        }

        if (sifre.length < 6) {
            return sendResponse(res, 400, 'Bad Request', 'Şifre en az 6 karakter olmalıdır.');
        }

        const mevcutKullanici = await findUserByEmail(email);
        if (mevcutKullanici) {
            return sendResponse(res, 400, 'Bad Request', 'Bu e-posta adresi zaten kayıtlı.');
        }

        const sifreHash = await bcrypt.hash(sifre, 10);
        const yeniKullanici = await createUser({ adSoyad: ad_soyad, email, sifreHash });

        const token = jwt.sign(
            { kullaniciId: yeniKullanici.KullaniciID, email: yeniKullanici.Email, adSoyad: yeniKullanici.AdSoyad },
            JWT_SECRET,
            { expiresIn: JWT_EXPIRES_IN }
        );

        return sendResponse(res, 201, 'Created', 'Kayıt başarılı', {
            token,
            kullanici: {
                id: yeniKullanici.KullaniciID,
                ad_soyad: yeniKullanici.AdSoyad,
                email: yeniKullanici.Email
            }
        });
    } catch (error) {
        return sendResponse(res, 500, 'Internal Server Error', 'Sunucu hatası, tekrar deneyin', { details: error.message });
    }
});

app.post('/api/auth/login', async (req, res) => {
    try {
        const { email, sifre } = req.body;

        if (!email || !sifre) {
            return sendResponse(res, 400, 'Bad Request', 'Eksik veya hatalı parametre. email ve sifre zorunludur.');
        }

        const kullanici = await findUserByEmail(email);
        if (!kullanici) {
            return sendResponse(res, 401, 'Unauthorized', 'E-posta veya şifre hatalı.');
        }

        const sifreEslesti = await bcrypt.compare(sifre, kullanici.SifreHash);
        if (!sifreEslesti) {
            return sendResponse(res, 401, 'Unauthorized', 'E-posta veya şifre hatalı.');
        }

        const token = jwt.sign(
            { kullaniciId: kullanici.KullaniciID, email: kullanici.Email, adSoyad: kullanici.AdSoyad },
            JWT_SECRET,
            { expiresIn: JWT_EXPIRES_IN }
        );

        return sendResponse(res, 200, 'OK', 'Giriş başarılı', {
            token,
            kullanici: {
                id: kullanici.KullaniciID,
                ad_soyad: kullanici.AdSoyad,
                email: kullanici.Email
            }
        });
    } catch (error) {
        return sendResponse(res, 500, 'Internal Server Error', 'Sunucu hatası, tekrar deneyin', { details: error.message });
    }
});

app.get('/api/auth/profile', jwtAuth, async (req, res) => {
    try {
        const kullanici = await findUserById(req.user.kullaniciId);
        if (!kullanici) {
            return sendResponse(res, 404, 'Not Found', 'Kullanıcı bulunamadı.');
        }

        return sendResponse(res, 200, 'OK', 'İstek başarılı', {
            id: kullanici.KullaniciID,
            ad_soyad: kullanici.AdSoyad,
            email: kullanici.Email
        });
    } catch (error) {
        return sendResponse(res, 500, 'Internal Server Error', 'Sunucu hatası, tekrar deneyin', { details: error.message });
    }
});

app.use('/api', rateLimiter, apiKeyAuth);

app.get('/api/status', async (req, res) => {
    try {
        const dbConnected = await checkConnection();

        let aiStatus = 'disconnected';
        try {
            const aiRes = await fetch(`${AI_SERVICE_URL.replace('/predict', '/health')}`, {
                method: 'GET',
                signal: AbortSignal.timeout(3000)
            });
            aiStatus = aiRes.ok ? 'running' : 'error';
        } catch {
            aiStatus = 'disconnected';
        }

        return sendResponse(res, 200, 'OK', 'İstek başarılı', {
            database: dbConnected ? 'connected' : 'disconnected',
            ai: aiStatus
        });
    } catch (error) {
        return sendResponse(res, 500, 'Internal Server Error', 'Sunucu hatası, tekrar deneyin', {
            details: error.message
        });
    }
});

app.get('/api/oneriler', async (req, res) => {
    try {
        const oneriler = await listAllOneriler();
        return sendResponse(res, 200, 'OK', 'İstek başarılı', oneriler);
    } catch (error) {
        return sendResponse(res, 500, 'Internal Server Error', 'Sunucu hatası, tekrar deneyin', {
            details: error.message
        });
    }
});

app.get('/api/tarlalar', async (req, res) => {
    try {
        const tarlalar = await listTarlalar();
        return sendResponse(res, 200, 'OK', 'İstek başarılı', tarlalar);
    } catch (error) {
        return sendResponse(res, 500, 'Internal Server Error', 'Sunucu hatası, tekrar deneyin', {
            details: error.message
        });
    }
});

app.post('/api/tarlalar', jwtAuth, async (req, res) => {
    try {
        const { tarla_adi, konum_enlem, konum_boylam, ekilmis_urun } = req.body;
        const kullanici_id = req.user.kullaniciId;

        // Zorunlu alanları kontrol et
        if (!tarla_adi || konum_enlem === undefined || konum_boylam === undefined) {
            return sendResponse(res, 400, 'Bad Request', 'Eksik veya hatalı parametre. tarla_adi, konum_enlem ve konum_boylam zorunludur.');
        }

        // Koordinat doğrulama
        const enlem = parseFloat(konum_enlem);
        const boylam = parseFloat(konum_boylam);
        if (Number.isNaN(enlem) || Number.isNaN(boylam) || enlem < -90 || enlem > 90 || boylam < -180 || boylam > 180) {
            return sendResponse(res, 400, 'Bad Request', 'Geçersiz koordinat değerleri. Enlem: -90 ile 90, boylam: -180 ile 180 arasında olmalıdır.');
        }

        const yeniTarla = await insertTarla({
            kullaniciId: Number(kullanici_id),
            tarlaAdi: tarla_adi,
            konumEnlem: enlem,
            konumBoylam: boylam,
            ekilmisUrun: ekilmis_urun || null
        });

        return sendResponse(res, 201, 'Created', 'Tarla başarıyla oluşturuldu', yeniTarla);
    } catch (error) {
        return sendResponse(res, 500, 'Internal Server Error', 'Sunucu hatası, tekrar deneyin', {
            details: error.message
        });
    }
});

app.delete('/api/tarlalar/:tarlaId', async (req, res) => {
    try {
        const tarlaId = Number(req.params.tarlaId);
        if (Number.isNaN(tarlaId)) {
            return sendResponse(res, 400, 'Bad Request', 'Eksik veya hatalı parametre');
        }

        const silinenTarla = await deleteTarla(tarlaId);
        if (!silinenTarla) {
            return sendResponse(res, 404, 'Not Found', 'İstenen kaynak bulunamadı');
        }

        return sendResponse(res, 200, 'OK', 'Tarla başarıyla silindi', silinenTarla);
    } catch (error) {
        return sendResponse(res, 500, 'Internal Server Error', 'Sunucu hatası, tekrar deneyin', {
            details: error.message
        });
    }
});

app.get('/api/tarlalar/:tarlaId/oneriler', async (req, res) => {
    try {
        const tarlaId = Number(req.params.tarlaId);
        if (Number.isNaN(tarlaId)) {
            return sendResponse(res, 400, 'Bad Request', 'Eksik veya hatalı parametre');
        }

        const tarla = await getTarlaById(tarlaId);
        if (!tarla) {
            return sendResponse(res, 404, 'Not Found', 'İstenen kaynak bulunamadı');
        }

        const oneriler = await listOnerilerByTarla(tarlaId);
        return sendResponse(res, 200, 'OK', 'İstek başarılı', oneriler);
    } catch (error) {
        return sendResponse(res, 500, 'Internal Server Error', 'Sunucu hatası, tekrar deneyin', {
            details: error.message
        });
    }
});

app.get('/api/tarlalar/:tarlaId/toprak-gecmisi', async (req, res) => {
    try {
        const tarlaId = Number(req.params.tarlaId);
        if (Number.isNaN(tarlaId)) {
            return sendResponse(res, 400, 'Bad Request', 'Eksik veya hatalı parametre');
        }

        const tarla = await getTarlaById(tarlaId);
        if (!tarla) {
            return sendResponse(res, 404, 'Not Found', 'İstenen kaynak bulunamadı');
        }

        const limit = Math.min(Number(req.query.limit) || 30, 100);
        const gecmis = await listToprakGecmisi(tarlaId, limit);
        return sendResponse(res, 200, 'OK', 'İstek başarılı', { tarla_id: tarlaId, tarla_adi: tarla.TarlaAdi, kayitlar: gecmis });
    } catch (error) {
        return sendResponse(res, 500, 'Internal Server Error', 'Sunucu hatası, tekrar deneyin', { details: error.message });
    }
});

app.get('/api/tarlalar/:tarlaId/hava', async (req, res) => {
    try {
        if (!OPENWEATHER_API_KEY || OPENWEATHER_API_KEY === 'buraya_api_anahtarini_yaz') {
            return sendResponse(res, 503, 'Service Unavailable', 'OpenWeatherMap API anahtarı tanımlanmamış. .env dosyasına OPENWEATHER_API_KEY ekleyin.');
        }

        const tarlaId = Number(req.params.tarlaId);
        if (Number.isNaN(tarlaId)) {
            return sendResponse(res, 400, 'Bad Request', 'Eksik veya hatalı parametre');
        }

        const tarla = await getTarlaById(tarlaId);
        if (!tarla) {
            return sendResponse(res, 404, 'Not Found', 'İstenen kaynak bulunamadı');
        }

        const lat = parseFloat(tarla.Konum_Enlem);
        const lon = parseFloat(tarla.Konum_Boylam);

        const [anlik, tahmin] = await Promise.all([
            fetchCurrentWeather(lat, lon, OPENWEATHER_API_KEY),
            fetchForecast(lat, lon, OPENWEATHER_API_KEY)
        ]);

        // Bugünün verisini DB'ye kaydet (upsert)
        await insertHavaVerisi({
            tarlaId,
            tarih: new Date().toISOString().split('T')[0],
            sicaklikOrt: anlik.sicaklik,
            yagisMiktari: anlik.yagis_1s
        });

        return sendResponse(res, 200, 'OK', 'İstek başarılı', {
            tarla_id: tarlaId,
            tarla_adi: tarla.TarlaAdi,
            anlik,
            tahmin
        });
    } catch (error) {
        return sendResponse(res, 500, 'Internal Server Error', 'Hava durumu alınamadı', { details: error.message });
    }
});

app.get('/api/tarlalar/:tarlaId/hava/gecmis', async (req, res) => {
    try {
        const tarlaId = Number(req.params.tarlaId);
        if (Number.isNaN(tarlaId)) {
            return sendResponse(res, 400, 'Bad Request', 'Eksik veya hatalı parametre');
        }

        const gecmis = await getHavaGecmisi(tarlaId);
        return sendResponse(res, 200, 'OK', 'İstek başarılı', gecmis);
    } catch (error) {
        return sendResponse(res, 500, 'Internal Server Error', 'Sunucu hatası, tekrar deneyin', { details: error.message });
    }
});

app.post('/api/plant-health/analyze', upload.single('image'), async (req, res) => {
    try {
        if (!req.file) {
            return sendResponse(res, 400, 'Bad Request', 'Eksik veya hatalı parametre');
        }

        const tarlaId = req.body.tarla_id ? Number(req.body.tarla_id) : null;
        if (req.body.tarla_id && Number.isNaN(tarlaId)) {
            return sendResponse(res, 400, 'Bad Request', 'Eksik veya hatalı parametre');
        }

        let cropName = req.body.crop_name || null;
        if (tarlaId !== null) {
            const tarla = await getTarlaById(tarlaId);
            if (!tarla) {
                return sendResponse(res, 404, 'Not Found', 'İstenen kaynak bulunamadı');
            }
            cropName = tarla.Ekilmis_Urun || cropName;
        }

        const formData = new FormData();
        const blob = new Blob([req.file.buffer], { type: req.file.mimetype });
        formData.append('image', blob, req.file.originalname);
        if (cropName) {
            formData.append('crop_name', cropName);
        }

        const response = await fetch(AI_IMAGE_URL, {
            method: 'POST',
            body: formData
        });

        const payload = await response.json();
        if (!response.ok) {
            const allowedStatusCodes = new Set([400, 401, 403, 404, 429, 500]);
            const status = allowedStatusCodes.has(response.status) ? response.status : 500;
            return sendResponse(
                res,
                status,
                payload.error || 'Internal Server Error',
                payload.message || 'Sunucu hatası, tekrar deneyin',
                payload.details
            );
        }

        if (tarlaId !== null && payload.data) {
            const oneriKaydi = await insertSistemOnerisi({
                tarlaId,
                oneriTuru: 'Bitki Sagligi',
                oneriDetayi: JSON.stringify(payload.data)
            });

            payload.data.saved_records = {
                oneri_id: oneriKaydi.OneriID
            };
        }

        return res.status(200).json(payload);
    } catch (error) {
        return sendResponse(res, 500, 'Internal Server Error', 'Sunucu hatası, tekrar deneyin', {
            details: error.message
        });
    }
});

app.post('/api/predict', async (req, res) => {
    try {
        const body = req.body || {};
        validatePredictPayload(body);

        const tarlaId = body.tarla_id !== undefined ? Number(body.tarla_id) : null;
        if (body.tarla_id !== undefined && Number.isNaN(tarlaId)) {
            return sendResponse(res, 400, 'Bad Request', 'Eksik veya hatalı parametre');
        }

        if (tarlaId !== null) {
            const tarla = await getTarlaById(tarlaId);
            if (!tarla) {
                return sendResponse(res, 404, 'Not Found', 'İstenen kaynak bulunamadı');
            }
        }

        const aiPayload = buildAiPayload(body);
        const response = await fetch(AI_SERVICE_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(aiPayload)
        });

        const payload = await response.json();
        if (!response.ok) {
            const allowedStatusCodes = new Set([400, 401, 403, 404, 429, 500]);
            const status = allowedStatusCodes.has(response.status) ? response.status : 500;
            return sendResponse(
                res,
                status,
                payload.error || 'Internal Server Error',
                payload.message || 'Sunucu hatası, tekrar deneyin',
                payload.details
            );
        }

        if (tarlaId !== null && payload.data) {
            const toprakKaydi = await insertToprakVerisi({
                tarlaId,
                phDegeri: body.ph_level,
                nemOrani: body.soil_moisture,
                npkDegerleri: body.npk_degerleri || null
            });

            const oneriKaydi = await insertSistemOnerisi({
                tarlaId,
                oneriTuru: mapPredictionToOneriTuru(payload.data.prediction),
                oneriDetayi: JSON.stringify({
                    prediction: payload.data.prediction,
                    actions: payload.data.actions || [],
                    confidence: payload.data.confidence,
                    input: aiPayload
                })
            });

            payload.data.saved_records = {
                analiz_id: toprakKaydi.AnalizID,
                oneri_id: oneriKaydi.OneriID
            };
        }

        return res.status(200).json(payload);
    } catch (error) {
        if (error.message.startsWith('Eksik alan:')) {
            return sendResponse(res, 400, 'Bad Request', 'Eksik veya hatalı parametre');
        }

        return sendResponse(res, 500, 'Internal Server Error', 'Sunucu hatası, tekrar deneyin', {
            details: error.message
        });
    }
});

app.get('/api/model/rapor', (req, res) => {
    try {
        const reportPath = require('path').join(__dirname, '..', 'ai_engine', 'artifacts', 'evaluation_report.json');
        if (!require('fs').existsSync(reportPath)) {
            return sendResponse(res, 404, 'Not Found', 'Model raporu henüz oluşturulmamış. Modeli eğitin.');
        }
        const report = JSON.parse(require('fs').readFileSync(reportPath, 'utf8'));
        return sendResponse(res, 200, 'OK', 'İstek başarılı', report);
    } catch (error) {
        return sendResponse(res, 500, 'Internal Server Error', 'Rapor okunamadı', { details: error.message });
    }
});

app.use((req, res) => {
    return sendResponse(res, 404, 'Not Found', 'İstenen kaynak bulunamadı');
});

app.listen(PORT, async () => {
    try {
        await checkConnection();
        console.log(`Sunucu http://localhost:${PORT} portunda calisiyor.`);
        console.log('PostgreSQL baglantisi basarili.');
    } catch (error) {
        console.log(`Sunucu http://localhost:${PORT} portunda calisiyor.`);
        console.warn('PostgreSQL baglantisi kurulamadi:', error.message);
    }
});
