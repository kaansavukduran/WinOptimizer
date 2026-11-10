# Terminal sürümünden grafik arayüze

WinOptimizer Aion, Windows işlemleri PowerShell 5.1 arka ucuna bağlı 6.x sürümünde gerçek Python/Qt Widgets masaüstü uygulamasıdır. Terminal menüsünün bire bir kaplaması değildir. Eski betikler `legacy/` içinde tarihçeleriyle korunur; kurulan uygulama bu betikleri çalıştırmaz. Aşağıdaki karşılaştırma `legacy/WinOptimizer.ps1` ve güncel `backend/` / `desktop/` koduna dayanır.

| Eski terminal sürümü | Grafik uygulamada durum |
| --- | --- |
| Geçici dosya ve çok tarayıcılı geniş temizlik | Yaş filtresi ve önizlemeyle kullanıcı Temp, Chrome/Edge Default önbelleği; geri alınabilir depo ve ayrı kalıcı silme. Firefox/Brave/Opera ve tüm profiller henüz kapsanmıyor. |
| cleanmgr ve DISM `/ResetBase` | Bu komutlar uygulanmıyor; geniş sistem temizliği ve geri dönüşü kısıtlayan ResetBase taşınmadı. |
| Genel registry temizliği | Yok. Yalnız geçerli kullanıcının HKCU Run başlangıç kaydı seçilerek kaldırılır ve geçmişten geri alınabilir. |
| Defender, firewall, UAC, BitLocker, port/virüs taraması | Defender/firewall/BitLocker durum göstergeleri var. Tam virüs taraması, port analizi ve UAC denetiminin tamamı yok. |
| Genel Windows güncellemelerini yükleme | Windows Update ayarlarını açma var. Uygulama içindeki otomatik kaynak sürücü teklifleri içindir; genel OS güncellemesi yüklenmiyor. |
| winget ile uygulamaları güncelleme | Henüz yok. |
| Registry, Task Scheduler ve Startup klasörü analizi | HKCU Run yönetimi var; zamanlanmış görevler ve Startup klasörünün tamamı yok. |
| Hizmetleri topluca devre dışı bırakma | Yok. Tara ve Düzelt yalnız önerilen durdurulmuş ses hizmetini onayla başlatır ve yeniden kontrol eder. |
| DNS, Winsock, TCP, QoS değişiklikleri | Ağ/DNS envanteri ve DNS önbelleği temizliği var. Toplu Winsock/TCP/QoS değişiklikleri yok. |
| Yeni güç planları ve CPU/PCIe değişiklikleri | Mevcut Windows güç planını seçme ve çakışma korumalı geri dönüş var. CPU minimumunu zorla %100 yapma yok. |
| Donanım, SMART, sıcaklık, işlem, SFC ve olay günlüğü raporu | OS/CPU/RAM/disk alanı ve Windows'un sunduğu disk sağlığı var. Sıcaklık, ayrıntılı SMART, SFC/olay günlüğü analizi henüz yok. |
| Log/rapor ve geri alma | Yerel işlem geçmişi, rapor/ayar dışa aktarma; temizliği geri alma, başlangıç/güç planı geri dönüşü, sürücü paket yedekleri. Her işlem geri alınabilir değildir. |

Grafik sürüm ayrıca sürücü envanteri ve Windows Update teklifleri, tarama sonucundan seçmeli veya **Tümünü güncelle**, otomatik üçüncü taraf sürücü yedeği, imzalı çevrimdışı INF paketleri, Microsoft Visual C++/DirectX kurucuları, geri yükleme noktaları, Aion etkileşimi, Türkçe/English ve bağımsız erişilebilirlik ayarları ekler. Bir sürücü yedeği tam sistem imajı değildir; IObit'in özel sürücü kataloğu uygulamada yoktur.

## İlk kullanım

1. **Tara ve Düzelt → Taramayı başlat.** Varsayılan tarama, sürücü tekliflerini aramak için internet kullanır. Ayarları değiştirmez ve kurulum başlatmaz. İnternetsiz kontrol için **Tarama seçenekleri → Çevrimiçi kontrolleri de yap** seçeneğini kapat.
2. **Sıradaki adım** bölümünü oku. Sürücü teklifleri varsa **Tümünü güncelle (sayı)** düğmesine bas. Filtreler bu toplamı daraltmaz. İstersen yalnız istediğin sürücüleri seçebilirsin.
3. Onay penceresinde sürücü listesini incele. Onaydan sonra sürücü yedeği alınır, Windows yönetici izni istenir ve kurulum sonucu sürücü başına gösterilir. Yedekleme de yönetici izni gerektirdiğinden Windows izni yedek alınmadan önce sorulur. Başarısız öğeler başarı sayılmaz; gerekiyorsa yeniden başlatma bilgisi gösterilir.

## English

This is a real Windows GUI with a PowerShell 5.1 backend, not full command-line feature parity. Broad cleanup/registry/service/network tweaks are excluded. General OS update installation, winget app updates, full startup-task management, temperature/advanced SMART and SFC/event-log analysis are not implemented. The current bounded cleanup, health, driver, runtime and recovery features have their own native paths; archived legacy scripts are not invoked.

For beginners: **Scan & Fix → Start scan → Next step → Update all (count) → review the driver list and confirm**. Online driver checks are on by default; disable them under **Scan options** for a local scan. Scanning performs no installation. Bulk updating includes every eligible offer from that scan, independently of visible filters, with the existing administrator, backup and per-item outcome flow.
