# AIONIA v1.2 QA — 6.9.0

Resmî belge 12.11.2026 tarihinde erişilerek okundu. PASS yalnız adı verilen ortam/kapsam için geçerlidir. Bu kaynak turu henüz Windows paket/güncelleme kapısını tamamlamış sayılmaz.

| Kontrol | Durum | Kanıt / sınır |
| --- | --- | --- |
| Ürün, teknoloji, 10 ekran, geçmiş hata ve görsel kaynak denetimi | PASS | DESIGN_BRIEF, SCREEN_INVENTORY, ART_BIBLE; mevcut Aion/ikon korunur. |
| Kaynak Qt/Node regresyonları | PASS | Yerel 237 Qt / 58 Node; önceki kritik regresyonlar korunur. Windows paket sonucu ayrı beklenir. |
| Ana ekran ve 16 alt bölüm, TR/EN, dar/geniş/büyük yazı | PASS | Asıl hedef dış yatay kaydırma 0 ve tek ana eylem; yalnız birim testi fiziksel cihaz değildir. |
| Başlangıçta boş/seçim durumları, açıklamalı disabled, klavye | PASS | Gerçek Qt denetim testi. |
| Hata/kurtarma, yükleme, veri/tercih koruma, onay/geri alma | PASS | Mevcut ve yeni regresyonlar; paket doğrulaması bekleniyor. |
| Gerçek Windows Setup/Portable/yeniden açılış ve 40 profil/sayfa | NOT TESTED | Her ana ekranı içeren paket QA ve gerçek geometri/screenshot kaydı bekleniyor. |
| 6.8.0 → 6.9.0 uygulama içi güncelleme | NOT TESTED | Hash/registry/runtime/tercihler/geçmiş doğrulanacak. |
| Eşzamanlı Qt render çağrısı CI ölçümü | NOT TESTED | Önceden tanımlı 2000 ms bütçe; uçtan uca kullanıcı gecikmesi değildir. |
| NVDA/Narrator / tam erişilebilirlik denetimi | NOT TESTED | Qt adları ve kontrast otomatik testi tam uyumluluk kanıtı değildir. |
| Fiziksel Windows tablet/dokunmatik, OSK, sistem DPI, düşük donanım | NOT TESTED | Pencere profili gerçek fiziksel cihazı temsil etmez. |
| Gerçek kullanıcı görev oranı/süresi; CPU/RAM/enerji/açılış benchmark | NOT TESTED | Ölçülmeyen başarı yüzdesi/FPS verilmez. |
| Kapsamlı pentest / tam WCAG denetimi | NOT TESTED | Mevcut imza/hash/izin sınırları ve bağımlılık denetimi bu kapsam değildir. |

Telefon OS/web/Gamepad/Xbox: bu Windows bakım uygulamasının dağıtım hedefleri değildir; oyun maddeleri uygulanmaz. Durumları sahte PASS yapılmaz. Yeni motor/framework veya varsayımsal platform sürümü oluşturulmaz. Kritik hedef akış FAIL kalırsa kararlı teslim yapılmaz. İlk kaynak denetiminde taşma bulundu; düzeltme sonrası sonuçlar ayrıca kaydedilir.
