# Akıllı Tarım Destek Sistemi - Bulut Altyapısı Tasarım Belgesi

Bu belge, "Akıllı Tarım Destek Sistemi" projesinin yüksek erişilebilirlik, güvenlik ve performans standartlarında çalışabilmesi için gerekli bulut altyapısı tasarımını, kaynak yapılandırmalarını ve maliyet optimizasyon stratejilerini içermektedir.

## 1. Bulut Hizmet Sağlayıcısı Seçimi

Projenin bulut altyapısı için temel sağlayıcı olarak **Amazon Web Services (AWS)**, kullanıcı arayüzü (frontend) dağıtımları için ise **Vercel** tercih edilmiştir. 

**Neden AWS ve Vercel?**
* **IoT ve Sensör Entegrasyonu:** AWS, tarım alanlarındaki sensörlerden (nem, sıcaklık vb.) gelen yoğun veriyi işlemek için güçlü IoT ve veri akışı (streaming) servisleri sunar.
* **Esneklik ve Ölçeklenebilirlik:** İhtiyaca göre otomatik olarak büyüyüp küçülebilen bir altyapı sağlar.
* **Modern Dağıtım:** Vercel, modern web uygulamaları için sıfır yapılandırma ile küresel ölçekte hızlı bir içerik dağıtım ağı (CDN) ve sunucusuz (serverless) işlevler sunarak frontend performansını maksimize eder.

---

## 2. Sistem Bileşenleri ve Kaynak Yapılandırması

### 2.1. İşlem Gücü (Compute)
* **Backend Servisleri (API):** Uygulamanın ana iş mantığını yürütecek backend API'leri için **AWS Elastic Container Service (ECS)** veya **AWS Elastic Beanstalk** kullanılacaktır. Konteyner mimarisi (Docker), uygulamanın farklı ortamlarda tutarlı çalışmasını sağlar.
* **Asenkron İşlemler ve Veri İşleme:** Sensörlerden gelen anlık verilerin tetiklediği kısa süreli işlemler (örneğin; "nem düştü, sulama sistemine sinyal gönder") için sunucusuz mimari olan **AWS Lambda** kullanılacaktır.
* **Frontend Barındırma:** Kullanıcı arayüzü, otomatik CI/CD süreçleriyle doğrudan GitHub üzerinden **Vercel**'e dağıtılacaktır.

### 2.2. Veri Depolama (Database & Storage)
* **İlişkisel Veriler:** Kullanıcı hesapları, yetkilendirmeler, tarla bilgileri ve sistem ayarları gibi yapılandırılmış veriler için **Amazon RDS (PostgreSQL)** kullanılacaktır. Multi-AZ (Çoklu Kullanılabilirlik Alanı) yapılandırması ile veri kaybı riski en aza indirilecektir.
* **Zaman Serisi ve Sensör Verileri:** Cihazlardan sürekli olarak akacak olan nem, sıcaklık ve toprak analizi gibi zaman serisi verileri için yüksek yazma kapasitesine sahip **Amazon DynamoDB** veya **Amazon Timestream** konumlandırılacaktır.
* **Nesne Depolama:** Kullanıcıların yüklediği tarla görselleri, rapor çıktıları ve sistem yedekleri **Amazon S3 (Simple Storage Service)** üzerinde güvenle saklanacaktır.

### 2.3. Ağ Yapılandırması (Networking)
* **VPC (Virtual Private Cloud):** Tüm AWS kaynakları izole bir ağ (VPC) içinde çalışacaktır.
* **Alt Ağlar (Subnets):**
    * *Public Subnet:* Sadece Load Balancer (Yük Dengeleyici) ve NAT Gateway gibi dışarıya açık olması zorunlu bileşenleri barındırır.
    * *Private Subnet:* Veritabanları (RDS), Backend sunucuları ve diğer kritik kaynaklar dış internete kapalı olan bu ağda yer alır.
* **API Gateway:** İstemcilerden (mobil uygulama veya web) gelen tüm istekler tek bir merkezden (**Amazon API Gateway**) yönetilecek ve yönlendirilecektir.

### 2.4. Güvenlik (Security)
* **Güvenlik Duvarı:** API Gateway ve Load Balancer önüne **AWS WAF (Web Application Firewall)** kurularak SQL Injection, XSS ve DDoS gibi kötü amaçlı saldırılar engellenecektir.
* **Kimlik ve Erişim Yönetimi:** **AWS IAM** kullanılarak servislere ve geliştiricilere "en az ayrıcalık (least privilege)" prensibine göre yetki verilecektir.
* **Veri Şifreleme:** Depolanan veriler (S3 ve RDS) AWS KMS kullanılarak şifrelenecek, veri aktarımı ise TLS/SSL sertifikaları üzerinden yapılacaktır.

---

## 3. İzleme, Ölçeklendirme ve Maliyet Optimizasyonu

### 3.1. Kaynak Kullanımını İzleme
* **AWS CloudWatch:** CPU kullanımı, bellek tüketimi, ağ trafiği ve veritabanı okuma/yazma kapasiteleri gibi tüm metrikler CloudWatch üzerinden anlık izlenecektir. 
* **Alarmlar:** Hata oranlarının artması veya kaynakların %80 kullanım sınırını aşması durumunda sistem yöneticilerine otomatik bildirimler gönderilecektir.

### 3.2. Ölçeklendirme Stratejileri
* **Auto Scaling (Otomatik Ölçeklendirme):** ECS ve EC2 örnekleri, CloudWatch'tan gelen CPU ve ağ metriklerine göre yapılandırılmış **Auto Scaling Group** kurallarına göre çalışacaktır. Trafiğin yoğun olduğu saatlerde (örneğin sabah sistem kontrolleri sırasında) yeni sunucular otomatik ayağa kalkacak, trafik azaldığında ise kapanacaktır.
* **Veritabanı Ölçeklendirmesi:** Okuma yükünü hafifletmek için RDS için "Read Replica" (Okuma Kopyaları) eklenecektir.

### 3.3. Maliyet Optimizasyonu
* **Sunucusuz (Serverless) Yaklaşımı:** Sürekli açık kalması gerekmeyen, sadece sensör verisi geldiğinde çalışan fonksiyonlar için AWS Lambda kullanılarak yalnızca işlem süresi kadar ödeme yapılacaktır.
* **S3 Yaşam Döngüsü Politikaları (Lifecycle Policies):** 30 günden eski ve sık erişilmeyen sensör logları veya eski sistem yedekleri, daha uygun maliyetli depolama sınıfı olan **S3 Glacier**'a otomatik olarak taşınacaktır.
* **Spot Instance Kullanımı:** Kritik olmayan, arka planda çalışan uzun süreli veri analizi görevleri için standart sunuculara göre çok daha ucuz olan **Amazon EC2 Spot Instances** kullanılacaktır.