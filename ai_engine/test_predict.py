"""
=============================================================================
 Akıllı Tarım Destek Sistemi — AI Engine Test Suite
 Modül: ai_engine/predict.py
 Test Framework: pytest + unittest.mock
 Yazar: QA Otomasyon Mühendisi
 Tarih: 2026-06-08
=============================================================================
 Bu test dosyası, predict.py içindeki iş mantıklarını uçtan uca test eder:
   1. analyze_conditions() fonksiyonu (8-parametreli kural-tabanlı uzman sistem)
   2. Keras model tahmin mekanizması (mock ile)
   3. Flask /predict endpoint'i (entegrasyon testi)
   4. Sınır değerler (edge cases) ve hata durumları
=============================================================================
"""

import pytest
import numpy as np
import json
import sys
import os
from unittest.mock import patch, MagicMock

# predict.py modülünü import edebilmek için path ayarla
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# =====================================================================
#  FIXTURE: Flask test client + model mock
# =====================================================================

@pytest.fixture(scope="module")
def mock_model():
    """Keras modelini mock'la — gerçek TensorFlow yüklenmesini engeller."""
    mock = MagicMock()
    # sigmoid çıkışı: 0-1 arası float döndür
    mock.predict.return_value = np.array([[0.78]], dtype=np.float32)
    return mock


@pytest.fixture(scope="module")
def app_client(mock_model):
    """Flask test client oluştur, gerçek model yerine mock kullan."""
    # TensorFlow ve model yüklemeyi mock'la
    with patch("predict.tf") as mock_tf, \
         patch("predict.get_or_create_model", return_value=mock_model), \
         patch("predict.model", mock_model):
        
        mock_tf.__version__ = "2.16.0-mock"
        
        # predict modülünü import et
        import predict
        predict.model = mock_model
        
        app = predict.app
        app.config["TESTING"] = True
        
        with app.test_client() as client:
            yield client, mock_model, predict


@pytest.fixture
def ideal_data():
    """Buğday için ideal koşullar — tüm parametreler aralık içinde."""
    return {
        "urun": "bugday",
        "sicaklik": 20.0,
        "nem": 50.0,
        "toprak_nemi": 50.0,
        "ph": 6.8,
        "nitrojen": 45.0,
        "fosfor": 55.0,
        "potasyum": 110.0,
        "bitki_sagligi": 85.0,
    }


@pytest.fixture
def worst_data():
    """Tüm parametreler kötü — en düşük skor beklenir."""
    return {
        "urun": "bugday",
        "sicaklik": -10.0,
        "nem": 95.0,
        "toprak_nemi": 5.0,
        "ph": 3.0,
        "nitrojen": 2.0,
        "fosfor": 3.0,
        "potasyum": 5.0,
        "bitki_sagligi": 10.0,
    }


# =====================================================================
#  1. ANALYZE_CONDITIONS — TEK TEK PARAMETRE ANALİZLERİ
# =====================================================================

class TestAnalyzeConditions:
    """analyze_conditions() fonksiyonunun kural-tabanlı mantık testleri."""

    # --- 1.1 Sıcaklık Analizi ---

    def test_ideal_sicaklik_bugday(self, app_client):
        """Buğday için ideal sıcaklık aralığı (12-25°C) — skor 1.0 olmalı."""
        _, _, predict = app_client
        data = {"sicaklik": 18, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        sicaklik_factor = next(f for f in result["confidence_factors"] if "Sıcaklık" in f["factor"])
        assert sicaklik_factor["score"] == 1.0, f"İdeal sıcaklıkta skor 1.0 olmalı, {sicaklik_factor['score']} geldi"
        assert result["sulama_gerekli"] is False

    def test_sicaklik_cok_dusuk_don_riski(self, app_client):
        """Sıcaklık -15°C — don riski, skor çok düşük, uyarı mesajı olmalı."""
        _, _, predict = app_client
        data = {"sicaklik": -15, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        sicaklik_factor = next(f for f in result["confidence_factors"] if "Sıcaklık" in f["factor"])
        assert sicaklik_factor["score"] == 0.3, "Aşırı düşük sıcaklıkta skor minimum 0.3'e sabitlenmeli"
        assert any("düşük" in w for w in result["warnings"]), "Düşük sıcaklık uyarısı olmalı"
        assert any("KRİTİK" in r for r in result["recommendations"]), "Kritik don uyarısı olmalı"

    def test_sicaklik_asiri_yuksek(self, app_client):
        """Sıcaklık 50°C — aşırı sıcak, sulama gerekli olmalı."""
        _, _, predict = app_client
        data = {"sicaklik": 50, "nem": 20, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        assert result["sulama_gerekli"] is True, "50°C'de sulama gerekli olmalı"
        sicaklik_factor = next(f for f in result["confidence_factors"] if "Sıcaklık" in f["factor"])
        assert sicaklik_factor["score"] == 0.3, "Aşırı yüksek sıcaklıkta skor 0.3 olmalı"

    def test_sicaklik_sinir_degeri_tam_ideal_min(self, app_client):
        """Sıcaklık tam ideal_min'e eşit (12°C buğday) — skor 1.0."""
        _, _, predict = app_client
        data = {"sicaklik": 12, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        sicaklik_factor = next(f for f in result["confidence_factors"] if "Sıcaklık" in f["factor"])
        assert sicaklik_factor["score"] == 1.0, "Sınır değerde skor 1.0 olmalı"

    def test_sicaklik_sinir_degeri_tam_ideal_max(self, app_client):
        """Sıcaklık tam ideal_max'e eşit (25°C buğday) — skor 1.0."""
        _, _, predict = app_client
        data = {"sicaklik": 25, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        sicaklik_factor = next(f for f in result["confidence_factors"] if "Sıcaklık" in f["factor"])
        assert sicaklik_factor["score"] == 1.0

    def test_sicaklik_1_derece_altinda(self, app_client):
        """Sıcaklık idealin 1°C altında (11°C buğday) — hafif düşüş."""
        _, _, predict = app_client
        data = {"sicaklik": 11, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        sicaklik_factor = next(f for f in result["confidence_factors"] if "Sıcaklık" in f["factor"])
        # 1.0 - 1*0.05 = 0.95
        assert sicaklik_factor["score"] == 0.95

    # --- 1.2 pH Analizi ---

    def test_ph_ideal_aralik(self, app_client):
        """pH buğday için ideal aralıkta (6.0-7.5) — skor 1.0."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.8,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        ph_factor = next(f for f in result["confidence_factors"] if "pH" in f["factor"])
        assert ph_factor["score"] == 1.0

    def test_ph_cok_asidik(self, app_client):
        """pH 2.0 — aşırı asitli toprak, kireçleme önerisi olmalı."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 2.0,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        ph_factor = next(f for f in result["confidence_factors"] if "pH" in f["factor"])
        assert ph_factor["score"] == 0.4, "pH 2.0'da skor minimum 0.4 olmalı"
        assert any("Kireçleme" in g for g in result["gubre_tavsiyeleri"]), "Kireçleme önerisi olmalı"

    def test_ph_cok_bazik(self, app_client):
        """pH 12.0 — aşırı alkali toprak, kükürt önerisi olmalı."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 12.0,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        ph_factor = next(f for f in result["confidence_factors"] if "pH" in f["factor"])
        assert ph_factor["score"] == 0.4, "pH 12'de skor minimum 0.4 olmalı"
        assert any("Kükürt" in g for g in result["gubre_tavsiyeleri"]), "Kükürt önerisi olmalı"

    def test_ph_sinir_tam_min(self, app_client):
        """pH tam alt sınırda (6.0 buğday) — skor 1.0."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.0,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        ph_factor = next(f for f in result["confidence_factors"] if "pH" in f["factor"])
        assert ph_factor["score"] == 1.0

    def test_ph_sinir_tam_max(self, app_client):
        """pH tam üst sınırda (7.5 buğday) — skor 1.0."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 7.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        ph_factor = next(f for f in result["confidence_factors"] if "pH" in f["factor"])
        assert ph_factor["score"] == 1.0

    # --- 1.3 Toprak Nemi — Sulama Kararı ---

    def test_toprak_nemi_ideal(self, app_client):
        """Toprak nemi ideal aralıkta — sulama gerekli değil."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        assert result["sulama_gerekli"] is False

    def test_toprak_nemi_cok_dusuk_kritik_sulama(self, app_client):
        """Toprak nemi %2 — KRİTİK sulama ihtiyacı."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 2, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        assert result["sulama_gerekli"] is True, "Toprak nemi %2'de sulama gerekli"
        assert any("KRİTİK" in r for r in result["recommendations"]), "Kritik sulama uyarısı olmalı"

    def test_toprak_nemi_asiri_yuksek_kok_curumesi(self, app_client):
        """Toprak nemi %95 — kök çürümesi riski."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 95, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        assert any("çürümesi" in w.lower() or "Kök" in w for w in result["warnings"]), "Kök çürümesi uyarısı olmalı"

    def test_toprak_nemi_sifir(self, app_client):
        """Toprak nemi %0 — tamamen kuru toprak."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 0, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        assert result["sulama_gerekli"] is True
        nem_factor = next(f for f in result["confidence_factors"] if "nem" in f["factor"].lower())
        assert nem_factor["score"] <= 0.3, "Sıfır nem'de skor 0.3 veya altı olmalı"

    def test_toprak_nemi_100(self, app_client):
        """Toprak nemi %100 — tamamen su doygunluğu."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 100, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        assert any("çürümesi" in w.lower() or "Kök" in w for w in result["warnings"])

    # --- 1.4 Besin Elementleri (N, P, K) ---

    def test_nitrojen_yeterli(self, app_client):
        """Azot yeterli seviyede — gübre önerisi yok."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 50, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        n_factor = next(f for f in result["confidence_factors"] if "Azot" in f["factor"])
        assert n_factor["score"] == 1.0

    def test_nitrojen_sifir(self, app_client):
        """Azot 0 mg/kg — ciddi eksiklik, gübre tavsiyesi olmalı."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 0, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        n_factor = next(f for f in result["confidence_factors"] if "Azot" in f["factor"])
        assert n_factor["score"] == 0.4, "Sıfır azotta skor minimum 0.4 olmalı"
        assert any("Azotlu gübre" in g for g in result["gubre_tavsiyeleri"])

    def test_fosfor_sifir(self, app_client):
        """Fosfor 0 mg/kg — ciddi eksiklik."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 0, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        p_factor = next(f for f in result["confidence_factors"] if "Fosfor" in f["factor"])
        assert p_factor["score"] == 0.4
        assert any("Fosforlu gübre" in g for g in result["gubre_tavsiyeleri"])

    def test_potasyum_sifir(self, app_client):
        """Potasyum 0 mg/kg — ciddi eksiklik."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 0, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        k_factor = next(f for f in result["confidence_factors"] if "Potasyum" in f["factor"])
        assert k_factor["score"] == 0.4

    def test_tum_besinler_asiri_yuksek(self, app_client):
        """Tüm besin elementleri çok yüksek (999) — skor 1.0 (yeterli)."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 999, "fosfor": 999, "potasyum": 999, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        n_factor = next(f for f in result["confidence_factors"] if "Azot" in f["factor"])
        p_factor = next(f for f in result["confidence_factors"] if "Fosfor" in f["factor"])
        k_factor = next(f for f in result["confidence_factors"] if "Potasyum" in f["factor"])
        assert n_factor["score"] == 1.0
        assert p_factor["score"] == 1.0
        assert k_factor["score"] == 1.0

    # --- 1.5 Bitki Sağlığı ---

    def test_bitki_sagligi_iyi(self, app_client):
        """Bitki sağlığı 85/100 — iyi durumda."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 85}
        result = predict.analyze_conditions(data, "bugday")
        
        bs_factor = next(f for f in result["confidence_factors"] if "sağlığı" in f["factor"])
        assert bs_factor["score"] == 1.0

    def test_bitki_sagligi_kritik(self, app_client):
        """Bitki sağlığı 10/100 — kritik, acil müdahale."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 10}
        result = predict.analyze_conditions(data, "bugday")
        
        bs_factor = next(f for f in result["confidence_factors"] if "sağlığı" in f["factor"])
        assert bs_factor["score"] <= 0.2
        assert any("KRİTİK" in r for r in result["recommendations"])

    def test_bitki_sagligi_sifir(self, app_client):
        """Bitki sağlığı 0/100 — ölü bitki, skor minimum 0.2."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 0}
        result = predict.analyze_conditions(data, "bugday")
        
        bs_factor = next(f for f in result["confidence_factors"] if "sağlığı" in f["factor"])
        assert bs_factor["score"] == 0.2

    def test_bitki_sagligi_orta(self, app_client):
        """Bitki sağlığı 55/100 — orta seviye."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 55}
        result = predict.analyze_conditions(data, "bugday")
        
        bs_factor = next(f for f in result["confidence_factors"] if "sağlığı" in f["factor"])
        assert 0.4 <= bs_factor["score"] <= 0.7


# =====================================================================
#  2. OVERALL SCORE — GENEL SKOR HESAPLAMASI
# =====================================================================

class TestOverallScore:
    """Genel uygunluk skorunun doğru hesaplanıp hesaplanmadığını test eder."""

    def test_ideal_kosullar_yuksek_skor(self, app_client):
        """Tüm parametreler ideal — skor >= 0.85 olmalı."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.8,
                "nitrojen": 45, "fosfor": 55, "potasyum": 110, "bitki_sagligi": 85}
        result = predict.analyze_conditions(data, "bugday")
        
        assert result["overall_score"] >= 0.85, \
            f"İdeal koşullarda skor >= 0.85 olmalı, {result['overall_score']} geldi"

    def test_en_kotu_kosullar_dusuk_skor(self, app_client):
        """Tüm parametreler kötü — skor < 0.45 olmalı."""
        _, _, predict = app_client
        data = {"sicaklik": -10, "nem": 95, "toprak_nemi": 2, "ph": 2.0,
                "nitrojen": 0, "fosfor": 0, "potasyum": 0, "bitki_sagligi": 5}
        result = predict.analyze_conditions(data, "bugday")
        
        assert result["overall_score"] < 0.45, \
            f"En kötü koşullarda skor < 0.45 olmalı, {result['overall_score']} geldi"

    def test_skor_0_1_araliginda(self, app_client):
        """Overall score her zaman 0-1 arasında olmalı."""
        _, _, predict = app_client
        
        test_cases = [
            {"sicaklik": -50, "nem": 0, "toprak_nemi": 0, "ph": 0, "nitrojen": 0, "fosfor": 0, "potasyum": 0, "bitki_sagligi": 0},
            {"sicaklik": 100, "nem": 100, "toprak_nemi": 100, "ph": 14, "nitrojen": 1000, "fosfor": 1000, "potasyum": 1000, "bitki_sagligi": 100},
            {"sicaklik": 0, "nem": 50, "toprak_nemi": 50, "ph": 7, "nitrojen": 50, "fosfor": 50, "potasyum": 50, "bitki_sagligi": 50},
        ]
        
        for i, data in enumerate(test_cases):
            result = predict.analyze_conditions(data, "bugday")
            assert 0.0 <= result["overall_score"] <= 1.0, \
                f"Test case {i}: Skor 0-1 arasında olmalı, {result['overall_score']} geldi"

    def test_skor_ortalama_hesabi(self, app_client):
        """Skor, tüm confidence_factors ortalaması olarak hesaplanır."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.8,
                "nitrojen": 45, "fosfor": 55, "potasyum": 110, "bitki_sagligi": 85}
        result = predict.analyze_conditions(data, "bugday")
        
        factor_scores = [f["score"] for f in result["confidence_factors"]]
        expected_avg = round(sum(factor_scores) / len(factor_scores), 2)
        assert result["overall_score"] == expected_avg, \
            f"Overall score ({result['overall_score']}) = ortalama ({expected_avg}) olmalı"


# =====================================================================
#  3. ÜRÜN BAZLI TESTLERİ
# =====================================================================

class TestUrunBazli:
    """Farklı ürünler için parametrelerin doğru eşiklerle değerlendirildiğini test eder."""

    def test_domates_yuksek_potasyum_ihtiyaci(self, app_client):
        """Domates: potasyum ihtiyacı 'yüksek' (eşik 180) — 100'de düşük olmalı."""
        _, _, predict = app_client
        data = {"sicaklik": 22, "nem": 65, "toprak_nemi": 65, "ph": 6.4,
                "nitrojen": 40, "fosfor": 80, "potasyum": 100, "bitki_sagligi": 80}
        result = predict.analyze_conditions(data, "domates")
        
        k_factor = next(f for f in result["confidence_factors"] if "Potasyum" in f["factor"])
        assert k_factor["score"] < 1.0, "Domates için potasyum 100'de düşük olmalı (eşik: 180)"
        assert any("Potasyumlu gübre" in g for g in result["gubre_tavsiyeleri"])

    def test_cay_asidik_toprak_tercihi(self, app_client):
        """Çay: ideal pH 4.5-6.0 — pH 5.0'da ideal olmalı."""
        _, _, predict = app_client
        data = {"sicaklik": 18, "nem": 75, "toprak_nemi": 75, "ph": 5.0,
                "nitrojen": 60, "fosfor": 50, "potasyum": 130, "bitki_sagligi": 80}
        result = predict.analyze_conditions(data, "cay")
        
        ph_factor = next(f for f in result["confidence_factors"] if "pH" in f["factor"])
        assert ph_factor["score"] == 1.0, "Çay için pH 5.0 ideal olmalı"

    def test_bilinmeyen_urun_bugday_fallback(self, app_client):
        """Bilinmeyen ürün adı — buğday parametrelerine geri dönmeli."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.8,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bilinmeyen_urun")
        
        assert result["urun_ad"] == "Buğday", "Bilinmeyen ürün buğday'a dönmeli"


# =====================================================================
#  4. EK UYARILAR — HAVA NEMİ ve EXTREM KOŞULLAR
# =====================================================================

class TestEkUyarilar:
    """Ek genel önerilerin doğru koşullarda tetiklenip tetiklenmediğini test eder."""

    def test_hava_nemi_cok_yuksek_mantar_uyarisi(self, app_client):
        """Hava nemi > %80 — mantar hastalık uyarısı."""
        _, _, predict = app_client
        data = {"sicaklik": 25, "nem": 90, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        assert any("mantar" in r.lower() or "Mantar" in r for r in result["recommendations"]), \
            "Hava nemi %90'da mantar uyarısı olmalı"

    def test_sicaklik_35_ustu_sulama_zamani(self, app_client):
        """Sıcaklık > 35°C — sulama zamanı uyarısı."""
        _, _, predict = app_client
        data = {"sicaklik": 40, "nem": 30, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        assert any("sıcaklık" in r.lower() or "🌡️" in r for r in result["recommendations"])

    def test_sicaklik_5_alti_don_uyarisi(self, app_client):
        """Sıcaklık < 5°C — don tehlikesi uyarısı."""
        _, _, predict = app_client
        data = {"sicaklik": 2, "nem": 60, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        assert any("❄️" in r or "Don" in r or "don" in r for r in result["recommendations"])


# =====================================================================
#  5. FLASK ENDPOINT TESTLERİ
# =====================================================================

class TestFlaskEndpoints:
    """Flask /predict ve /health endpoint'lerinin davranış testleri."""

    def test_health_endpoint(self, app_client):
        """GET /health — 200 ve model durumu."""
        client, _, _ = app_client
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "online"
        assert data["model_loaded"] is True

    def test_predict_endpoint_ideal_data(self, app_client, ideal_data):
        """POST /predict — ideal veriyle başarılı tahmin."""
        client, mock_model, _ = app_client
        mock_model.predict.return_value = np.array([[0.85]], dtype=np.float32)
        
        response = client.post(
            "/predict",
            data=json.dumps(ideal_data),
            content_type="application/json"
        )
        
        assert response.status_code == 200
        result = response.get_json()
        assert "confidence" in result
        assert "recommendations" in result
        assert "sulama_gerekli" in result
        assert "prediction" in result
        assert "urun_ad" in result
        assert result["urun_ad"] == "Buğday"

    def test_predict_endpoint_bos_body(self, app_client):
        """POST /predict — boş JSON body — default değerler kullanılmalı."""
        client, mock_model, _ = app_client
        mock_model.predict.return_value = np.array([[0.5]], dtype=np.float32)
        
        response = client.post(
            "/predict",
            data=json.dumps({}),
            content_type="application/json"
        )
        
        assert response.status_code == 200
        result = response.get_json()
        assert "confidence" in result

    def test_predict_endpoint_eksik_parametreler(self, app_client):
        """POST /predict — bazı parametreler eksik, default'lar devreye girmeli."""
        client, mock_model, _ = app_client
        mock_model.predict.return_value = np.array([[0.6]], dtype=np.float32)
        
        partial_data = {"urun": "domates", "sicaklik": 28}
        response = client.post(
            "/predict",
            data=json.dumps(partial_data),
            content_type="application/json"
        )
        
        assert response.status_code == 200
        result = response.get_json()
        assert result["urun_ad"] == "Domates"

    def test_predict_endpoint_hatali_veri(self, app_client):
        """POST /predict — string değer gönderildiğinde anlamlı hata mesajı."""
        client, _, _ = app_client
        
        bad_data = {"sicaklik": "çok_sıcak", "nem": "yüksek"}
        response = client.post(
            "/predict",
            data=json.dumps(bad_data),
            content_type="application/json"
        )
        
        # safe_float() ValueError fırlatacak → 400 + anlamlı mesaj
        assert response.status_code == 400
        result = response.get_json()
        assert "error" in result
        # Yeni: Hata mesajı hangi alanın hatalı olduğunu belirtmeli
        assert "sicaklik" in result["error"] or "sayısal" in result["error"], \
            "Hata mesajı hangi alanın hatalı olduğunu belirtmeli"
        assert "tip" in result, "Yanıtta 'tip' (yardımcı bilgi) alanı olmalı"

    def test_predict_response_yapisi(self, app_client, ideal_data):
        """Yanıt yapısı doğru alanları içermeli."""
        client, mock_model, _ = app_client
        mock_model.predict.return_value = np.array([[0.75]], dtype=np.float32)
        
        response = client.post(
            "/predict",
            data=json.dumps(ideal_data),
            content_type="application/json"
        )
        
        result = response.get_json()
        required_fields = [
            "prediction", "ozet", "confidence", "tf_confidence",
            "confidence_factors", "warnings", "recommendations",
            "gubre_tavsiyeleri", "urun_ad", "sulama_gerekli", "ai_technology"
        ]
        for field in required_fields:
            assert field in result, f"Yanıtta '{field}' alanı eksik"

    def test_predict_tf_confidence_0_1_arasi(self, app_client, ideal_data):
        """TF model confidence her zaman 0-1 arası olmalı."""
        client, mock_model, _ = app_client
        mock_model.predict.return_value = np.array([[0.92]], dtype=np.float32)
        
        response = client.post(
            "/predict",
            data=json.dumps(ideal_data),
            content_type="application/json"
        )
        
        result = response.get_json()
        assert 0.0 <= result["tf_confidence"] <= 1.0


# =====================================================================
#  6. KERAS MODEL MOCK TESTLERİ
# =====================================================================

class TestKerasModelMock:
    """Model predict çağrısının doğru şekilde yapıldığını test eder."""

    def test_model_8_parametre_alir(self, app_client, ideal_data):
        """Model.predict() 8 özellikli numpy array ile çağrılır."""
        client, mock_model, _ = app_client
        mock_model.predict.return_value = np.array([[0.7]], dtype=np.float32)
        
        client.post(
            "/predict",
            data=json.dumps(ideal_data),
            content_type="application/json"
        )
        
        call_args = mock_model.predict.call_args[0][0]
        assert call_args.shape == (1, 8), f"Model girdisi (1,8) olmalı, {call_args.shape} geldi"
        assert call_args.dtype == np.float32

    def test_model_girdi_sirasi(self, app_client):
        """Model girdisi doğru sırada olmalı: sicaklik, nem, toprak_nemi, ph, nitrojen, fosfor, potasyum, bitki_sagligi."""
        client, mock_model, _ = app_client
        mock_model.predict.return_value = np.array([[0.5]], dtype=np.float32)
        
        # Tüm değerler fiziksel sınırlar içinde olmalı (clamp sonrası değişmesin)
        data = {
            "urun": "bugday",
            "sicaklik": 11.0, "nem": 22.0, "toprak_nemi": 33.0, "ph": 7.0,
            "nitrojen": 55.0, "fosfor": 66.0, "potasyum": 77.0, "bitki_sagligi": 88.0
        }
        
        client.post("/predict", data=json.dumps(data), content_type="application/json")
        
        call_args = mock_model.predict.call_args[0][0]
        expected = [11.0, 22.0, 33.0, 7.0, 55.0, 66.0, 77.0, 88.0]
        np.testing.assert_array_almost_equal(call_args[0], expected)


# =====================================================================
#  7. SINIR DEĞERLERİ ve EDGE CASE'LER
# =====================================================================

class TestEdgeCases:
    """Uç senaryolar ve sınır değer testleri."""

    def test_tum_degerler_sifir(self, app_client):
        """Tüm sayısal değerler 0 — sistem çökmemeli."""
        _, _, predict = app_client
        data = {"sicaklik": 0, "nem": 0, "toprak_nemi": 0, "ph": 0,
                "nitrojen": 0, "fosfor": 0, "potasyum": 0, "bitki_sagligi": 0}
        result = predict.analyze_conditions(data, "bugday")
        
        assert "overall_score" in result
        assert isinstance(result["overall_score"], float)
        assert len(result["confidence_factors"]) == 7  # 7 analiz faktörü

    def test_negatif_degerler_clamp_edilir(self, app_client):
        """Negatif değerler fiziksel sınırlara clamp edilir (nem=-10 → 0, ph=-1 → 0 vb.)."""
        _, _, predict = app_client
        data = {"sicaklik": -50, "nem": -10, "toprak_nemi": -5, "ph": -1,
                "nitrojen": -20, "fosfor": -10, "potasyum": -5, "bitki_sagligi": -10}
        result = predict.analyze_conditions(data, "bugday")
        
        assert "overall_score" in result
        assert result["overall_score"] >= 0.0  # Skor negatif olmamalı
        # Clamp doğrulaması: negatif değerler 0'a sabitlenmeli (sıcaklık hariç, -60'a kadar izin var)

    def test_cok_buyuk_degerler_clamp_edilir(self, app_client):
        """Çok büyük sayılar fiziksel sınırlara clamp edilir."""
        _, _, predict = app_client
        data = {"sicaklik": 1000, "nem": 9999, "toprak_nemi": 9999, "ph": 100,
                "nitrojen": 99999, "fosfor": 99999, "potasyum": 99999, "bitki_sagligi": 9999}
        result = predict.analyze_conditions(data, "bugday")
        
        assert "overall_score" in result
        assert 0.0 <= result["overall_score"] <= 1.0
        # sicaklik 1000 → clamp 60, nem 9999 → clamp 100, ph 100 → clamp 14 vb.

    def test_float_ondalik_degerler(self, app_client):
        """Ondalıklı değerler doğru işlenmeli."""
        _, _, predict = app_client
        data = {"sicaklik": 22.756, "nem": 55.123, "toprak_nemi": 48.999,
                "ph": 6.543, "nitrojen": 38.7, "fosfor": 52.1, "potasyum": 99.99,
                "bitki_sagligi": 72.5}
        result = predict.analyze_conditions(data, "bugday")
        
        assert isinstance(result["overall_score"], float)

    def test_string_to_float_donusum(self, app_client):
        """String olarak gelen sayılar float'a dönüştürülmeli."""
        _, _, predict = app_client
        data = {"sicaklik": "25", "nem": "50", "toprak_nemi": "50", "ph": "6.5",
                "nitrojen": "40", "fosfor": "50", "potasyum": "100", "bitki_sagligi": "70"}
        result = predict.analyze_conditions(data, "bugday")
        
        assert "overall_score" in result  # String → float dönüşümü çalışmalı

    def test_eksik_veri_default_degerler(self, app_client):
        """Parametreler eksik olduğunda default değerler kullanılmalı."""
        _, _, predict = app_client
        data = {}  # Hiçbir parametre yok
        result = predict.analyze_conditions(data, "bugday")
        
        assert "overall_score" in result
        # Default: sicaklik=25, nem=50, toprak_nemi=40, ph=6.5...
        assert result["overall_score"] > 0

    def test_tum_urunler_crash_etmemeli(self, app_client):
        """Tüm tanımlı ürünler için analyze_conditions hatasız çalışmalı."""
        _, _, predict = app_client
        data = {"sicaklik": 22, "nem": 55, "toprak_nemi": 55, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        
        for urun_key in predict.URUN_BILGILERI.keys():
            result = predict.analyze_conditions(data, urun_key)
            assert "overall_score" in result, f"{urun_key} için sonuç üretilemedi"
            assert result["urun_ad"] == predict.URUN_BILGILERI[urun_key]["ad"]


# =====================================================================
#  8. OZET MESAJI MANTIK TESTLERİ
# =====================================================================

class TestOzetMesaji:
    """Skor aralığına göre doğru özet mesajı üretilip üretilmediğini test eder."""

    def test_ozet_yuksek_skor(self, app_client, ideal_data):
        """Skor >= 0.85 — 'oldukça uygun' mesajı."""
        client, mock_model, _ = app_client
        mock_model.predict.return_value = np.array([[0.9]], dtype=np.float32)
        
        response = client.post(
            "/predict",
            data=json.dumps(ideal_data),
            content_type="application/json"
        )
        result = response.get_json()
        
        if result["confidence"] >= 0.85:
            assert "uygun" in result["ozet"].lower()

    def test_ozet_dusuk_skor_acil_mudahale(self, app_client, worst_data):
        """Skor < 0.45 — 'acil müdahale' mesajı."""
        client, mock_model, _ = app_client
        mock_model.predict.return_value = np.array([[0.1]], dtype=np.float32)
        
        response = client.post(
            "/predict",
            data=json.dumps(worst_data),
            content_type="application/json"
        )
        result = response.get_json()
        
        if result["confidence"] < 0.45:
            assert "müdahale" in result["ozet"].lower() or "uygun değil" in result["ozet"].lower()


# =====================================================================
#  9. SULAMA KARARI LOJİĞİ
# =====================================================================

class TestSulamaKarari:
    """Sulama kararının doğru koşullarda verilip verilmediğini test eder."""

    def test_sulama_toprak_nemi_dusuk(self, app_client):
        """Toprak nemi düşükken sulama gerekli."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 10, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        assert result["sulama_gerekli"] is True

    def test_sulama_sicaklik_yuksek(self, app_client):
        """Sıcaklık yüksek ama toprak nemi yeterli — sulama hâlâ gerekli (sıcaklık tetikler)."""
        _, _, predict = app_client
        data = {"sicaklik": 40, "nem": 30, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        assert result["sulama_gerekli"] is True, "Yüksek sıcaklıkta sulama gerekli"

    def test_sulama_gerekmez_ideal(self, app_client):
        """Her şey ideal — sulama gereksiz."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        assert result["sulama_gerekli"] is False

    def test_sulama_mesaji_predict_endpoint(self, app_client):
        """Sulama gerekli olduğunda prediction mesajında 'önerilir' olmalı."""
        client, mock_model, _ = app_client
        mock_model.predict.return_value = np.array([[0.3]], dtype=np.float32)
        
        data = {"urun": "bugday", "sicaklik": 20, "nem": 50, "toprak_nemi": 10,
                "ph": 6.5, "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        
        response = client.post("/predict", data=json.dumps(data), content_type="application/json")
        result = response.get_json()
        
        assert "önerilir" in result["prediction"].lower()


# =====================================================================
#  10. RETURN YAPISININ BUTUNLUGU
# =====================================================================

class TestReturnYapisi:
    """analyze_conditions() dönüş yapısının tutarlılığını test eder."""

    def test_donus_yapisi_tam(self, app_client):
        """Dönüş dict'i tüm gerekli anahtarları içermeli."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        required_keys = [
            "confidence_factors", "warnings", "recommendations",
            "gubre_tavsiyeleri", "overall_score", "urun_ad", "sulama_gerekli"
        ]
        for key in required_keys:
            assert key in result, f"'{key}' anahtarı eksik"

    def test_confidence_factors_7_adet(self, app_client):
        """Her zaman 7 confidence factor olmalı (sıcaklık, pH, nem, N, P, K, bitki sağlığı)."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        assert len(result["confidence_factors"]) == 7, \
            f"7 confidence factor olmalı, {len(result['confidence_factors'])} geldi"

    def test_confidence_factor_score_aralik(self, app_client):
        """Her confidence factor skoru 0-1 arasında olmalı."""
        _, _, predict = app_client
        
        test_cases = [
            {"sicaklik": -50, "nem": 0, "toprak_nemi": 0, "ph": 0,
             "nitrojen": 0, "fosfor": 0, "potasyum": 0, "bitki_sagligi": 0},
            {"sicaklik": 100, "nem": 100, "toprak_nemi": 100, "ph": 14,
             "nitrojen": 1000, "fosfor": 1000, "potasyum": 1000, "bitki_sagligi": 100},
        ]
        
        for data in test_cases:
            result = predict.analyze_conditions(data, "bugday")
            for factor in result["confidence_factors"]:
                assert 0.0 <= factor["score"] <= 1.0, \
                    f"Factor '{factor['factor']}' skoru 0-1 arasında olmalı: {factor['score']}"

    def test_recommendations_liste_tipi(self, app_client):
        """Recommendations ve warnings her zaman list olmalı."""
        _, _, predict = app_client
        data = {"sicaklik": 20, "nem": 50, "toprak_nemi": 50, "ph": 6.5,
                "nitrojen": 40, "fosfor": 50, "potasyum": 100, "bitki_sagligi": 70}
        result = predict.analyze_conditions(data, "bugday")
        
        assert isinstance(result["recommendations"], list)
        assert isinstance(result["warnings"], list)
        assert isinstance(result["gubre_tavsiyeleri"], list)
        assert isinstance(result["confidence_factors"], list)


# =====================================================================
#  11. DOĞRULAMA ve CLAMP TESTLERİ (YENİ - Sorunlar düzeltildikten sonra)
# =====================================================================

class TestValidationAndClamp:
    """Girdi doğrulama, tip kontrolü ve fiziksel sınır clamp testleri."""

    # --- 11.1 safe_float() — Tip Doğrulama ---

    def test_safe_float_gecerli_sayi(self, app_client):
        """Geçerli sayı string'i float'a çevrilmeli."""
        _, _, predict = app_client
        assert predict.safe_float("25.5", "sicaklik", 20) == 25.5
        assert predict.safe_float(42, "sicaklik", 20) == 42.0
        assert predict.safe_float(0, "ph", 6.5) == 0.0

    def test_safe_float_none_default_doner(self, app_client):
        """None geldiğinde default değer kullanılmalı."""
        _, _, predict = app_client
        assert predict.safe_float(None, "sicaklik", 25) == 25.0
        assert predict.safe_float(None, "ph", 6.5) == 6.5

    def test_safe_float_hatali_string_ValueError(self, app_client):
        """Sayısal olmayan string → anlamlı ValueError fırlatmalı."""
        _, _, predict = app_client
        with pytest.raises(ValueError) as exc_info:
            predict.safe_float("çok_sıcak", "sicaklik", 25)
        
        error_msg = str(exc_info.value)
        assert "sicaklik" in error_msg, "Hata mesajı alan adını içermeli"
        assert "çok_sıcak" in error_msg, "Hata mesajı gelen değeri içermeli"
        assert "sayısal" in error_msg, "Hata mesajı yönlendirme içermeli"

    def test_safe_float_liste_TypeError(self, app_client):
        """Liste gibi geçersiz tip → ValueError fırlatmalı."""
        _, _, predict = app_client
        with pytest.raises(ValueError):
            predict.safe_float([1, 2, 3], "fosfor", 50)

    def test_safe_float_dict_TypeError(self, app_client):
        """Dict gibi geçersiz tip → ValueError fırlatmalı."""
        _, _, predict = app_client
        with pytest.raises(ValueError):
            predict.safe_float({"a": 1}, "potasyum", 100)

    def test_safe_float_bool_kabul_edilir(self, app_client):
        """Bool Python'da int alt tipidir, float'a dönüştürülebilir."""
        _, _, predict = app_client
        assert predict.safe_float(True, "bitki_sagligi", 70) == 1.0
        assert predict.safe_float(False, "bitki_sagligi", 70) == 0.0

    # --- 11.2 clamp_value() — Fiziksel Sınır Testleri ---

    def test_clamp_sicaklik_alt_sinir(self, app_client):
        """Sıcaklık -100 → -60'a clamp edilmeli."""
        _, _, predict = app_client
        assert predict.clamp_value(-100, "sicaklik") == -60.0

    def test_clamp_sicaklik_ust_sinir(self, app_client):
        """Sıcaklık 200 → 60'a clamp edilmeli."""
        _, _, predict = app_client
        assert predict.clamp_value(200, "sicaklik") == 60.0

    def test_clamp_sicaklik_sinir_icinde(self, app_client):
        """Sıcaklık 25 → değişmemeli."""
        _, _, predict = app_client
        assert predict.clamp_value(25, "sicaklik") == 25.0

    def test_clamp_nem_negatif_sifira(self, app_client):
        """Nem -10 → 0'a clamp edilmeli."""
        _, _, predict = app_client
        assert predict.clamp_value(-10, "nem") == 0.0

    def test_clamp_nem_100_ustu(self, app_client):
        """Nem 200 → 100'e clamp edilmeli."""
        _, _, predict = app_client
        assert predict.clamp_value(200, "nem") == 100.0

    def test_clamp_ph_0_14_arasi(self, app_client):
        """pH -5 → 0, pH 20 → 14."""
        _, _, predict = app_client
        assert predict.clamp_value(-5, "ph") == 0.0
        assert predict.clamp_value(20, "ph") == 14.0
        assert predict.clamp_value(7.0, "ph") == 7.0

    def test_clamp_fosfor_negatif(self, app_client):
        """Fosfor -50 → 0'a clamp edilmeli."""
        _, _, predict = app_client
        assert predict.clamp_value(-50, "fosfor") == 0.0

    def test_clamp_potasyum_ust_sinir(self, app_client):
        """Potasyum 999 → 500'e clamp edilmeli."""
        _, _, predict = app_client
        assert predict.clamp_value(999, "potasyum") == 500.0

    def test_clamp_bitki_sagligi_0_100(self, app_client):
        """Bitki sağlığı -10 → 0, 150 → 100."""
        _, _, predict = app_client
        assert predict.clamp_value(-10, "bitki_sagligi") == 0.0
        assert predict.clamp_value(150, "bitki_sagligi") == 100.0

    def test_clamp_bilinmeyen_alan_degismez(self, app_client):
        """Tanımlanmamış alan adı → clamp uygulanmaz."""
        _, _, predict = app_client
        assert predict.clamp_value(9999, "bilinmeyen_alan") == 9999

    # --- 11.3 validate_and_clamp() — Entegre Doğrulama ---

    def test_validate_and_clamp_normal(self, app_client):
        """Normal değer → değişmeden döner."""
        _, _, predict = app_client
        data = {"sicaklik": 25}
        assert predict.validate_and_clamp(data, "sicaklik", 20) == 25.0

    def test_validate_and_clamp_eksik_alan_default(self, app_client):
        """Eksik alan → default değer kullanılır."""
        _, _, predict = app_client
        data = {}
        assert predict.validate_and_clamp(data, "sicaklik", 20) == 20.0

    def test_validate_and_clamp_negatif_fosfor_sifira(self, app_client):
        """Negatif fosfor → 0'a clamp edilir."""
        _, _, predict = app_client
        data = {"fosfor": -30}
        assert predict.validate_and_clamp(data, "fosfor", 50) == 0.0

    def test_validate_and_clamp_string_sayi_kabul(self, app_client):
        """String olarak gelen sayı → float'a çevrilir ve clamp edilir."""
        _, _, predict = app_client
        data = {"ph": "20"}
        assert predict.validate_and_clamp(data, "ph", 6.5) == 14.0  # clamp

    def test_validate_and_clamp_hatali_string_hata(self, app_client):
        """Sayısal olmayan string → ValueError."""
        _, _, predict = app_client
        data = {"nem": "yüksek"}
        with pytest.raises(ValueError):
            predict.validate_and_clamp(data, "nem", 50)

    # --- 11.4 PARAMETRE_SINIRLARI Dict Tutarlılığı ---

    def test_tum_parametreler_sinir_tanimli(self, app_client):
        """8 sensör parametresinin tümü PARAMETRE_SINIRLARI'nda tanımlı olmalı."""
        _, _, predict = app_client
        beklenen = ["sicaklik", "nem", "toprak_nemi", "ph", "nitrojen", "fosfor", "potasyum", "bitki_sagligi"]
        for param in beklenen:
            assert param in predict.PARAMETRE_SINIRLARI, f"'{param}' PARAMETRE_SINIRLARI'nda tanımlı olmalı"

    def test_sinir_degerleri_mantikli(self, app_client):
        """Her sınır: min < max ve fiziksel olarak anlamlı olmalı."""
        _, _, predict = app_client
        for param, (min_val, max_val) in predict.PARAMETRE_SINIRLARI.items():
            assert min_val < max_val, f"{param}: min ({min_val}) < max ({max_val}) olmalı"
            assert isinstance(min_val, float), f"{param}: min float olmalı"
            assert isinstance(max_val, float), f"{param}: max float olmalı"

    # --- 11.5 Endpoint Seviyesinde Validation ---

    def test_endpoint_hatali_tip_anlamli_mesaj(self, app_client):
        """Endpoint'e hatalı tip gönderildiğinde anlamlı hata mesajı dönmeli."""
        client, _, _ = app_client
        
        response = client.post(
            "/predict",
            data=json.dumps({"sicaklik": "abc", "urun": "bugday"}),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        result = response.get_json()
        assert "sicaklik" in result["error"]
        assert "abc" in result["error"]

    def test_endpoint_liste_degeri_hata(self, app_client):
        """Endpoint'e liste gönderildiğinde hata mesajı."""
        client, _, _ = app_client
        
        response = client.post(
            "/predict",
            data=json.dumps({"fosfor": [1, 2, 3], "urun": "bugday"}),
            content_type="application/json"
        )
        
        assert response.status_code == 400
        result = response.get_json()
        assert "fosfor" in result["error"]

    def test_endpoint_clamp_sonrasi_basarili(self, app_client):
        """Aşırı değerler clamp edilir ve başarılı sonuç döner."""
        client, mock_model, _ = app_client
        mock_model.predict.return_value = np.array([[0.5]], dtype=np.float32)
        
        extreme_data = {
            "urun": "bugday",
            "sicaklik": 999,      # → clamp 60
            "nem": -50,           # → clamp 0
            "toprak_nemi": 500,   # → clamp 100
            "ph": 20,             # → clamp 14
            "nitrojen": -100,     # → clamp 0
            "fosfor": 9999,       # → clamp 500
            "potasyum": -1,       # → clamp 0
            "bitki_sagligi": 200  # → clamp 100
        }
        
        response = client.post(
            "/predict",
            data=json.dumps(extreme_data),
            content_type="application/json"
        )
        
        assert response.status_code == 200, "Clamp sonrası başarılı yanıt dönmeli"
        result = response.get_json()
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
