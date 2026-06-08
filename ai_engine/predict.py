from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import os

app = Flask(__name__)
CORS(app)  # CORS desteği

MODEL_PATH = 'tarim_modeli.keras'

# Örnek Model Yükleme veya Oluşturma
def get_or_create_model():
    if os.path.exists(MODEL_PATH):
        return tf.keras.models.load_model(MODEL_PATH)
    else:
        print("Model bulunamadı, yeni bir TensorFlow modeli oluşturuluyor ve sentetik veriyle eğitiliyor...")
        model = tf.keras.Sequential([
            tf.keras.layers.InputLayer(input_shape=(8,)),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        
        # Basit sentetik veri seti ile eğitim (Modelin rastgele sonuç üretmesini engeller)
        # Özellikler: [sicaklik, nem, toprak_nemi, ph, nitrojen, fosfor, potasyum, bitki_sagligi]
        X_dummy = np.array([
            [25.0, 50.0, 60.0, 6.5, 40.0, 50.0, 100.0, 80.0], # İdeal koşul -> 1
            [35.0, 20.0, 20.0, 5.0, 10.0, 10.0, 30.0, 30.0],  # Kötü/Kurak -> 0
            [15.0, 80.0, 85.0, 8.0, 15.0, 20.0, 40.0, 40.0],  # Kötü/Islak -> 0
            [22.0, 60.0, 55.0, 6.8, 50.0, 60.0, 120.0, 90.0]  # Çok iyi koşul -> 1
        ], dtype=np.float32)
        y_dummy = np.array([[1], [0], [0], [1]], dtype=np.float32)
        
        model.fit(X_dummy, y_dummy, epochs=15, verbose=0)
        
        model.save(MODEL_PATH)
        return model

model = get_or_create_model()

# Ürün bilgileri - ideal koşullar
URUN_BILGILERI = {
    'bugday': {'ad': 'Buğday', 'ideal_ph': (6.0, 7.5), 'ideal_nem': (40, 60), 'ideal_sicaklik': (12, 25), 'azot_ihtiyaci': 'orta', 'fosfor_ihtiyaci': 'orta', 'potasyum_ihtiyaci': 'düşük'},
    'misir': {'ad': 'Mısır', 'ideal_ph': (5.8, 7.0), 'ideal_nem': (50, 70), 'ideal_sicaklik': (20, 30), 'azot_ihtiyaci': 'yüksek', 'fosfor_ihtiyaci': 'orta', 'potasyum_ihtiyaci': 'orta'},
    'domates': {'ad': 'Domates', 'ideal_ph': (6.0, 6.8), 'ideal_nem': (60, 80), 'ideal_sicaklik': (18, 27), 'azot_ihtiyaci': 'orta', 'fosfor_ihtiyaci': 'yüksek', 'potasyum_ihtiyaci': 'yüksek'},
    'biber': {'ad': 'Biber', 'ideal_ph': (6.0, 6.8), 'ideal_nem': (55, 70), 'ideal_sicaklik': (18, 30), 'azot_ihtiyaci': 'orta', 'fosfor_ihtiyaci': 'orta', 'potasyum_ihtiyaci': 'yüksek'},
    'patlican': {'ad': 'Patlıcan', 'ideal_ph': (5.5, 6.8), 'ideal_nem': (60, 75), 'ideal_sicaklik': (20, 30), 'azot_ihtiyaci': 'yüksek', 'fosfor_ihtiyaci': 'orta', 'potasyum_ihtiyaci': 'yüksek'},
    'salatalik': {'ad': 'Salatalık', 'ideal_ph': (5.5, 7.0), 'ideal_nem': (60, 80), 'ideal_sicaklik': (18, 28), 'azot_ihtiyaci': 'orta', 'fosfor_ihtiyaci': 'orta', 'potasyum_ihtiyaci': 'orta'},
    'patates': {'ad': 'Patates', 'ideal_ph': (5.0, 6.5), 'ideal_nem': (60, 80), 'ideal_sicaklik': (15, 22), 'azot_ihtiyaci': 'yüksek', 'fosfor_ihtiyaci': 'yüksek', 'potasyum_ihtiyaci': 'yüksek'},
    'sogan': {'ad': 'Soğan', 'ideal_ph': (6.0, 7.0), 'ideal_nem': (50, 70), 'ideal_sicaklik': (13, 24), 'azot_ihtiyaci': 'orta', 'fosfor_ihtiyaci': 'orta', 'potasyum_ihtiyaci': 'orta'},
    'uzum': {'ad': 'Üzüm', 'ideal_ph': (5.5, 7.5), 'ideal_nem': (40, 60), 'ideal_sicaklik': (15, 30), 'azot_ihtiyaci': 'düşük', 'fosfor_ihtiyaci': 'orta', 'potasyum_ihtiyaci': 'yüksek'},
    'zeytin': {'ad': 'Zeytin', 'ideal_ph': (6.0, 8.0), 'ideal_nem': (35, 55), 'ideal_sicaklik': (15, 30), 'azot_ihtiyaci': 'düşük', 'fosfor_ihtiyaci': 'düşük', 'potasyum_ihtiyaci': 'orta'},
    'cay': {'ad': 'Çay', 'ideal_ph': (4.5, 6.0), 'ideal_nem': (70, 90), 'ideal_sicaklik': (14, 25), 'azot_ihtiyaci': 'yüksek', 'fosfor_ihtiyaci': 'orta', 'potasyum_ihtiyaci': 'orta'},
    'findik': {'ad': 'Fındık', 'ideal_ph': (5.5, 7.0), 'ideal_nem': (60, 80), 'ideal_sicaklik': (13, 22), 'azot_ihtiyaci': 'orta', 'fosfor_ihtiyaci': 'düşük', 'potasyum_ihtiyaci': 'orta'},
    'pamuk': {'ad': 'Pamuk', 'ideal_ph': (6.0, 8.0), 'ideal_nem': (45, 65), 'ideal_sicaklik': (20, 35), 'azot_ihtiyaci': 'yüksek', 'fosfor_ihtiyaci': 'orta', 'potasyum_ihtiyaci': 'orta'},
    'aycicegi': {'ad': 'Ayçiçeği', 'ideal_ph': (6.0, 7.5), 'ideal_nem': (40, 60), 'ideal_sicaklik': (18, 28), 'azot_ihtiyaci': 'orta', 'fosfor_ihtiyaci': 'orta', 'potasyum_ihtiyaci': 'düşük'},
    'arpa': {'ad': 'Arpa', 'ideal_ph': (6.0, 8.0), 'ideal_nem': (35, 55), 'ideal_sicaklik': (10, 22), 'azot_ihtiyaci': 'orta', 'fosfor_ihtiyaci': 'düşük', 'potasyum_ihtiyaci': 'düşük'},
    'fasulye': {'ad': 'Fasulye', 'ideal_ph': (6.0, 7.0), 'ideal_nem': (50, 70), 'ideal_sicaklik': (16, 28), 'azot_ihtiyaci': 'düşük', 'fosfor_ihtiyaci': 'orta', 'potasyum_ihtiyaci': 'orta'},
    'nohut': {'ad': 'Nohut', 'ideal_ph': (6.0, 8.0), 'ideal_nem': (30, 50), 'ideal_sicaklik': (15, 25), 'azot_ihtiyaci': 'düşük', 'fosfor_ihtiyaci': 'orta', 'potasyum_ihtiyaci': 'düşük'},
    'mercimek': {'ad': 'Mercimek', 'ideal_ph': (6.0, 8.0), 'ideal_nem': (30, 50), 'ideal_sicaklik': (12, 22), 'azot_ihtiyaci': 'düşük', 'fosfor_ihtiyaci': 'orta', 'potasyum_ihtiyaci': 'düşük'},
    'kavun': {'ad': 'Kavun', 'ideal_ph': (6.0, 7.0), 'ideal_nem': (50, 65), 'ideal_sicaklik': (22, 32), 'azot_ihtiyaci': 'orta', 'fosfor_ihtiyaci': 'orta', 'potasyum_ihtiyaci': 'yüksek'},
    'karpuz': {'ad': 'Karpuz', 'ideal_ph': (6.0, 7.0), 'ideal_nem': (50, 70), 'ideal_sicaklik': (22, 32), 'azot_ihtiyaci': 'orta', 'fosfor_ihtiyaci': 'orta', 'potasyum_ihtiyaci': 'yüksek'},
}


# ===== GİRDİ DOĞRULAMA ve CLAMP FONKSİYONU =====
# Fiziksel olarak mümkün olmayan değerleri güvenli aralıklara sınırlar
PARAMETRE_SINIRLARI = {
    'sicaklik':      (-60.0, 60.0),     # °C — dünya ekstrem sınırları
    'nem':           (0.0, 100.0),       # % — hava nemi
    'toprak_nemi':   (0.0, 100.0),       # % — toprak nemi
    'ph':            (0.0, 14.0),        # pH skalası
    'nitrojen':      (0.0, 500.0),       # mg/kg
    'fosfor':        (0.0, 500.0),       # mg/kg
    'potasyum':      (0.0, 500.0),       # mg/kg
    'bitki_sagligi': (0.0, 100.0),       # 0-100 skor
}


def safe_float(value, field_name, default):
    """Güvenli float dönüşümü — hatalı tip gelirse anlamlı hata fırlatır."""
    if value is None:
        return float(default)
    try:
        return float(value)
    except (ValueError, TypeError):
        raise ValueError(
            f"'{field_name}' alanı sayısal bir değer olmalıdır. "
            f"Gelen değer: '{value}' (tip: {type(value).__name__}). "
            f"Lütfen geçerli bir sayı gönderin."
        )


def clamp_value(value, field_name):
    """Değeri fiziksel sınırlar içine clamp eder."""
    if field_name in PARAMETRE_SINIRLARI:
        min_val, max_val = PARAMETRE_SINIRLARI[field_name]
        return max(min_val, min(max_val, value))
    return value


def validate_and_clamp(data, field_name, default):
    """Veriyi al → float'a çevir → fiziksel sınırlara clamp et."""
    raw = data.get(field_name, default)
    value = safe_float(raw, field_name, default)
    return clamp_value(value, field_name)


def analyze_conditions(data, urun):
    """Koşulları analiz edip detaylı sonuç üret.
    Girdiler validate_and_clamp ile doğrulanır ve fiziksel sınırlara clamp edilir.
    """
    urun_info = URUN_BILGILERI.get(urun, URUN_BILGILERI['bugday'])
    
    sicaklik = validate_and_clamp(data, 'sicaklik', 25)
    nem = validate_and_clamp(data, 'nem', 50)
    toprak_nemi = validate_and_clamp(data, 'toprak_nemi', 40)
    ph = validate_and_clamp(data, 'ph', 6.5)
    nitrojen = validate_and_clamp(data, 'nitrojen', 20)
    fosfor = validate_and_clamp(data, 'fosfor', 50)
    potasyum = validate_and_clamp(data, 'potasyum', 100)
    bitki_sagligi = validate_and_clamp(data, 'bitki_sagligi', 70)
    
    # Güven skoru hesaplama faktörleri
    confidence_factors = []
    warnings = []
    recommendations = []
    gubre_tavsiyeleri = []
    sulama_gerekli = False
    
    # 1. Sıcaklık analizi
    ideal_min, ideal_max = urun_info['ideal_sicaklik']
    if ideal_min <= sicaklik <= ideal_max:
        confidence_factors.append(('Sıcaklık ideal aralıkta', 1.0))
        recommendations.append(f'Mevcut sıcaklık ({sicaklik}°C), {urun_info["ad"]} yetiştiriciliği için ideal aralıktadır ({ideal_min}-{ideal_max}°C). Bu koşullarda bitkinin fotosentez aktivitesi ve büyüme hızı optimum seviyededir. Mevsim boyunca bu sıcaklık aralığında kalmaya devam edilmesi durumunda verim artışı beklenir.')
    elif sicaklik < ideal_min:
        diff = ideal_min - sicaklik
        score = max(0.3, 1.0 - diff * 0.05)
        confidence_factors.append((f'Sıcaklık idealin {diff:.0f}°C altında', score))
        warnings.append(f'Sıcaklık {urun_info["ad"]} için düşük ({sicaklik}°C). İdeal: {ideal_min}-{ideal_max}°C')
        if diff > 10:
            recommendations.append(f'🔴 KRİTİK: Sıcaklık, {urun_info["ad"]} için çok düşük ({sicaklik}°C). Bu seviyede don riski yüksektir ve bitki gelişimi ciddi şekilde yavaşlar. Sera veya tünel tipi örtü altı yetiştiricilik uygulanması şiddetle tavsiye edilir. Açık alanda ise mulçlama (toprak örtme) ile kök bölgesinin korunması ve don örtüsü kullanılması gerekmektedir.')
        elif diff > 5:
            recommendations.append(f'⚠️ Sıcaklık {urun_info["ad"]} için idealin {diff:.0f}°C altında. Agril veya zirai don örtüsü kullanarak bitkileri koruma altına alınız. Sabah saatlerinde sisli havada don oluşumu riski artmaktadır. Tünel tipi basit sera sistemleri 3-5°C ek sıcaklık sağlayabilir.')
        else:
            recommendations.append(f'Sıcaklık {urun_info["ad"]} için biraz düşük ({sicaklik}°C). En az {ideal_min}°C gereklidir. Geçici olarak agril örtü kullanabilir veya ekim zamanını öne alarak havaların ısınmasını bekleyebilirsiniz. Fide dikimi planlıyorsanız, gece sıcaklıklarının {ideal_min}°C üzerine çıkmasını bekleyin.')
    else:
        diff = sicaklik - ideal_max
        score = max(0.3, 1.0 - diff * 0.05)
        confidence_factors.append((f'Sıcaklık idealin {diff:.0f}°C üstünde', score))
        warnings.append(f'Sıcaklık {urun_info["ad"]} için yüksek ({sicaklik}°C). İdeal: {ideal_min}-{ideal_max}°C')
        if diff > 10:
            recommendations.append(f'🔴 KRİTİK: Aşırı sıcaklık ({sicaklik}°C)! {urun_info["ad"]} bitkisinde yaprak yanığı, çiçek dökülmesi ve meyve kalitesinde ciddi düşüş riski vardır. Gölgeleme ağları (%40-60 gölgeleme oranı) kurulmalı, sulama sabah 06:00 öncesi ve akşam 19:00 sonrası yapılmalıdır. Yaprak yüzeyine serin su püskürtmesi yapılabilir.')
        elif diff > 5:
            recommendations.append(f'⚠️ Sıcaklık {urun_info["ad"]} için oldukça yüksek ({sicaklik}°C). Gölgeleme önlemleri alın ve sulama sıklığını %30-50 artırın. Buharlaşma kaybını azaltmak için malçlama yapılması önerilir. Ayrıca yaprak gübrelemesi yerine damla sulama ile kök bölgesinden besleme tercih edin.')
        else:
            recommendations.append(f'Sıcaklık {urun_info["ad"]} için biraz yüksek ({sicaklik}°C). Sulama sıklığını hafif artırarak toprak sıcaklığını düşürebilirsiniz. Organik malçlama (saman, yaprak örtüsü) toprak nemini koruyarak kök bölgesini serinletir.')
        sulama_gerekli = True  # Yüksek sıcaklıkta sulama ihtiyacı artar
    
    # 2. pH analizi
    ph_min, ph_max = urun_info['ideal_ph']
    if ph_min <= ph <= ph_max:
        confidence_factors.append(('Toprak pH ideal aralıkta', 1.0))
        recommendations.append(f'Toprağın pH değeri ({ph}) {urun_info["ad"]} için ideal aralıktadır ({ph_min}-{ph_max}). Bu pH seviyesinde besin elementlerinin yarayışlılığı (özellikle azot, fosfor ve mikro elementler) en üst düzeydedir. Her sezon başında toprak analizi yaptırarak bu değeri takip etmeniz önerilir.')
    elif ph < ph_min:
        score = max(0.4, 1.0 - (ph_min - ph) * 0.15)
        confidence_factors.append((f'Toprak pH düşük ({ph})', score))
        warnings.append(f'Toprak pH değeri düşük ({ph}). İdeal: {ph_min}-{ph_max}')
        fark = ph_min - ph
        recommendations.append(f'Toprak asitliği {urun_info["ad"]} için idealin altında (pH {ph}). Asitli toprakta alüminyum ve mangan toksisitesi riski artar, fosfor bağlanarak bitkiye yarayışsız hale gelir. Kireçleme ile pH yükseltilmeli, sonbahar aylarında dekara 200-400 kg tarım kireci (CaCO3) serpilip toprağa karıştırılmalıdır. Kireçleme etkisi 2-3 yıl sürer, bu sürede yıllık pH takibi önerilir.')
        gubre_tavsiyeleri.append(f'Kireçleme önerilir: pH değerini {ph} seviyesinden {ph_min} seviyesine çıkarmak için dekara yaklaşık {int(fark * 250)} kg tarım kireci (CaCO3) uygulanmalıdır. Uygulama sonbahar veya kış aylarında, toprak işleme öncesinde yapılmalıdır. Kireçlemenin etkili olabilmesi için toprağın nemli olması gerekir.')
    else:
        score = max(0.4, 1.0 - (ph - ph_max) * 0.15)
        confidence_factors.append((f'Toprak pH yüksek ({ph})', score))
        warnings.append(f'Toprak pH değeri yüksek ({ph}). İdeal: {ph_min}-{ph_max}')
        recommendations.append(f'Toprak alkaliliği {urun_info["ad"]} için idealin üzerinde (pH {ph}). Yüksek pH\'da demir, çinko, mangan ve bor gibi mikro besin elementlerinin alımı zorlaşır, yaprak sararması (kloroz) görülebilir. pH düşürmek için elementel kükürt veya amonyum sülfat gübresi kullanılabilir. Ayrıca organik madde (çiftlik gübresi, kompost) ilavesi toprak tampon kapasitesini artırarak pH dengelenmesine yardımcı olur.')
        gubre_tavsiyeleri.append(f'Kükürt uygulaması: Dekara 30-50 kg elementel kükürt uygulanarak pH düşürülebilir. Alternatif olarak amonyum sülfat (%21 N) gübresi hem azot takviyesi yapar hem de asitleştirici etkisiyle pH\'ı düşürmeye yardımcı olur.')
    
    # 3. Toprak nemi analizi — SULAMA KARARI BURADA VERİLİR (kural-tabanlı)
    nem_min, nem_max = urun_info['ideal_nem']
    if nem_min <= toprak_nemi <= nem_max:
        confidence_factors.append(('Toprak nemi yeterli', 1.0))
        recommendations.append(f'Toprak nemi (%{toprak_nemi:.0f}) {urun_info["ad"]} için ideal aralıktadır (%{nem_min}-%{nem_max}). Mevcut sulama programınıza devam edin. Toprak nemini korumak için malçlama (organik örtü) uygulaması yapabilirsiniz; bu yöntem buharlaşmayı %25-30 oranında azaltır.')
    elif toprak_nemi < nem_min:
        score = max(0.3, 1.0 - (nem_min - toprak_nemi) * 0.02)
        confidence_factors.append((f'Toprak nemi düşük (%{toprak_nemi:.0f})', score))
        warnings.append(f'Toprak nemi yetersiz (%{toprak_nemi:.0f}). İdeal: %{nem_min}-%{nem_max}')
        sulama_gerekli = True  # TOPRAK NEMİ DÜŞÜK → SULAMA GEREKLİ
        eksik = nem_min - toprak_nemi
        if eksik > 30:
            recommendations.append(f'🔴 KRİTİK SULAMA İHTİYACI: Toprak nemi çok düşük (%{toprak_nemi:.0f}), {urun_info["ad"]} için minimum %{nem_min} gereklidir. Acil sulama yapılmalıdır. Kök bölgesinin tamamen kuruması durumunda bitki kalıcı solgunluk evresine girer ve telafisi güçleşir. Damla sulama ile kademeli olarak nem seviyesini artırın, ani su baskınından kaçının. Sabah erken saatlerde sulama yapılması buharlaşma kaybını en aza indirir.')
        elif eksik > 15:
            recommendations.append(f'⚠️ Toprak nemi düşük (%{toprak_nemi:.0f}). {urun_info["ad"]} ideal nem aralığı %{nem_min}-%{nem_max} olup sulama yapılması gerekmektedir. Damla sulama sistemi kullanıyorsanız süreyi %50 artırın. Yağmurlama sulama yapıyorsanız sabah 06:00-08:00 arası veya akşam 18:00-20:00 arası uygulayın. Sulama sonrası malçlama yaparak nemin korunmasını sağlayın.')
        else:
            recommendations.append(f'Toprak nemi hafif düşük (%{toprak_nemi:.0f}), {urun_info["ad"]} için %{nem_min} seviyesine çıkarılması önerilir. Damla sulama ile kademeli nem artışı sağlayabilirsiniz. Hava durumuna göre yakın zamanda yağış bekleniyorsa sulamayı erteleyebilirsiniz.')
    else:
        score = max(0.5, 1.0 - (toprak_nemi - nem_max) * 0.02)
        confidence_factors.append((f'Toprak nemi yüksek (%{toprak_nemi:.0f})', score))
        warnings.append(f'Toprak nemi fazla (%{toprak_nemi:.0f}). Kök çürümesi riski var.')
        fazla = toprak_nemi - nem_max
        if fazla > 20:
            recommendations.append(f'🔴 KRİTİK: Toprak nemi aşırı yüksek (%{toprak_nemi:.0f}). {urun_info["ad"]} için maximum %{nem_max} olmalıdır. Kök çürümesi (Phytophthora, Pythium) ve toprak kaynaklı mantar hastalıkları riski çok yüksektir. Sulamayı derhal durdurun, drenaj kanallarını kontrol edin. Tarlada su birikintisi varsa kanal açarak tahliye edin. Tarlaya biyolojik fungisit (Trichoderma harzianum) uygulaması yapılabilir.')
        else:
            recommendations.append(f'Toprak nemi biraz yüksek (%{toprak_nemi:.0f}). {urun_info["ad"]} için ideal üst sınır %{nem_max} olup sulamayı kısa süreli durdurun. Drenaj sisteminizi kontrol edin ve toprak havalandırması için yüzeysel çapalama yapın. Aşırı nem mantari hastalıklara (külleme, mildiyö) zemin hazırlar.')
    
    # 4. Azot analizi
    azot_esik = {'düşük': 20, 'orta': 40, 'yüksek': 60}
    azot_ihtiyac = azot_esik.get(urun_info['azot_ihtiyaci'], 40)
    if nitrojen >= azot_ihtiyac:
        confidence_factors.append(('Azot seviyesi yeterli', 1.0))
        recommendations.append(f'{urun_info["ad"]} için azot (N) seviyesi yeterlidir ({nitrojen} mg/kg). Aşırı azot uygulamasından kaçının; fazla azot vejetatif büyümeyi artırıp meyve/tohum oluşumunu geciktirebilir ve çevresel kirliliğe yol açabilir.')
    else:
        score = max(0.4, nitrojen / azot_ihtiyac)
        confidence_factors.append((f'Azot seviyesi düşük ({nitrojen} mg/kg)', score))
        eksik_oran = round((1 - nitrojen / azot_ihtiyac) * 100)
        gubre_tavsiyeleri.append(f'Azotlu gübre önerilir: Mevcut azot seviyesi ({nitrojen} mg/kg) {urun_info["ad"]} ihtiyacının %{eksik_oran} altındadır. Amonyum sülfat (%21 N) dekara 25-40 kg veya üre (%46 N) dekara 12-20 kg uygulanması tavsiye edilir. {urun_info["ad"]} için azot ihtiyacı "{urun_info["azot_ihtiyaci"]}" düzeydedir. Uygulamayı ikiye bölerek (ekim/dikim + büyüme dönemi) yapmanız verimi artırır.')
        recommendations.append(f'Azot eksikliği tespit edildi. Azot eksikliğinin belirtileri: alt yaprakların sararması, genel büyüme yavaşlaması ve bitkide cılız görünüm. Azot, klorofil sentezi ve protein oluşumu için kritik bir elementtir.')
    
    # 5. Fosfor analizi
    fosfor_esik = {'düşük': 25, 'orta': 50, 'yüksek': 75}
    fosfor_ihtiyac = fosfor_esik.get(urun_info['fosfor_ihtiyaci'], 50)
    if fosfor >= fosfor_ihtiyac:
        confidence_factors.append(('Fosfor seviyesi yeterli', 1.0))
    else:
        score = max(0.4, fosfor / fosfor_ihtiyac)
        confidence_factors.append((f'Fosfor seviyesi düşük ({fosfor} mg/kg)', score))
        eksik_oran = round((1 - fosfor / fosfor_ihtiyac) * 100)
        gubre_tavsiyeleri.append(f'Fosforlu gübre önerilir: Mevcut fosfor seviyesi ({fosfor} mg/kg) {urun_info["ad"]} ihtiyacının %{eksik_oran} altındadır. Triple Süper Fosfat (TSP, %46 P2O5) dekara 15-25 kg veya DAP (Diamonyum Fosfat, %18N + %46P) dekara 20-30 kg uygulanması tavsiye edilir. Fosfor toprakta hareketsiz olduğundan ekim/dikim öncesi toprağa karıştırılmalıdır.')
        recommendations.append(f'Fosfor eksikliği tespit edildi. Fosfor, kök gelişimi, çiçeklenme ve tohum/meyve oluşumu için hayati önem taşır. Eksikliğinde yapraklarda morumsu renk değişimi, kök gelişiminde yavaşlama ve geç olgunlaşma görülebilir.')
    
    # 6. Potasyum analizi
    potasyum_esik = {'düşük': 80, 'orta': 130, 'yüksek': 180}
    potasyum_ihtiyac = potasyum_esik.get(urun_info['potasyum_ihtiyaci'], 130)
    if potasyum >= potasyum_ihtiyac:
        confidence_factors.append(('Potasyum seviyesi yeterli', 1.0))
    else:
        score = max(0.4, potasyum / potasyum_ihtiyac)
        confidence_factors.append((f'Potasyum seviyesi düşük ({potasyum} mg/kg)', score))
        eksik_oran = round((1 - potasyum / potasyum_ihtiyac) * 100)
        gubre_tavsiyeleri.append(f'Potasyumlu gübre önerilir: Mevcut potasyum seviyesi ({potasyum} mg/kg) {urun_info["ad"]} ihtiyacının %{eksik_oran} altındadır. Potasyum sülfat (K2SO4, %50 K2O) dekara 20-35 kg uygulanması tavsiye edilir. Potasyum, bitkinin kuraklık ve hastalıklara dayanıklılığını artırır, meyve kalitesini ve raf ömrünü iyileştirir.')
        recommendations.append(f'Potasyum eksikliği tespit edildi. Potasyum eksikliğinde yaprak kenarlarında kahverengileşme ve kuruma, meyvede renk bozukluğu ve tat kaybı, bitkide kuraklığa ve hastalıklara karşı duyarlılık artışı gözlenir.')
    
    # 7. Bitki sağlığı
    if bitki_sagligi >= 70:
        confidence_factors.append(('Bitki sağlığı iyi', 1.0))
        recommendations.append(f'Bitki sağlık skoru ({bitki_sagligi}/100) iyi durumda. Düzenli gözlem ve koruyucu zirai ilaçlama programına devam edin. Entegre zararlı yönetimi (IPM) ilkeleri doğrultusunda, biyolojik mücadele yöntemlerini (faydalı böcekler, biyolojik preparatlar) tercih etmeniz hem çevre hem de maliyet açısından avantajlıdır.')
    elif bitki_sagligi >= 40:
        score = bitki_sagligi / 100
        confidence_factors.append((f'Bitki sağlığı orta ({bitki_sagligi}/100)', score))
        warnings.append(f'Bitki sağlık skoru orta seviyede ({bitki_sagligi}/100).')
        recommendations.append(f'Bitki sağlığı orta seviyede ({bitki_sagligi}/100). Zararlı böcek ve hastalık belirtileri açısından yaprakları, gövdeyi ve kök bölgesini detaylı inceleyin. Yapraklarda lekeler, sararma veya deformasyonlar hastalık işareti olabilir. Gerekirse ziraat mühendisinden numune analizi yaptırın. Koruyucu bakır içerikli (bordo bulamacı) veya kükürt bazlı ilaçlama düşünülebilir.')
    else:
        score = max(0.2, bitki_sagligi / 100)
        confidence_factors.append((f'Bitki sağlığı düşük ({bitki_sagligi}/100)', score))
        warnings.append(f'Bitki sağlık skoru kritik düzeyde düşük ({bitki_sagligi}/100)!')
        recommendations.append(f'🔴 KRİTİK: Bitki sağlığı çok düşük ({bitki_sagligi}/100)! Acil müdahale gereklidir. Yapraklarda, gövdede ve meyvede hastalık belirtilerini fotoğrafla belgeleyerek en yakın Tarım İl Müdürlüğü veya ziraat mühendisine danışın. Hastalıklı bitki parçalarını tarladan uzaklaştırın (yakın veya gömün). Bulaşmanın yayılmaması için hastalıklı bitkiler arasında kullandığınız aletleri %10 çamaşır suyu çözeltisiyle dezenfekte edin.')
    
    # Gübre tavsiyesi yoksa
    if not gubre_tavsiyeleri:
        gubre_tavsiyeleri.append(f'{urun_info["ad"]} için mevcut toprak besin değerleri (N: {nitrojen}, P: {fosfor}, K: {potasyum} mg/kg) yeterli görünmektedir. Düzenli toprak analizi yaptırmaya devam edin. Her sezon başında ve ortasında toprak numunesi alarak besin seviyelerini takip etmeniz, aşırı gübrelemeyi önler ve maliyetlerinizi düşürür.')
    
    # Ek genel öneriler — mevsimsel ve hava durumuna dayalı
    if nem > 80:
        recommendations.append(f'Hava nemi çok yüksek (%{nem}). Mantar hastalıklarına (külleme, mildiyö, botrytis) karşı dikkatli olun. Bitki sıklığını azaltarak hava sirkülasyonunu iyileştirin. Koruyucu fungisit uygulaması düşünülebilir. Seradaysa havalandırma fanlarını çalıştırın.')
    elif nem > 65:
        recommendations.append(f'Hava nemi (%{nem}) orta-yüksek seviyede. Mantar hastalıkları açısından düzenli gözlem yapın. Bitkilerin altından (damlama ile) sulama yaparak yaprak ıslaklığını minimize edin.')
    
    if sicaklik > 35:
        recommendations.append(f'🌡️ Aşırı sıcaklık uyarısı ({sicaklik}°C)! Sabah erken (06:00 öncesi) veya akşam geç (19:00 sonrası) saatlerde sulama yapın. Gün ortasında sulama yapmak buharlaşma kaybını artırır ve yaprak yanıklarına neden olabilir. Gölgeleme ağı kullanımı bitki stresini %30-40 azaltabilir.')
    
    if sicaklik < 5:
        recommendations.append(f'❄️ Don tehlikesi uyarısı ({sicaklik}°C)! Hassas bitkileri don örtüsüyle koruyun. Rüzgarlı havalarda don riski daha da artar. Toprak yüzeyinin nemli tutulması (ısı kapasitesi artışı) hafif donlara karşı koruma sağlayabilir.')
    
    # Toplam güven skoru
    total_score = sum(s for _, s in confidence_factors) / len(confidence_factors)
    
    return {
        'confidence_factors': [{'factor': f, 'score': round(s, 2)} for f, s in confidence_factors],
        'warnings': warnings,
        'recommendations': recommendations,
        'gubre_tavsiyeleri': gubre_tavsiyeleri,
        'overall_score': round(total_score, 2),
        'urun_ad': urun_info['ad'],
        'sulama_gerekli': sulama_gerekli
    }


# Sağlık kontrolü endpoint'i
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "online",
        "model_loaded": model is not None,
        "tensorflow_version": tf.__version__,
        "ai_technology": "TensorFlow/Keras Sequential Neural Network"
    })


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if data is None:
            return jsonify({
                "error": "Geçersiz istek: JSON body boş veya hatalı.",
                "detail": "Content-Type: application/json header'ı ile geçerli JSON gönderin."
            }), 400
        
        print("Gelen veri:", data)
        
        urun = data.get('urun', 'bugday')
        
        # Girdi doğrulama ve fiziksel sınırlara clamp
        features = [
            validate_and_clamp(data, 'sicaklik', 25.0),
            validate_and_clamp(data, 'nem', 50.0),
            validate_and_clamp(data, 'toprak_nemi', 40.0),
            validate_and_clamp(data, 'ph', 6.5),
            validate_and_clamp(data, 'nitrojen', 20.0),
            validate_and_clamp(data, 'fosfor', 50.0),
            validate_and_clamp(data, 'potasyum', 100.0),
            validate_and_clamp(data, 'bitki_sagligi', 70.0)
        ]
        
        input_data = np.array([features], dtype=np.float32)
        
        # TensorFlow modeline tahmin yaptırma
        tf_prediction = model.predict(input_data)
        tf_confidence = float(tf_prediction[0][0])
        
        # Detaylı analiz (aynı validate_and_clamp içeride de kullanılıyor)
        analysis = analyze_conditions(data, urun)
        
        # Sulama kararı: kural-tabanlı (toprak nemi ve sıcaklığa dayalı)
        sulama_gerekli = analysis.get('sulama_gerekli', False)
        if sulama_gerekli:
            sulama_durumu = "Sulama yapılması önerilir."
        else:
            sulama_durumu = "Sulama gerekmiyor, mevcut toprak nemi yeterli düzeydedir."
        
        # Detaylı genel değerlendirme özeti
        ozet_parts = []
        
        # Uygunluk durumuna göre özet
        skor = analysis['overall_score']
        if skor >= 0.85:
            ozet_parts.append(f"{analysis['urun_ad']} için mevcut koşullar oldukça uygun görünmektedir (Genel Uygunluk: %{round(skor*100)}).")
        elif skor >= 0.65:
            ozet_parts.append(f"{analysis['urun_ad']} için koşullar kısmen uygun ancak bazı iyileştirmeler gereklidir (Genel Uygunluk: %{round(skor*100)}).")
        elif skor >= 0.45:
            ozet_parts.append(f"{analysis['urun_ad']} için koşullar orta düzeyde, dikkat edilmesi gereken noktalar mevcut (Genel Uygunluk: %{round(skor*100)}).")
        else:
            ozet_parts.append(f"{analysis['urun_ad']} için mevcut koşullar uygun değil, acil müdahale önerilir (Genel Uygunluk: %{round(skor*100)}).")
        
        ozet_parts.append(sulama_durumu)
        
        if analysis['warnings']:
            ozet_parts.append(f"{len(analysis['warnings'])} adet uyarı tespit edildi, detayları inceleyiniz.")
        if len(analysis['gubre_tavsiyeleri']) > 1 or (len(analysis['gubre_tavsiyeleri']) == 1 and 'yeterli' not in analysis['gubre_tavsiyeleri'][0]):
            ozet_parts.append("Gübreleme tavsiyesi mevcut, aşağıdaki önerileri dikkate alınız.")
        ozet = ' '.join(ozet_parts)
        
        result = {
            "prediction": sulama_durumu,
            "ozet": ozet,
            "confidence": round(analysis['overall_score'], 2),
            "tf_confidence": round(tf_confidence, 2),
            "confidence_factors": analysis['confidence_factors'],
            "warnings": analysis['warnings'],
            "recommendations": analysis['recommendations'],
            "gubre_tavsiyeleri": analysis['gubre_tavsiyeleri'],
            "urun_ad": analysis['urun_ad'],
            "sulama_gerekli": sulama_gerekli,
            "ai_technology": {
                "model": "TensorFlow v" + tf.__version__,
                "type": "Keras Sequential Neural Network",
                "layers": "InputLayer(8) → Dense(16, ReLU) → Dense(1, Sigmoid)",
                "description": "8 girdi özelliğini (sıcaklık, nem, toprak nemi, pH, azot, fosfor, potasyum, bitki sağlığı) değerlendiren yapay sinir ağı modeli ve kural tabanlı uzman sistemin birleştirilmiş analizi"
            }
        }
        
        return jsonify(result)

    except ValueError as e:
        return jsonify({
            "error": str(e),
            "tip": "Girdi doğrulama hatası. Lütfen tüm alanların sayısal değer olduğundan emin olun."
        }), 400
    except Exception as e:
        return jsonify({"error": f"Beklenmeyen hata: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
