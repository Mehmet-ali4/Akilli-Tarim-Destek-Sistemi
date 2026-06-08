const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// Veritabanı dosyasının yolu
const dbPath = path.resolve(__dirname, 'akilli_tarim.db');

// Veritabanı bağlantısı oluştur (Eğer dosya yoksa otomatik oluşturur)
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Veritabanına bağlanılamadı:', err.message);
    } else {
        console.log('SQLite veritabanına başarıyla bağlanıldı.');
        initDB();
    }
});

// Veritabanı tablolarını ve indekslerini başlatan fonksiyon
function initDB() {
    db.serialize(() => {
        // 1. Kullanicilar Tablosu
        db.run(`CREATE TABLE IF NOT EXISTS Kullanicilar (
            KullaniciID INTEGER PRIMARY KEY AUTOINCREMENT,
            AdSoyad VARCHAR(100) NOT NULL,
            Email VARCHAR(100) UNIQUE NOT NULL,
            SifreHash VARCHAR(255) NOT NULL
        )`);

        // 2. Tarlalar Tablosu
        db.run(`CREATE TABLE IF NOT EXISTS Tarlalar (
            TarlaID INTEGER PRIMARY KEY AUTOINCREMENT,
            KullaniciID INTEGER NOT NULL,
            TarlaAdi VARCHAR(100) NOT NULL,
            Konum_Enlem DECIMAL(10,8) NOT NULL,
            Konum_Boylam DECIMAL(11,8) NOT NULL,
            Ekilmis_Urun VARCHAR(50),
            FOREIGN KEY (KullaniciID) REFERENCES Kullanicilar(KullaniciID) ON DELETE CASCADE
        )`);

        // 3. Toprak_Verileri Tablosu
        db.run(`CREATE TABLE IF NOT EXISTS Toprak_Verileri (
            AnalizID INTEGER PRIMARY KEY AUTOINCREMENT,
            TarlaID INTEGER NOT NULL,
            Tarih DATE NOT NULL,
            PH_Degeri DECIMAL(4,2),
            Nem_Orani DECIMAL(5,2),
            NPK_Degerleri VARCHAR(50),
            FOREIGN KEY (TarlaID) REFERENCES Tarlalar(TarlaID) ON DELETE CASCADE
        )`);

        // 4. Hava_Verileri Tablosu
        db.run(`CREATE TABLE IF NOT EXISTS Hava_Verileri (
            HavaVeriID INTEGER PRIMARY KEY AUTOINCREMENT,
            TarlaID INTEGER NOT NULL,
            Tarih DATE NOT NULL,
            Sicaklik_Ort DECIMAL(4,2),
            Yagis_Miktari DECIMAL(6,2),
            FOREIGN KEY (TarlaID) REFERENCES Tarlalar(TarlaID) ON DELETE CASCADE
        )`);

        // 5. Sistem_Onerileri Tablosu
        db.run(`CREATE TABLE IF NOT EXISTS Sistem_Onerileri (
            OneriID INTEGER PRIMARY KEY AUTOINCREMENT,
            TarlaID INTEGER NOT NULL,
            Olusturma_Trh DATE NOT NULL,
            Oneri_Turu VARCHAR(50) NOT NULL,
            Oneri_Detayi TEXT NOT NULL,
            FOREIGN KEY (TarlaID) REFERENCES Tarlalar(TarlaID) ON DELETE CASCADE
        )`);

        // Performans ve Sorgu Optimizasyonu İçin İndeksleme (Indexing)
        // Yabancı anahtarlar (Foreign Keys) ve sık aranan alanlar (Tarih, Email) için indeksler
        db.run(`CREATE INDEX IF NOT EXISTS idx_kullanici_email ON Kullanicilar(Email)`);
        db.run(`CREATE INDEX IF NOT EXISTS idx_tarla_kullanici ON Tarlalar(KullaniciID)`);
        db.run(`CREATE INDEX IF NOT EXISTS idx_toprak_tarla ON Toprak_Verileri(TarlaID)`);
        db.run(`CREATE INDEX IF NOT EXISTS idx_toprak_tarih ON Toprak_Verileri(Tarih)`);
        db.run(`CREATE INDEX IF NOT EXISTS idx_hava_tarla ON Hava_Verileri(TarlaID)`);
        db.run(`CREATE INDEX IF NOT EXISTS idx_hava_tarih ON Hava_Verileri(Tarih)`);
        db.run(`CREATE INDEX IF NOT EXISTS idx_oneri_tarla ON Sistem_Onerileri(TarlaID)`);
        db.run(`CREATE INDEX IF NOT EXISTS idx_oneri_tarih ON Sistem_Onerileri(Olusturma_Trh)`);

        // Sistemin hemen çalışabilmesi için varsayılan bir kullanıcı ve tarla ekle
        db.run(`INSERT OR IGNORE INTO Kullanicilar (KullaniciID, AdSoyad, Email, SifreHash) VALUES (1, 'Varsayılan Çiftçi', 'ciftci@akillitarim.com', '123456')`);
        db.run(`INSERT OR IGNORE INTO Tarlalar (TarlaID, KullaniciID, TarlaAdi, Konum_Enlem, Konum_Boylam, Ekilmis_Urun) VALUES (1, 1, 'Merkez Tarla', 39.92077, 32.85411, 'Buğday')`);

        console.log('Veritabanı tabloları ve indeksleri başarıyla kontrol edildi/oluşturuldu.');
    });
}

module.exports = db;
