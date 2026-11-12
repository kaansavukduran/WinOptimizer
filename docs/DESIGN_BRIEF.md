# WinOptimizer — DESIGN BRIEF

**Ürün:** Windows x64 bakım uygulaması; Python/Qt Widgets, paketli headless Node ve Windows PowerShell. Mevcut altyapı, ayrı Setup/Portable, ayarlar ve geçmiş korunur.

**Kullanıcı:** Teknik bilgisi sınırlı Windows kullanıcısı; ayrıca büyük yazı/klavye kullanan, disleksik, ileri yaşta veya dar dizüstü penceresinde çalışan kullanıcılar. “Herkes için kusursuz” iddiası yerine açık test kapsamı vardır.

**Ana görev:** Bilgisayarı tara → bulguyu anla → uygun değişikliği/yedeği incele → onayla → gerçek sonucu veya kurtarma yolunu gör.

**Hedef cihaz:** Windows masaüstü/dizüstü; resizable pencere ve farklı uygulama yazı/arayüz ölçekleri. 540 px dar pencere, yaklaşık 1240 px geniş pencere ve %200 arayüz + %125 yazı profilleri. Windows VM'deki gerçek boyut kayda alınır. Fiziksel tablet/dokunmatik, OSK/DPI ve düşük donanım ayrıca doğrulanmalıdır. Telefon OS/web sürümü yoktur; gamepad şartı uygulanmaz.

**Ton / üç sıfat:** Anlaşılır, sakin, güvenilir. Sıcak pembe/mavi Aion kimliği işlevsel bir yardımcıdır. Teknik ayrıntı gerektiğinde açılır; işlem kanıtı karakter animasyonu değil günlük ve sonuçtur.

**Kaçınılacak üç kalıp:** Ölçülmemiş sağlık/onarım yüzdesi; aynı ekranda yarışan ana düğmeler; bağlamdan kopuk gradient/ikon/kart/maskot kolajı.

**Marka:** Fragaria Interactive üst marka, AIONIA ürün kalite standardı/evren bağlamıdır. WinOptimizer kendi Windows aracıdır. Onaylı uygulama Aion'u ve çarklı ikon korunur; yeni karakter veya kanon kararı yoktur. Kaynak ve onay sınırları ART_BIBLE.md / AIONIA-REFERENCES.json içindedir.

**Bileşenler:** Mevcut dört tema, sistem/Verdana/OpenDyslexic, 4 px kenar ve ölçeklenen boşluk. Qt'nin düğme/checkbox/combobox semantiği korunur; görünen uzun metin sarılır, erişilebilir/asıl metin kesilmez. Sayfa/bölüm 1.35×/1.12× tipografiyle ayrılır. Destructive eylem metni + tehlike rengi; sonuç günlüğünde gerçek complete/failed metni + renk. Renk tek bilgi kanalı değildir.

**Örnek ana ekranlar:** Genel bakışta üç gerçek bakım görevi; Tara ve Düzelt'te bulgu → tek ana eylem; sürücü merkezinde seçili bölüm başlığı → ilgili eylem; Ayarlar'da görünüm/erişilebilirlik alanları ve otomatik kayıt. Ekran/eylem envanteri SCREEN_INVENTORY.md içindedir.

**Ölçüm:** Paketli Windows'ta 40 sayfa/profil örneğinde dış yatay kaydırma 0, ana eylem sayısı ≤1. Sadece eşzamanlı Qt render çağrısı için önceden belirlenen CI bütçesi 2000 ms; sonuçlar ölçülünce raporlanır. Bu ölçü tam açılış/gecikme/FPS, CPU/bellek/enerji veya insan görev başarısı değildir.
