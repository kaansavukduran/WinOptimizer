# AIONIA v1.1 doğrulaması — 6.8.0

Durum 12 Kasım 2026. PASS yalnız belirtilen ortam/kapsam için geçerlidir. 6.8.0 kararlı yayımlandı; kaynak/PR/main/yayın/hareket/güncelleme altı kontrol de başarılı.

| Kontrol | Sonuç | Kanıt / sınır |
| --- | --- | --- |
| Drive standardı v1.1 ve 00_BAŞLA | PASS | Bağlantıdan içerik okundu; bölüm 11 kapsamı uygulandı. |
| 19 görsel, pafta/sprite/logo referansı | PASS | Ham dosyalar indirildi ve görsel incelendi; hash/boyut manifestte. Bu onay kararı değildir. |
| Teknoloji ve ürün kapsamı | PASS | Windows Python/Qt korunur; yeni bağımlılık/framework yok. |
| Dar pencere / %200 UI + %125 yazı, TR/EN | PASS | Gerçek yerel Qt denetimleri, 540 px; bütün on bölüm erişilebilir. Fiziksel ekran testi değildir. |
| F1 rehber / Esc / Ctrl kısayolları / odak | PASS | Gerçek Qt olayları, on sayfa TR/EN rehberi; rehber sistem işlemi başlatmadı. |
| Açılış yükleme ve motor hatası | PASS | Gecikmeli bootstrap ve başarısız motor; yükleme kapanıp kurtarma kaldı. |
| Kontrast token'ları | PASS | Açık/koyu/kontrast × 4 özel renk; metin 4.5:1 ve odak/sınır 3:1 renk çiftleri. |
| Node üretim bağımlılıkları denetimi | PASS | npm audit --omit=dev: sıfır bilinen açık; Python/Qt veya tüm ürün pentesti değildir. |
| Kaynak regresyonları | PASS | Yerel ve Windows 133 Qt / 58 Node; mevcut bakım/onay/imza/hash/iptal/geri alma kuralları geçti. |
| Gerçek Windows Setup/Portable/yeniden açılış | PASS | Paketlenmiş Qt, F1/Ctrl gezinme, on bölüm, ayarlar/ilerleme, veri izolasyonu ve kilitli EXE değişimi. |
| Gerçek 6.7.0 → 6.8.0 güncelleme | PASS | Uygulamanın kendi güncellemesi; kesin payload hash, registry/çalışan sürüm, tercihler, geçmiş ve milestones. |
| On sayfada gerçek paket animasyonu | PASS | Windows hareketi açık özel test; bütün saatler ilerledi, runner ayarı finally içinde geri alındı. |
| Windows CPU/RAM/pil/başlangıç benchmark | NOT TESTED | İşlevsel açılış testi performans ölçümü yerine geçmez. |
| Windows ekran okuyucu (NVDA/Narrator) | NOT TESTED | Qt erişilebilir adları tam yardımcı teknoloji testi yerine geçmez. |
| Fiziksel dokunmatik / çok yüksek DPI / düşük donanım | NOT TESTED | Fare/klavye testinden bu cihazlara sonuç çıkarılmaz. |
| Gerçek kullanıcı görev başarısı | NOT TESTED | Kullanıcı araştırması yapılmadı. |
| Kapsamlı güvenlik/pentest ve tüm ürün WCAG denetimi | NOT TESTED | Var olan imza/onay testleri bu kapsamı karşılamaz. |

Oyun kamerası/çarpışma/Godot/web export, bu Windows aracının kapsamı dışındadır. Testler bu kapsam için PASS olarak yazılmaz.

Son çalıştırılan kontrollerde açık FAIL yok. İlk Windows turunda testin 2000 px masaüstü varsayımı FAIL verdi; gerçek çalışma alanı ve yerleşimi tamamlanmış odakla düzeltilip aynı koşullar son kaynakta yeniden geçti. Büyük yazı geliştirmesinde günlük panelinin içeriği sıkıştırması da bulunup kendi kaydırılabilir alanıyla düzeltildi.

[Kaynak](https://github.com/kaansavukduran/WinOptimizer/actions/runs/43227313949) · [PR](https://github.com/kaansavukduran/WinOptimizer/actions/runs/43227324236) · [main](https://github.com/kaansavukduran/WinOptimizer/actions/runs/43228876061) · [yayın](https://github.com/kaansavukduran/WinOptimizer/actions/runs/43228931961) · [hareket](https://github.com/kaansavukduran/WinOptimizer/actions/runs/43228681381) · [güncelleme](https://github.com/kaansavukduran/WinOptimizer/actions/runs/43229351327).

Gerçek Windows VM görüntüleri: [sürücü merkezi](screenshots/WinOptimizer-6.8.0-Surucu-Merkezi.png), [büyük yazı/dar pencere](screenshots/WinOptimizer-6.8.0-Buyuk-Yazi.png), [kaydırılabilir rehber](screenshots/WinOptimizer-6.8.0-Kullanim-Rehberi.png). Son iki görüntü büyütülmüş font stres kontrolüdür; varsayılan görünüm veya fiziksel cihaz testi değildir. [Kararlı sürüm](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v6.8.0) · [Özel yedek](https://drive.google.com/drive/folders/10nIOqRara8hCja2YPjZpCNMVqW1MmmWG). Ayrıntılı arşiv/hash kanıtı `VALIDATION.md` içindedir.
