# AIONIA v1.2 QA — 6.9.0

Resmî belge 12.11.2026 tarihinde erişilerek okundu. PASS yalnız adı verilen ortam/kapsam için geçerlidir. Son kaynak, PR, main, yayın, hareket ve kurulu güncelleme kapıları geçti; aşağıdaki sınırlar geçerliliğini korur.

| Kontrol | Durum | Kanıt / sınır |
| --- | --- | --- |
| Ürün, teknoloji, 10 ekran, geçmiş hata ve görsel kaynak denetimi | PASS | DESIGN_BRIEF, SCREEN_INVENTORY, ART_BIBLE; mevcut Aion/ikon korunur. |
| Kaynak Qt/Node regresyonları | PASS | Yerel 237 Qt / 58 Node; önceki kritik regresyonlar korunur. Windows kaynak/PR/main çalıştırıcısında da geçti. |
| Ana ekran ve 16 alt bölüm, TR/EN, dar/geniş/büyük yazı | PASS | Asıl hedef dış yatay kaydırma 0 ve tek ana eylem; yalnız birim testi fiziksel cihaz değildir. |
| Başlangıçta boş/seçim durumları, açıklamalı disabled, klavye | PASS | Gerçek Qt denetim testi. |
| Hata/kurtarma, yükleme, veri/tercih koruma, onay/geri alma | PASS | Mevcut ve yeni regresyonlar; Gerçek paket ve güncelleme kanıtlarıyla da doğrulandı. |
| Gerçek Windows Setup/Portable/yeniden açılış ve 40 profil/sayfa | PASS | Dört profil × on sayfa; dış yatay taşma 0, sayfa başına en fazla bir ana eylem; gerçek PNG/geometri/JSON kanıtı. |
| 6.8.0 → 6.9.0 uygulama içi güncelleme | PASS | Gerçek baseline UI: bölüm seç → Ayarlar → Güncellemeler → indir/yeniden başlat → onay; exact payload SHA, registry/runtime 6.9.0, önceki tercihler ve geçmiş korundu. |
| Eşzamanlı Qt render çağrısı CI ölçümü | PASS | Kaynak Setup P95 46.27 ms, Portable 45.44 ms; 40 kayıt, 2000 ms bütçe. Uçtan uca açılış/FPS/kullanıcı gecikmesi değildir. |
| NVDA/Narrator / tam erişilebilirlik denetimi | NOT TESTED | Qt adları ve kontrast otomatik testi tam uyumluluk kanıtı değildir. |
| Fiziksel Windows tablet/dokunmatik, OSK, sistem DPI, düşük donanım | NOT TESTED | Pencere profili gerçek fiziksel cihazı temsil etmez. |
| Gerçek kullanıcı görev oranı/süresi; CPU/RAM/enerji/açılış benchmark | NOT TESTED | Ölçülmeyen başarı yüzdesi/FPS verilmez. |
| Kapsamlı pentest / tam WCAG denetimi | NOT TESTED | Mevcut imza/hash/izin sınırları ve bağımlılık denetimi bu kapsam değildir. |

Telefon OS/web/Gamepad/Xbox: bu Windows bakım uygulamasının dağıtım hedefleri değildir; oyun maddeleri uygulanmaz. Durumları sahte PASS yapılmaz. Yeni motor/framework veya varsayımsal platform sürümü oluşturulmaz. Kritik hedef akış FAIL kalırsa kararlı teslim yapılmaz. İlk kaynak denetiminde taşma bulundu; düzeltme sonrası sonuçlar ayrıca kaydedilir.

İlk güncelleme otomasyonu FAIL: 6.8.0 büyük yazıda bölüm seçicisine geçtiği için testin sabit Settings sekmesi varsayımı boşa çıktı (`43244789017`). Gerçek UIA ağacı incelendi; test yardımcı betiği görünür sekme veya yerel Section seçicisini kullanacak şekilde düzeltildi (`3462f2693ab87c5026dfcb03b8a4dfa25893ee87`). Sonraki gerçek Windows koşusu PASS; imza/onay veya hash denetimi atlanmadı. Uygulama payload'ı yeniden derlenmedi/değiştirilmedi. Son testlerde açık FAIL yoktur; NOT TESTED satırları tamamlandı sayılmaz.

[Ekranlar](SCREEN_INVENTORY.md), [ayrıntılı kanıt](VALIDATION.md#690-aionia-v12-native-layout-and-task-hierarchy).
