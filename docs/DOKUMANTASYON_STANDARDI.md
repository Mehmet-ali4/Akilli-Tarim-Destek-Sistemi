# Akıllı Tarım Destek Sistemi — Dokümantasyon Standardı

**Proje:** Akıllı Tarım Destek Sistemi  
**Grup:** Yapay Zeka Yoldaşları  
**Hazırlayan:** MERYEM ABDURRAHMAN (250541605@firat.edu.tr)  
**Tarih:** Mayıs 2026  
**Sürüm:** 1.0  

---

## 1. Amaç

Bu belge, proje boyunca üretilecek tüm dokümanların (gereksinimler, tasarım, test senaryoları, kullanıcı kılavuzları vb.) tutarlı ve erişilebilir olmasını sağlamak amacıyla oluşturulmuş bir standart kılavuzdur. Tüm ekip üyeleri bu standarda uymakla yükümlüdür.

---

## 2. Doküman Türleri

| Doküman Türü | Açıklama | Sorumlu |
|---|---|---|
| Gereksinim Belgesi | Sistem gereksinimlerini tanımlar | Tüm ekip |
| Tasarım Belgesi | Mimari ve teknik tasarımı açıklar | Yazılım Mühendisleri |
| Test Senaryoları | Test adımlarını ve beklenen sonuçları içerir | Yazılım Mühendisleri |
| Kullanıcı Kılavuzu | Son kullanıcıya yönelik kullanım rehberi | Yazılım Mühendisleri |
| Toplantı Notları | Sprint ve ekip toplantı özetleri | Tüm ekip |

---

## 3. Dosya Adlandırma Kuralları

Tüm dokümanlar aşağıdaki formata uygun şekilde adlandırılmalıdır:

```
[DOKÜMAN_TÜRÜ]_[KONU]_v[SÜRÜM]_[TARIH].md
```

**Örnekler:**
- `GEREKSINIM_HavaDurumu_v1.0_2026-05.md`
- `TASARIM_Veritabani_v1.2_2026-05.md`
- `TEST_OneriSistemi_v1.0_2026-05.md`

**Kurallar:**
- Türkçe karakter kullanılmaz (ç→c, ş→s, ğ→g, ü→u, ö→o, ı→i)
- Boşluk yerine alt çizgi `_` kullanılır
- Küçük harf kullanılmaz; tüm harfler büyük olur (konu kısmı hariç)

---

## 4. Doküman Şablonu

Her doküman aşağıdaki başlık bloğuyla başlamalıdır:

```markdown
# [Doküman Başlığı]

**Proje:** Akıllı Tarım Destek Sistemi  
**Hazırlayan:** [Ad Soyad] ([öğrenci no]@firat.edu.tr)  
**Tarih:** [GG.AA.YYYY]  
**Sürüm:** [x.y]  
**Durum:** [Taslak / İncelemede / Onaylandı]  

---
```

Ardından içerik bölümleri gelir:

```markdown
## 1. Amaç
## 2. Kapsam
## 3. İçerik / Detaylar
## 4. Referanslar
```

---

## 5. Sürüm Kontrol Sistemi

### 5.1 Sürüm Numaralandırma

| Sürüm | Anlam | Örnek |
|---|---|---|
| v1.0 | İlk yayın | v1.0 |
| v1.1 | Küçük güncelleme / düzeltme | v1.1 |
| v2.0 | Büyük değişiklik / yeniden yazım | v2.0 |

### 5.2 Sürüm Geçmişi Tablosu

Her dokümanın sonunda aşağıdaki tablo bulunmalıdır:

```markdown
## Sürüm Geçmişi

| Sürüm | Tarih | Yazar | Değişiklik |
|---|---|---|---|
| 1.0 | 2026-05 | Mehmet Ali Kıraççakalı | İlk oluşturma |
| 1.1 | 2026-05 | [Ad] | [Değişiklik açıklaması] |
```

### 5.3 GitHub ile Sürüm Kontrolü

- Her doküman güncelleme commit mesajı şu formatta olmalıdır:
  ```
  docs: [doküman adı] v[sürüm] güncellendi
  ```
  **Örnek:** `docs: TASARIM_Veritabani v1.1 güncellendi`

- Tüm dokümanlar `/docs` klasörü altında tutulur:
  ```
  /docs
    /gereksinimler
    /tasarim
    /test
    /kullanici-kilavuzu
    /toplanti-notlari
  ```

---

## 6. Ekip Üyelerine Duyuru

Bu standart **tüm ekip üyeleri** için geçerlidir:

| Üye | E-posta |
|---|---|
| MEHMET ALİ KIRAÇÇAKALI | 250541069@firat.edu.tr |
| KAAN MERT KEKLİK | 250541053@firat.edu.tr |
| ARDA ÖZCAN ÇİFCİ | 250542012@firat.edu.tr |
| MELİK BUĞRA KARA | 250541110@firat.edu.tr |
| MERYEM ABDURRAHMAN | 250541605@firat.edu.tr |
| Ceylan Dağılma | — |

**Ekip üyeleri:**
- Yeni doküman oluştururken bu şablonu kullanır
- Dokümanı `/docs` klasörüne yükler
- Commit mesajında sürüm bilgisini belirtir

---

## 7. Uyum Takibi

- Sprint başında Scrum AI tarafından doküman durumu kontrol edilir
- Eksik veya uyumsuz dokümanlar ilgili kişiye bildirilir
- Tamamlanan dokümanlarda "Durum: Onaylandı" ibaresi kullanılır

---

## Sürüm Geçmişi

| Sürüm | Tarih | Yazar | Değişiklik |
|---|---|---|---|
| 1.0 | 2026-05 | Mehmet Ali Kıraççakalı | İlk oluşturma |
