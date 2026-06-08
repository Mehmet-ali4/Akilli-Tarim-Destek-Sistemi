## 6. Yapay Zeka Teknolojileri Araştırması

Bu raporda, Akıllı Tarım Destek Sistemi projesi kapsamında kullanılan ve gelecekte kullanılabilecek yapay zeka teknolojileri detaylı bir şekilde araştırılmıştır. Sistem, hava durumu, toprak analizi ve bitki sağlığı verilerini kullanarak çiftçilere en uygun sulama ve gübreleme yöntemleri hakkında öneriler sunmayı amaçlamaktadır.

### 2. Kural Tabanlı Uzman Sistemler
Mevcut projemizin (v1.0) çekirdeğini oluşturan teknolojidir. Geleneksel makine öğrenmesinin aksine, ziraat mühendisliği kurallarını if-else algoritmalarıyla koda dökerek kesin, bilimsel ve güvenilir tavsiyeler üretir.
* **Avantaj:** Eğitilmiş veriye ihtiyaç duymadan, %100 bilinen tarımsal ideal değerlere (pH, N-P-K ihtiyaçları, sıcaklık) göre çalışır. Hata payı yoktur.
* **Projedeki Yeri:** Bitkilerin ideal sıcaklık, nem, azot, fosfor ve potasyum seviyelerini kontrol edip anlık gübreleme/sulama tavsiyesi üretmekte aktif olarak kullanılmaktadır.

### 3. Derin Öğrenme (Deep Learning) - TensorFlow & Keras
Derin öğrenme, yapay sinir ağları kullanarak karmaşık verileri analiz edebilen gelişmiş bir makine öğrenmesi alt dalıdır.
* **Avantaj:** Doğrusal olmayan karmaşık ilişkileri çözebilir.
* **Dezavantaj:** Eğitilmesi için büyük veri setleri gerektirir.
* **Projedeki Yeri:** Şu anki sistemde basit bir Keras Sequential (Yapay Sinir Ağı) modeli prototip olarak kurulmuştur. Gelecekte gerçek veritabanı oluştuğunda eğitilecek ve kural-tabanlı sistemin yerini alacaktır.

### 4. Veri Analizi ve İşleme Teknolojileri (NumPy)
Sensörlerden gelen sayısal verilerin işlenmesi ve derin öğrenme modellerine girdi olarak hazırlanması için NumPy kullanılmaktadır.
* **Projedeki Yeri:** Python backend (Flask) üzerinde, frontend'den gelen JSON verilerini modelin anlayacağı NumPy matrislerine dönüştürmek için aktif olarak kullanılmaktadır.

### 5. Backend ve API Çatısı (Node.js & Flask)
Yapay zeka modellerinin kullanıcılarla etkileşime girmesini sağlayan HTTP altyapısıdır.
* **Projedeki Yeri:** Express.js proxy sunucusu görevini üstlenerek istekleri karşılamakta ve ağır makine öğrenmesi algoritmalarını çalıştıran Python/Flask API'sine yönlendirmektedir.

### 6. Web ve Arayüz Teknolojileri (Vanilla JS)
Geliştirilen sistemin kullanıcılar tarafından kolayca kullanılabilmesi için web arayüzü gereklidir.
* **Projedeki Yeri:** Modern CSS değişkenleri ve Vanilla JS kullanılarak "Glassmorphism" tasarım dilinde, React veya Flutter gibi ağır frameworklere ihtiyaç duymadan hafif, hızlı ve dinamik bir kullanıcı deneyimi sunulmaktadır.

### 7. Genel Değerlendirme ve Sonuç
Yapılan araştırmalar sonucunda, Akıllı Tarım Destek Sistemi için en uygun yaklaşımın hibrid bir yapı olduğu belirlenmiştir. Sistemin ilk versiyonunda güvenilir ziraat kurallarını işleten "Kural Tabanlı Uzman Sistem" ile esnekliği temsil eden "Yapay Sinir Ağları" birleştirilmiştir. Gelecekte IoT entegrasyonu ve veritabanı kurulumu ile model eğitimine ağırlık verilecektir.
