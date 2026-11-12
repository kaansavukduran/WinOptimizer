# Ekran ve kategori envanteri — 6.9.0

Mevcut on ana kategori ve Ctrl+1…9/Ctrl+0 sırası korunur. Önce kullanıcı görevi; alt bölüm başlığı, eylem ve sonuç aynı bağlamı anlatır. Dar pencerede aynı bölümler yerel seçicide görünür. Gereksiz yeni menü katmanı, sekme veya kart koleksiyonu eklenmez.

| Ekran | Görev / ana eylem | Alt bölümler / durum |
| --- | --- | --- |
| Genel bakış | İlk eksik bakım görevine git; tamamlandıysa Tara ve Düzelt | Üç gerçek görev, neyi saydığı, sıradaki adım; sürücü yedeği doğru Yedekler bölümüne gider. |
| Tara ve Düzelt | Tarama; uygun teklif varsa Tümünü güncelle | Sorun/güncelleme/isteğe bağlı/bilinmeyen/bilgi filtresi; açık tarama seçenekleri korunur. |
| Güvenli temizlik | Önce adayları tara | Planı incele/onayla; geri alma Geçmiş ve yedekler'de. |
| Sürücü merkezi | Seçili işin kontrol/yedek/inceleme eylemi | Güncellemeler, Yüklü sürücüler, Yedekler ve geri yükleme, Çevrimdışı hazırlık, Atlananlar; her birinin başlığı/açıklaması vardır. |
| Donanım | Donanımı tara | 14 kategori, arama, ayrıntı ve rapor; bilinmeyen değer tahmin edilmez. |
| Başlangıç | Öğeleri listele | Henüz taranmadı / boş / seçim yok / tek seçim / fazla seçim açıklanır. Bir seferde bir öğe; onay olmadan değişmez. |
| Bakım atölyesi | Seçili kategoriyi oku/incele | Oyun bileşenleri, geri yükleme noktaları, geçici oyun odağı, aygıtlar; bölüm başlıkları eşleşir. |
| Sistem araçları | Yerel kontrolü yenile | Ağ/Windows araçları ikincil eylemdir; yönetici/onay/kurtarma sınırları korunur. |
| Geçmiş ve yedekler | Kaydı yenile / ilgili kaydı incele | Boş geçmiş açık; geri al ve kalıcı sil farklı metin/onay/tehlike görünümü. |
| Ayarlar | Alanı değiştir, otomatik kaydı gör | Genel, Görünüm, Erişilebilirlik, Aion ve Bildirimler, Veri, Güncellemeler, Hakkında; ayrı bölüm başlığı. |

Başlık sırası: sayfa → bölüm → özellik/değer. Uzun aygıt adları ve Türkçe etiketler sarılır. Tablo sütunlarının kendi yatay kaydırması, bütün sayfanın yatay kaymasıyla karıştırılmaz. Formlar pencere değişince yeniden dizilir, girilen metin kaybolmaz. Yeni durumlar, eski yükleniyor/hata/iptal/onay/geri alma ve çevrimdışı davranışlarının yerine geçmez.

Geçmiş kullanıcı şikâyetleri: erken resize attribute hatası, silinen Qt nesnesine geç callback, belirsiz Windows beklemesi, belirsiz bakım 2/3 sayacı, bulunamayan font/tema, bilinmeyen sürücü kodu, motor kopmasında sonsuz bekleme ve büyük yazıda kaybolan içerik. İlgili eski testler korunur; yeni ekran/profil ve alt bölüm testleri eklenir. Fonksiyonel ve görsel Windows QA kaydı AIONIA-1.2-QA.md içindedir.
