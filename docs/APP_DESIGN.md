# WinOptimizer ürün tasarımı

Vaat: Kullanıcı Windows bakım ihtiyacını anlayabilsin, önerilen değişikliği inceleyip onaylasın ve gerçek sonucu görebilsin.

Ana akış: Tara ve Düzelt → bulguyu oku → uygun işlemi seç → kapsam/adet ve yedek bilgisini gör → onayla → gerçek adımları izle → sonuç veya kurtarma yolunu kullan. Tarama, salt okuma durumları ve sistem değişiklikleri ayrıdır. Çevrimiçi sorgu Windows Update'e gider; yerel/çevrimdışı akış sürer. Erişilemeyen veri hata/sağlıklı ayrımında dürüst kalır.

Bilgi mimarisi mevcut on bölümdür. Genel bakış üç bakım görevini açıklar; sonuç/ayrıntı sayfaları bağlama göre rehber sunar. İlk açılışta otomatik sistem değişikliği, zorunlu hesap veya yeni telemetri yoktur. Rehber F1 ile çevrimdışı açılır. Klavye Tab/Shift+Tab, odaklı düğme Enter/Boşluk, Ctrl+1…9/Ctrl+0; rehber Esc ile kapanır. Kısayollar bir kurulumu otomatik onaylamaz. Dar ekranda ve büyütülmüş metinde tek bölüm seçicisi kaybolan sekmelerin yerini alır. Büyük yazıda başlık sadeleşir; sürüm Ayarlar → Hakkında üzerinden de okunur. İşlem günlüğü kendi kaydırılabilir alanındadır, ana içeriğin bütün yüksekliğini alamaz.

Güvenlik/mahremiyet: Mevcut onay, yedek, izin, imza/hash, firmware dışlama ve read-retry izin listesi korunur. Rehber ve gezinme yeni Windows yetkisi, veri dışa aktarımı veya ağ isteği eklemez. Yardım metni rapor/kimlik/cihaz yolu içermez. Kurulumun, motor kopmasının ve iptal edilen işlemin durumları ayrıdır; belirsiz sonuç otomatik başarı sayılmaz.

Sürdürülebilirlik: Yeni `native/usability.py` yalnız gezinme/rehberden sorumlu, mevcut Qt ve yerelleştirme yapısını kullanır. Yeni bağımlılık, oyun motoru veya genel framework eklenmez. Uyarlanabilir gezinme yeniden boyutlanmada mevcut denetimleri kullanır; kullanıcı tercihlerini değiştirmez. Mevcut animasyon önbelleği ve gizli zamanlayıcı kontrolü korunur.

Ölçüm sınırları: İlk kez kullanan gerçek kişilerle görev başarısı, fiziksel dokunmatik cihaz, NVDA/Narrator, yüksek-DPI fiziksel ekran ve düşük donanımda performans ölçülmeden onaylanmış sayılmaz. PASS/FAIL/NOT TESTED kaydı `AIONIA-QA.md` içindedir.
