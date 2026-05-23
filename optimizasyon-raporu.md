# Akıllı Tarım Destek Sistemi - Model Optimizasyon Raporu

Gereksinim belgelerinde belirtilen "Çiftçiye eylem önerisinde bulunma (Sulama Yap, vb.)" hedefine ulaşmak için sistem bir Sınıflandırma (Classification) problemi olarak ele alınmıştır.

## 1. Algoritma Karşılaştırması
Sistemin en doğru kararı verebilmesi için veriler üzerinde 3 farklı makine öğrenmesi algoritması test edilmiştir:
- Logistic Regression
- Support Vector Machine (SVM)
- Random Forest Classifier

**Sonuç:** Tablosal sensör verilerindeki ve kurallardaki yüksek başarı oranı sebebiyle **Random Forest** ana algoritma olarak seçilmiştir.

## 2. Model Optimizasyonu (Hyperparameter Tuning)
Seçilen Random Forest modelinin performansını maksimize etmek ve ezberlemeyi (overfitting) önlemek için **GridSearchCV** tekniği uygulanmıştır. 
Modelin parametreleri (`n_estimators`, `max_depth`, `min_samples_split`) farklı kombinasyonlarla çapraz doğrulamadan (Cross-Validation) geçirilerek en ideal konfigürasyon tespit edilmiştir.

**İlgili Kod:** `ai_engine/model_optimizasyon.py`
