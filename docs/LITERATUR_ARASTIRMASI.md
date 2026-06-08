# Akıllı Tarım Destek Sistemi — Literatür Araştırması

**Proje:** Akıllı Tarım Destek Sistemi  
**Grup:** Yapay Zeka Yoldaşları  
**Hazırlayan:** MERYEM ABDURRAHMAN (250541605@firat.edu.tr)  
**Tarih:** Mayıs 2026  
**Sürüm:** 1.0  

---

## 1. Giriş

Bu belge, Akıllı Tarım Destek Sistemi projesinin akademik ve teknik temelini oluşturmak amacıyla gerçekleştirilen literatür araştırmasının sonuçlarını içermektedir. Araştırma; akademik makaleler, bilimsel dergiler ve güvenilir teknik kaynaklar taranarak hazırlanmıştır. Proje kapsamında hava durumu, toprak analizi ve bitki sağlığı verilerini kullanarak çiftçilere ekim zamanı ve gübreleme önerileri sunan yapay zeka tabanlı bir sistem geliştirilmesi hedeflenmektedir.

---

## 2. Tarımda Yapay Zeka: Genel Durum

Yapay zeka ve makine öğrenmesi teknolojileri, tarım sektöründe hızla yaygınlaşmaktadır. Küresel ölçekte tarımda yapay zeka uygulamalarının pazar büyüklüğü 2023 yılında 1,7 milyar dolar olup 2028'e kadar yaklaşık 4,7 milyar dolara ulaşması beklenmektedir. Bu sistemler sayesinde ürün seçimi, verim tahmini, hastalık teşhisi, hava durumu tahmini ve akıllı sulama gibi işlemler çok daha verimli hale gelmiştir.

Çakmakçı ve Çakmakçı (2023), uzaktan algılama ve yapay zekanın akıllı tarım teknolojilerinin geleceğini şekillendirdiğini vurgulamaktadır. Tarım 4.0 olarak adlandırılan bu dönüşüm; sensör teknolojileri, makine öğrenmesi, otomasyon ve robotik sistemleri kapsamaktadır.

---

## 3. Ekim Önerisi ve Ürün Tahmin Sistemleri

Literatürde ekim önerisi sistemleri, toprak özellikleri ve iklim verilerini bir araya getiren makine öğrenmesi modelleri üzerine yoğunlaşmaktadır.

### 3.1 Kullanılan Algoritmalar

| Algoritma | Kullanım Alanı | Kaynak |
|---|---|---|
| Random Forest | Ekim önerisi, toprak analizi | Scientific Reports, 2025 |
| XGBoost | Ürün verimi tahmini | ScienceDirect, 2024 |
| SVM (Destek Vektör Makinesi) | Yağış tahmini | IJSAT, 2025 |
| Karar Ağaçları (Decision Tree) | Ürün verimi tahmini | MDPI, 2024 |
| Naive Bayes | Hava koşulu tabanlı tahmin | MDPI, 2024 |
| Derin Öğrenme (CNN/LSTM) | Bitki hastalığı tespiti | Nature, 2025 |

### 3.2 Önemli Bulgular

Nature dergisinde yayımlanan bir çalışmada (2025), denetimli makine öğrenmesi ve Açıklanabilir Yapay Zeka (XAI) yöntemlerini birleştiren bir ekim öneri sistemi **%99.27 doğruluk oranına** ulaşmıştır.

MDPI'da yayımlanan başka bir çalışmada (2024), Random Forest, SVM ve Karar Ağaçları algoritmalarının toprak özellikleri (N, P, K, pH) ve hava durumu verileriyle birlikte kullanılmasının ekim tavsiye sistemlerinin doğruluğunu önemli ölçüde artırdığı gösterilmiştir.

---

## 4. Toprak Analizi ve Veri Kaynakları

| Veri Kategorisi | Parametreler |
|---|---|
| Toprak Özellikleri | pH, nem, N-P-K seviyeleri, elektriksel iletkenlik, toprak rengi |
| İklim Verileri | Sıcaklık (min/max), yağış, nem, rüzgar hızı, bulut örtüsü |
| Konum Bilgisi | Enlem, boylam koordinatları |
| Ürün Geçmişi | Geçmiş yıl verim verileri, ekim türleri |

---

## 5. IoT ve Bulut Teknolojilerinin Rolü

Küresel IoT cihaz sayısı 2015'teki 3.6 milyardan 2024'te 18.6 milyara yükselmiştir. Tarımda IoT; sensörler, kameralar, kızılötesi cihazlar ve insansız hava araçları aracılığıyla gerçek zamanlı veri toplanmasını sağlamaktadır. Bu veriler bulut ortamında işlenerek çiftçilere anlık öneriler sunulmaktadır.

---

## 6. Projeye Katkısı

Bu literatür araştırması, Akıllı Tarım Destek Sistemi'nin tasarımında aşağıdaki vizyon ve kararların alınmasına temel oluşturmaktadır:

- **Algoritma seçimi (Gelecek Sürüm):** İlerleyen versiyonlarda Random Forest ve XGBoost gibi gelişmiş makine öğrenmesi algoritmaları kullanılarak veri setlerinin eğitilmesi hedeflenmektedir. (v1.0 sürümünde kural tabanlı uzman sistem ve Keras Sinir Ağı prototipi kullanılmaktadır).
- **Veri parametreleri:** Toprak pH, N-P-K, nem ve hava durumu verileri sistemin ana girdilerini oluşturmaktadır.
- **Altyapı (Gelecek Sürüm):** Tam otonom bulut tabanlı veri işleme ve IoT entegrasyonu (sensörlerden otomatik veri çekme) sistemin nihai amacıdır.
- **Doğruluk hedefi:** Gerçek veritabanı olgunlaştığında literatürdeki %99+ doğruluk oranlarına ulaşılması hedeflenmektedir.

---

## 7. Kaynaklar

1. Çakmakçı, M. F. ve Çakmakçı, R. (2023). Uzaktan algılama, yapay zekâ ve geleceğin akıllı tarım teknolojisi trendleri. *Avrupa Bilim ve Teknoloji Dergisi*, Sayı 52, s.234-246.
2. Gyamfi, E. K., ElSayed, Z., Kropczynski, J. ve diğerleri. (2024). Agricultural 4.0 Leveraging on Technological Solutions. *arXiv preprint arXiv:2401.00814*.
3. Karadeniz, A. T. (2024). Tarımda AI kullanımı. *AgriTR Science*, 6(2), 145-152.
4. Ryan, M., Isakhanyan, G. & Tekinerdogan, B. (2023). An interdisciplinary approach to artificial intelligence in agriculture. *NJAS: Impact in Agricultural and Life Sciences*, 95(1).
5. Şahin, H. (2024). Tarımsal Akıllı Sulama Sistemlerinde Yapay Zekâ, Derin Öğrenme ve Nesnelerin İnterneti Uygulamaları. *Tarım Makinaları Bilimi Dergisi*, 20(1), 41-60.
6. Scientific Reports. (2025). Advancing crop recommendation system with supervised machine learning and explainable artificial intelligence. *Nature Publishing Group*.
7. MDPI Engineering Proceedings. (2024). A Machine Learning-Enabled System for Crop Recommendation. doi:10.3390/engproc2024067051
8. ScienceDirect. (2024). Machine learning based recommendation using NPK, soil pH and climatic variables. *Heliyon*, 10(3).
9. ScienceDirect. (2025). An IoT-enabled AI system for real-time crop prediction using soil and weather data.
10. TÜBİTAK Bilim Genç. (2025). Tarımda Yapay Zekâ. https://bilimgenc.tubitak.gov.tr/makale/tarimda-yapay-zeka

---

## Sürüm Geçmişi

| Sürüm | Tarih | Yazar | Değişiklik |
|---|---|---|---|
| 1.0 | 2026-05 | Meryem Abdurrahman | İlk oluşturma |
