# AIONIA v1.1 doğrulaması — 6.8.0

Durum 12 Kasım 2026. PASS yalnız belirtilen ortam/kapsam için geçerlidir. Paket/Windows sonuçları tamamlanmadan kararlı yayın iddiası yapılmaz.

| Kontrol | Sonuç | Kanıt / sınır |
| --- | --- | --- |
| Drive standardı v1.1 ve 00_BAŞLA | PASS | Bağlantıdan içerik okundu; bölüm 11 kapsamı uygulandı. |
| 19 görsel, pafta/sprite/logo referansı | PASS | Ham dosyalar indirildi ve görsel incelendi; hash/boyut manifestte. Bu onay kararı değildir. |
| Teknoloji ve ürün kapsamı | PASS | Windows Python/Qt korunur; yeni bağımlılık/framework yok. |
| Dar pencere / %200 UI + %125 yazı, TR/EN | PASS | Gerçek yerel Qt denetimleri, 540 px; bütün on bölüm erişilebilir. Fiziksel ekran testi değildir. |
| F1 rehber / Esc / Ctrl kısayolları / odak | PASS | Gerçek Qt olayları, on sayfa TR/EN rehberi; rehber sistem işlemi başlatmadı. |
| Açılış yükleme ve motor hatası | PASS | Gecikmeli bootstrap ve başarısız motor; yükleme kapanıp kurtarma kaldı. |
| Kontrast token'ları | PASS | Açık/koyu/kontrast × 4 özel renk; metin 4.5:1 ve odak/sınır 3:1 renk çiftleri. |
| Kaynak regresyonları | PASS | Yerel 133 Qt / 58 Node; Windows paket doğrulaması ayrıca bekleniyor. |
| Gerçek Windows Setup/Portable/yeniden açılış | NOT TESTED | Yeni paket henüz doğrulanmadı. |
| Gerçek 6.7.0 → 6.8.0 güncelleme | NOT TESTED | İmza/hash, tercihler/geçmiş ve çalışan sürüm doğrulanacak. |
| Windows ekran okuyucu (NVDA/Narrator) | NOT TESTED | Qt erişilebilir adları tam yardımcı teknoloji testi yerine geçmez. |
| Fiziksel dokunmatik / çok yüksek DPI / düşük donanım | NOT TESTED | Fare/klavye testinden bu cihazlara sonuç çıkarılmaz. |
| Gerçek kullanıcı görev başarısı | NOT TESTED | Kullanıcı araştırması yapılmadı. |
| Kapsamlı güvenlik/pentest ve tüm ürün WCAG denetimi | NOT TESTED | Var olan imza/onay testleri bu kapsamı karşılamaz. |

Oyun kamerası/çarpışma/Godot/web export, bu Windows aracının kapsamı dışındadır. Testler bu kapsam için PASS olarak yazılmaz.
