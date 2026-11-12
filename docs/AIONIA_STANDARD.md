# AIONIA v1.1 — WinOptimizer uygulaması

Normatif kaynak: [Evrensel Dijital Ürün, Tasarım ve Kalite Standartları](https://docs.google.com/document/d/16jj2cwbm8SiVWqDy3N3dzqxTlLoK7JR2_aH6hl4noWY/edit), v1.1, 12 Kasım 2026. Drive belgesi bu tarihte okunmuştur. **11. bölüm**, önceki Godot/oyun/pixel art zorunluluklarını teknoloji bağımsız ürün kapsamıyla değiştirir. Kullanıcının WinOptimizer için yaptığı “normal uygulama, oyun motoru değil” açıklaması uygulanır.

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
