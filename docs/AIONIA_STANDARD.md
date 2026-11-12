# AIONIA v1.5 — WinOptimizer uygulaması

Normatif kaynak: [Evrensel Dijital Ürün, Tasarım ve Kalite Standartları](https://docs.google.com/document/d/16jj2cwbm8SiVWqDy3N3dzqxTlLoK7JR2_aH6hl4noWY/edit), v1.5, 12 Kasım 2026. Güncel Drive belgesi yeniden okunmuştur; önceki repo kaydı v1.2 idi. **11, 14, 19 ve 20. bölümler** bu Windows aracında teknoloji bağımsız UX, ilk açılış tercihi ve geometrik kaliteyi belirler. Kullanıcının “normal uygulama, oyun motoru değil” açıklaması uygulanır.

## Ürün ve kullanıcı

WinOptimizer bir Windows x64 bakım aracıdır. Temel kullanıcılar teknik bilgisi sınırlı kişiler; ayrıca klavye kullananlar, büyük yazıya ihtiyaç duyanlar, disleksik kullanıcılar ve dar pencerede çalışanlardır. Hedef, bakım önerisini anlayıp hangi değişikliğe onay verdiğini görebilmeleridir. Herkes için eksiksiz kullanılabilirlik veya doğrulanmış WCAG uyumluluğu iddiası yoktur.

Teknoloji: Python 3.12 / Qt Widgets, paketlenmiş headless Node ve sınırlandırılmış Windows PowerShell 5.1 işlemleri. Chromium, yeni framework veya oyun motoru eklenmez. Windows dışında yalnız kaynak önizleme/Qt birim testleri yapılabilir; Windows işlevi iddia edilmez.

## Bu turdaki eksikler ve karşılıkları

| Bulgu | Uygulama |
| --- | --- |
| Dar/büyük yazılı pencerede sağ sekmeler görünmüyor | Gerçek metin ölçüsüne göre bütün on bölümü içeren yerel Bölüm seçicisi; seçili bölüm ve görünür klavye odağı korunur. |
| Özel vurgu rengi odak çerçevesini görünmez yapabiliyor | Ayrı odak token'ı: arka plan ve yüzeye karşı en az 3:1; ana düğme metninde en az 4.5:1. |
| Odak yalnız düğmelerde belirgin | Form, liste, kaydırıcı ve Aion odağı için görünür işaret. |
| Açılışta boş pencere kullanıcıyı bekletiyor | İşlem motoruna bağlantı açıklaması ve belirsiz ilerleme; hata halinde yükleme durur, kurtarma ekranı kalır. |
| Kullanıcı mevcut bölümde ne yapacağını bulamıyor | Her sayfada yerel F1 rehberi; tara–incele–onayla, gerçek işlem durumları, bölüm açıklaması ve klavye kontrolleri. |

## Kalite sınırları

Görünüm tercihleri, geçmiş, bakım ilerlemesi ve onaylı Aion varlıkları korunur. Yeni rehber/gezinti sistem değişikliği yapmaz, ağ bağlantısı/telemetri eklemez; metinler paketlidir. Kamera, fizik, oynanabilir bölüm, Godot/web export bu masaüstü aracı için kapsam dışıdır. Ses/müzik eklenmez. Yeni evren karakteri veya onaysız marka logosu yüklenmez.

Testler PASS / FAIL / NOT TESTED olarak [QA kaydında](AIONIA-QA.md) raporlanır. Kaynak Qt testleri gerçek Windows paket/yardımcı teknoloji testi yerine geçmez. [Ürün tasarımı](APP_DESIGN.md), [görsel kurallar](ART_BIBLE.md), [referans manifesti](AIONIA-REFERENCES.json).

## v1.5 uygulaması / 6.10.0

Yeni kurulum ilk açılışta koyu tema ve sistem fontu kullanır. Kayıtlı açık/sistem/yüksek kontrast tema, font ve ölçekler normalize edilerek korunur; zorunlu sıfırlama yoktur. Kullanıcı Ayarlar'dan değiştirebilir. Bölüm 18–19'daki retro oyun yükleme ekranı, 15–17'deki oyun yönü/dokunmatik/kontrol şeması ve Xbox gereklilikleri bu oyun dışı Windows aracına zorlanmaz.

Geniş masaüstünde içerik 1120 × uygulama ölçeği mantıksal piksel ile sınırlanır ve ortalanır. Chrome tam pencere genişliğini kullanır; veri tabloları kendi yatay kaydırmasını korur. 4/8/16 tabanlı boşluklar, 4 px köşe ve 2 px düğme kenarı aynı ailede tutarlıdır. Focus/hover/pressed sırasında kenar rengi değişir; dış geometri değişmez. Birincil eylem ayrı renkle ve metinle belirtilir; görsel öncelik bütün düğmelerin aynı genişliğe zorlanması anlamına gelmez.

Bakım adımı başlığı ve durumu aynı kopya sütunundadır. Üç eşdeğer Aç/Tekrar aç düğmesinin genişliği gerçek font ölçüsünden ortak hesaplanır. Başlık alanı daraltılmaz; gerçek içerik genişliği yetmeyince aynı satır dikey dizilir. Yeniden boyutlandırma işlem başlatmaz, veri veya odak kaybetmez. Yardım ve hızlı görünüm düğmeleri metinleri kadar yer kaplar, yüksekliği satıra bölünen metni korur. Bunlar aynalı simetri yerine işlevsel ve ölçülen optik denge kararlarıdır.

Güncel analiz ve PASS/FAIL/NOT TESTED: [v1.5 QA](AIONIA-1.5-QA.md). Önceki v1.2 ve v1.1 kayıtları tarihsel kanıt olarak korunur; yeni Windows paket/güncelleme sonuçları olmadan tamamlanmış sayılmaz.

## v1.2 uygulaması / 6.9.0

[DESIGN_BRIEF](DESIGN_BRIEF.md), [ekran envanteri](SCREEN_INVENTORY.md) ve [v1.2 QA](AIONIA-1.2-QA.md) bu turun karar ve doğrulama kayıtlarıdır. Ana kategori adları/sırası ve görsel kimlik korunur. Yeni motor/framework/dependency yoktur. Uzun yerel etiketler, kontroller ve başlıklar Qt üzerinden satıra bölünür; yalnız tabloların içindeki iki boyutlu içerik yatay kayabilir. Her sayfada en fazla bir vurgulu ana eylem vardır; otomatik kaydedilen ayarlara sahte Kaydet düğmesi eklenmez. İlgili bölüm başlığı sayfa başlığının altında ikinci düzeydir.

v1.2 telefon/tablet/web kuralları var olmayan platform sürümü iddiasına dönüşmez: dağıtım Windows x64'tür. Dar pencere bir telefon testi değildir. Fiziksel Windows tablet/dokunmatik, OSK/sistem DPI, ekran okuyucu ve düşük donanım ölçülmedikçe NOT TESTED kalır. Oyun/Xbox zorunluluğu bu bakım uygulamasına uygulanmaz.
