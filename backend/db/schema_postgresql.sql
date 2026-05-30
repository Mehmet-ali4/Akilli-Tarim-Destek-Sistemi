-- Akilli Tarim Destek Sistemi - PostgreSQL semasi
-- Kaynak: veritabani-tasarimi.md

CREATE TABLE IF NOT EXISTS "Kullanicilar" (
    "KullaniciID" SERIAL PRIMARY KEY,
    "AdSoyad" VARCHAR(100) NOT NULL,
    "Email" VARCHAR(100) NOT NULL UNIQUE,
    "SifreHash" VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS "Tarlalar" (
    "TarlaID" SERIAL PRIMARY KEY,
    "KullaniciID" INT NOT NULL REFERENCES "Kullanicilar"("KullaniciID") ON DELETE CASCADE,
    "TarlaAdi" VARCHAR(100) NOT NULL,
    "Konum_Enlem" DECIMAL(10, 8) NOT NULL,
    "Konum_Boylam" DECIMAL(11, 8) NOT NULL,
    "Ekilmis_Urun" VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS "Toprak_Verileri" (
    "AnalizID" SERIAL PRIMARY KEY,
    "TarlaID" INT NOT NULL REFERENCES "Tarlalar"("TarlaID") ON DELETE CASCADE,
    "Tarih" DATE NOT NULL,
    "PH_Degeri" DECIMAL(4, 2),
    "Nem_Orani" DECIMAL(5, 2),
    "NPK_Degerleri" VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS "Hava_Verileri" (
    "HavaVeriID" SERIAL PRIMARY KEY,
    "TarlaID" INT NOT NULL REFERENCES "Tarlalar"("TarlaID") ON DELETE CASCADE,
    "Tarih" DATE NOT NULL,
    "Sicaklik_Ort" DECIMAL(4, 2),
    "Yagis_Miktari" DECIMAL(6, 2),
    CONSTRAINT "uq_hava_tarla_tarih" UNIQUE ("TarlaID", "Tarih")
);

CREATE TABLE IF NOT EXISTS "Sistem_Onerileri" (
    "OneriID" SERIAL PRIMARY KEY,
    "TarlaID" INT NOT NULL REFERENCES "Tarlalar"("TarlaID") ON DELETE CASCADE,
    "Olusturma_Trh" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    "Oneri_Turu" VARCHAR(50) NOT NULL,
    "Oneri_Detayi" TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS "idx_tarlalar_kullanici" ON "Tarlalar"("KullaniciID");
CREATE INDEX IF NOT EXISTS "idx_toprak_tarla_tarih" ON "Toprak_Verileri"("TarlaID", "Tarih" DESC);
CREATE INDEX IF NOT EXISTS "idx_hava_tarla_tarih" ON "Hava_Verileri"("TarlaID", "Tarih" DESC);
CREATE INDEX IF NOT EXISTS "idx_oneri_tarla_tarih" ON "Sistem_Onerileri"("TarlaID", "Olusturma_Trh" DESC);
