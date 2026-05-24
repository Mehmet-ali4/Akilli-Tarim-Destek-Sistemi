# Akıllı Tarım Destek Sistemi - Veri Ön İşleme Raporu

Makine öğrenmesi algoritmalarının doğru ve kararlı çalışabilmesi için sistemimize gelen ham sensör verilerine aşağıdaki ön işleme (preprocessing) adımları uygulanmıştır:

## 1. Eksik Veri Tamamlama (Imputation)
Sensör bağlantı kopuklukları veya gecikmelerden kaynaklı oluşan boş (`NULL` / `NaN`) değerler saptanmıştır.
- **Yöntem:** Eksik değerler, veri setindeki ilgili kolonun **Medyan (Ortanca)** değeri ile doldurulmuştur.
- **Neden Ortalama Değil?** İçeride bulunabilecek aşırı yüksek/düşük aykırı değerlerin ortalamayı bozarak modeli yanıltmasını engellemek için medyan tercih edilmiştir.

## 2. Aykırı Değer Tespiti ve Temizlenmesi (Outlier Detection)
Aykırı değerler iki aşamalı bir filtreden geçirilmiştir:

### A. Domain Mantık Sınırları (Clipping)
`api-tasarim.md` dosyasında belirtilen veri doğrulama (Data Validation) kuralları uygulanmıştır:
- Sıcaklık: `-50°C` ile `+70°C` arası
- Nem ve Toprak Nemi: `%0` ile `%100` arası
- pH Seviyesi: `0` ile `14` arası
Bu sınırların dışındaki imkansız değerler, bu üst ve alt sınırlara çekilmiştir (Clipping).

### B. İstatistiksel IQR (Interquartile Range) Yöntemi
Fiziksel olarak mümkün olsa da istatistiksel dağılımı bozan değerler için **Winsorization** tekniği uygulanmıştır. Çeyreklik değerler (Q1 ve Q3) hesaplanmış, `1.5 * IQR` formülü ile üst ve alt sınırlar belirlenerek sapan değerler bu sınırlara eşitlenmiştir. Veri kaybı yaşamamak adına satır silme (drop) işlemi yapılmamıştır.

**İlgili Kod:** `ai_engine/veri_onisleme.py`
