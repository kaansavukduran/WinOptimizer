# İsteklerin kapsam kaydı

Bu kayıt, yapılan işi başka bir uygulamanın bütün özellikleriyle eşit göstermemek için tutulur. Son yayımlanmış 6.9.0 kanıtları `VALIDATION.md` içindedir. 6.7.0, gerçek Windows Setup/Portable, hareket açık animasyon ve 6.6.0 → 6.7.0 uygulama içi güncelleme kontrollerinden geçerek kararlı yayımlandı.

| Önceki istek | Durum / uygulamadaki yeri |
| --- | --- |
| AIONIA v1.2 bütünsel UX/tema/yerleşim | 6.9: Sarılan kontroller, bölüm hiyerarşisi, tek ana eylem, yeniden dizilen formlar ve okunur presetler. 237 Qt/58 Node, gerçek Windows paketleri/40 profil ve 6.8→6.9 güncelleme PASS. Fiziksel cihaz/yardımcı teknoloji/tam denetim sınırları AIONIA-1.2-QA.md içinde. |
| AIONIA v1.1 teknoloji bağımsız kalite standardı | 6.8: Dar ekran/klavye/rehber/kontrast/açılış; mevcut Qt ve onaylı Aion korunur. Gerçek Windows ve güncelleme PASS; yardımcı teknoloji, fiziksel cihaz, perf ve tam denetim sınırları AIONIA-QA.md içinde. |
| Yalnız Windows, Chromium olmadan bağımsız uygulama | Tamam: Python/Qt Widgets, paketli Node, Windows PowerShell. Başka OS paketi veya donor alt uygulama yok. |
| Setup ve portable, ayrı sürümler, uygulama içi güncelleme | Tamam: sürümlü iki EXE; imzalı güncelleme metadatası ve dosya özeti, gerçek iki paketle güncelleme kontrolü. Portable Data klasörünü korur. |
| Tarama ve düzeltme, her adımın çalıştığını görebilme | Tamamlanan kapsam: Windows aygıt kodları, servis/ağ/ekran/bileşen göstergeleri ve dokuz ortak bakım kategorisi. Gerçek adım günlüğü, belirsiz/bilinen toplamlı ilerleme, iptal ve açık hata yolu. Her Windows arızasını saptama iddiası yok. |
| Tek tek seçmeden Tümünü güncelle | Tamam: taramanın bütün uygun Windows Update sürücü teklifleri, liste/sayıyla tek onay, önce yedek, sürücü başına sonuç. Firmware dışarıda. |
| Driver Booster benzeri sürücü merkezi | 6.7: Güncellemeler / Yüklü sürücüler / Yedekler ve geri yükleme / Çevrimdışı hazırlık / Atlananlar aynı uygulamada. Envanter arama/filtre, tarihli yedekler ve toplu atla/geri göster. |
| Sürücü yedeği ve geri yükleme | Tamamlanan kapsam: üçüncü taraf paket yedeği, hash ve imzayla inceleme, uygun INF seçimi, yeni yedek ve onayla Windows'a uygulama. Windows daha uygun sürücüyü koruyabilir; gerçek sürüm değişimi ayrı gösterilir. Tam disk imajı veya zorla rollback değildir. |
| Otomatik sürücü kaynağı / veritabanı | Kısmi: Windows Update Agent uygun teklifleri otomatik bulur. Yerel imzalı paketler desteklenir. IObit'in özel kataloğu ve tüm OEM'leri kapsayan lisanslı otomatik veri kaynağı yok. OEM siteleri ve Microsoft Catalog kullanıcı kontrollü dış bağlantılardır. |
| Driver Booster for Steam ile bütün özelliklerde eşitlik | Tamamlandı denemez. Özel katalog, bütün OEM/Game Ready paketleri, PhysX/OpenAL/eski VC nesilleri, kapalı uygulamada zamanlanmış/sessiz kurulum ve kesilenden devam eden sürücü indirme yok. Ayrıntılı sınırlar `DRIVER-COVERAGE.md` içinde. Bunları varmış gibi gösteren sayaç/düğme eklenmez. |
| Oyun bileşenleri ve bakım araçları | Tamamlanan kapsam: resmi Microsoft Visual C++ v14 x86/x64 ve DirectX June 2010; imza/hash/lisans onayı, geri yükleme noktaları, sınırlı bağlı olmayan aygıtlar ve geçici oyun odağı. 6.7'de atölye ilgili kategorilere ayrılır. |
| Donanım sekmesi ve VRAM/RAM/anakart vb. | Tamam: 14 yerel kategori, 64 bit DXGI VRAM, modüller, anakart/BIOS/disk/ekran/ağ vb.; arama, özet, rapor ve gerçek kategori ilerlemesi. Windows'un vermediği sensör/fan/PSU bilgisi tahmin edilmez. |
| SysMender donor malzemesini uygun yerlere entegre et | Tamam: dokuz yerel bakım kategorisi ortak tarama, genel bakış, araçlar ve geçmişte. Ayrı SysMender C#/EXE veya alt uygulama yok; MIT bildirimleri korunur. |
| Aion pembe/mavi kimliği ve karşıdan bakan çarklı logo | Tamam: sevimli önden yüzlü ikon, pembe/mavi/beyaz çark; iki EXE'nin yedi ikon boyutu doğrulanır. |
| Kare kare animasyon, fare takibi ve sevilme | Tamam: on sayfa klibi, yeni 24 kare, 16 çizilmiş bakış yönü, fare/klavye sevilme, gerçek sonuç tepkisi, pause, hareket azaltma ve kapatılabilirlik. |
| Kullanımı kolay tema/font/renk/yüzde ayarları | Tamam: her sayfada Yazı ve tema, OpenDyslexic Türkçe glifleri/önizleme, dört tema, hazır/özel renk, bağımsız arayüz ve yazı ölçeği, klavye ve dar/büyük yazı kontrolleri. |
| Bakım yolculuğundaki üç iş ve sıradaki adım anlaşılır olsun | Tamam: üç gerçek görev, açıklama/durum, doğru eylemi gösterme ve geri dönüş. Gezinme veya aynı başarıyı tekrarlama puan vermez. |
| Eski terminal sürümünün bütün özellikleri | Bire bir eşitlik yok. Geniş registry/service/QoS değişiklikleri ve geri dönüşü kısıtlayan ResetBase aktarılmadı. Winget güncelleme, kapsamlı Task Scheduler yönetimi ve SFC onarımı yok. `LEGACY-COVERAGE.md` bu farkları listeler. |
| GitHub sürümü ve özel Drive yedeği | Her döngüde: kaynak/dal/commit, bütün erişilebilir Git geçmişi/etiketler, iki paket, notlar/kanıtlar; özel anahtarlar hariç, ham geri okuma ve arşiv doğrulaması. |

Kapanış ölçütü bir özelliğin görünen düğmesi değil, gerçek giriş noktasından çalışan davranış ve doğrulamadır. Lisanslı katalog gibi dış kaynak gerektiren satırlar kaynak olmadan tamamlandı olarak işaretlenmez. Genel/sessiz sistem değişiklikleri, yalnız bir rakipte adı geçiyor diye otomatik uygulanmaz.
