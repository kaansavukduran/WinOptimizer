# AIONIA v1.5 QA — 6.10.0

12 Kasım 2026'da güncel normatif belge v1.5 olarak okunmuştur. Önceki kaynak kaydı v1.2 idi. Bu tablo geliştirme sırasında güncellenir; aşağıdaki bekleyen Windows kapıları PASS sayılmaz.

| İnceleme / bulgu | Düzeltme / kanıt | Durum |
| --- | --- | --- |
| Ürün ve teknoloji, on ekran, geçmiş şikâyetler, mevcut Aion ve logo | Windows/Qt korunur, görsel kaynaklar ART_BIBLE/AIONIA-REFERENCES kaydından tekrar incelendi; yeni kanon yok. | PASS |
| Yeni kurulumun sistem teması v1.5'in koyu tema kuralıyla uyuşmuyordu | Koyu + sistem fontu yalnız yeni/eksik tercihin varsayılanıdır; eski açık/sistem/kontrast ve font yeniden açılışta korunur. Kaynak regresyonu doğrulandı; Windows kapısı ayrıca aşağıdadır. | PASS |
| Bakım adımında geniş düğme başlık ve durumu daraltıyordu | Başlık/durum aynı sütun; ölçülen ortak eylem genişliği, gerçek alana göre dikey dizilim. Kaynak regresyonu doğrulandı; Windows kapısı ayrıca aşağıdadır. | PASS |
| Geniş ekranda içerik ve kısa yardımcı düğmeler kontrolsüz genişliyordu | Ölçekli içerik sınırı ve eşit yan boşluk; metin kadar yardımcı düğme, HFW korunur. Kaynak regresyonu doğrulandı; Windows kapısı ayrıca aşağıdadır. | PASS |
| Düğme kenarı focus/press durumunda kalınlık değiştiriyordu | 2 px ortak kenar, renk/yerel odak işaretiyle durum; geometri sabit. Kaynak regresyonu doğrulandı; Windows kapısı ayrıca aşağıdadır. | PASS |
| Kaynak regresyonları; eski startup/disposal/recovery/safety testleri | Yerel 248 Qt / 59 Node PASS; üretim bağımlılığı denetiminde 0 bulgu. Windows sonucu ayrıca beklenir. | PASS |
| Gerçek Windows Setup/Portable/reopen, beş profil × on ekran, geometrik ölçüm ve PNG | Dört önceki profil korunur; geniş koyu/sistem-font profili eklenir. | NOT TESTED |
| Gerçek 6.9.0 → 6.10.0 imzalı kurulu güncelleme ve veri koruma | Payload hash, registry/runtime, önceki ayarlar ve geçmiş doğrulanacak. | NOT TESTED |
| Fiziksel Windows tablet/dokunmatik/OSK/DPI, NVDA/Narrator, düşük donanım | Windows pencere/Qt simülasyonu fiziksel cihaz kanıtı değildir. | NOT TESTED |
| İnsan görev başarısı, tam performans/WCAG/pentest | Test edilmedikçe yüzde, FPS veya sertifikasyon iddiası yok. | NOT TESTED |

Oyun/mobil OS/web portu yapılmaz; oyun kontrol şeması/onay maddesi uygulanmaz. Mevcut azaltılmış hareket, Aion'u gizleme, klavye, tema/font/ölçek ve gerçek adım günlüğü korunur. Testte yakalanan büyük EN metin kırpılması, yardımcı düğmenin QSizePolicy değişirken height-for-width bilgisini kaybetmesinden kaynaklandı; politika bayrağı korunarak düzeltildi, eski kırpılmama koşulu gevşetilmedi. Final sonuçlar ve açık sınırlar bu kayıtta güncellenecek.
