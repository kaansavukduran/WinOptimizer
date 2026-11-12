# AIONIA v1.5 QA — 6.10.0

12 Kasım 2026'da güncel normatif belge v1.5 olarak okunmuştur. Önceki kaynak kaydı v1.2 idi. Son kaynak/PR, paket, hareket ve kurulu güncelleme kapıları PASS; fiziksel cihaz ve kapsamlı denetim sınırları aşağıdadır.

| İnceleme / bulgu | Düzeltme / kanıt | Durum |
| --- | --- | --- |
| Ürün ve teknoloji, on ekran, geçmiş şikâyetler, mevcut Aion ve logo | Windows/Qt korunur, görsel kaynaklar ART_BIBLE/AIONIA-REFERENCES kaydından tekrar incelendi; yeni kanon yok. | PASS |
| Yeni kurulumun sistem teması v1.5'in koyu tema kuralıyla uyuşmuyordu | Koyu + sistem fontu yalnız yeni/eksik tercihin varsayılanıdır; eski açık/sistem/kontrast ve font yeniden açılışta korunur. Kaynak regresyonu ve gerçek paket geometri/PNG kanıtları doğrulandı. | PASS |
| Bakım adımında geniş düğme başlık ve durumu daraltıyordu | Başlık/durum aynı sütun; ölçülen ortak eylem genişliği, gerçek alana göre dikey dizilim. Kaynak regresyonu ve gerçek paket geometri/PNG kanıtları doğrulandı. | PASS |
| Geniş ekranda içerik ve kısa yardımcı düğmeler kontrolsüz genişliyordu | Ölçekli içerik sınırı ve eşit yan boşluk; metin kadar yardımcı düğme, HFW korunur. Kaynak regresyonu ve gerçek paket geometri/PNG kanıtları doğrulandı. | PASS |
| Düğme kenarı focus/press durumunda kalınlık değiştiriyordu | 2 px ortak kenar, renk/yerel odak işaretiyle durum; geometri sabit. Kaynak regresyonu ve gerçek paket geometri/PNG kanıtları doğrulandı. | PASS |
| Kaynak regresyonları; eski startup/disposal/recovery/safety testleri | Yerel 251 Qt / 59 Node PASS; üretim bağımlılığı denetiminde 0 bulgu. Windows kaynak/PR çalıştırıcısında da PASS. | PASS |
| Gerçek Windows Setup/Portable/reopen, beş profil × on ekran, geometrik ölçüm ve PNG | Dört önceki profil korunur; geniş koyu/sistem-font profili eklenir. 50 gerçek pencere/sayfa; dış yatay taşma 0, ortalanma hatası ≤2 px, eşdeğer eylem genişlikleri aynı, en fazla tek ana eylem. | PASS |
| Gerçek 6.9.0 → 6.10.0 imzalı kurulu güncelleme ve veri koruma | Exact payload SHA, registry/runtime 6.10.0, önceki 19 ayar alanı (test beta kanalı dışında), temizlik/geri alma geçmişi ve bakım ilerlemesi korundu. | PASS |
| Fiziksel Windows tablet/dokunmatik/OSK/DPI, NVDA/Narrator, düşük donanım | Windows pencere/Qt simülasyonu fiziksel cihaz kanıtı değildir. | NOT TESTED |
| İnsan görev başarısı, tam performans/WCAG/pentest | Test edilmedikçe yüzde, FPS veya sertifikasyon iddiası yok. | NOT TESTED |

Oyun/mobil OS/web portu yapılmaz; oyun kontrol şeması/onay maddesi uygulanmaz. Mevcut azaltılmış hareket, Aion'u gizleme, klavye, tema/font/ölçek ve gerçek adım günlüğü korunur. Testte yakalanan büyük EN metin kırpılması, yardımcı düğmenin QSizePolicy değişirken height-for-width bilgisini kaybetmesinden kaynaklandı; politika bayrağı korunarak düzeltildi, eski kırpılmama koşulu gevşetilmedi. Final testlerde açık FAIL yoktur. İlk yerel HFW kırpılma hatası yukarıdaki düzeltme sonrası yeniden test edildi; koşul gevşetilmedi.

İlk Windows paket testi FAIL: test-helper QBoxLayout enumunu nesne üzerinden okumaya çalıştı (stage 42 AttributeError); doğrudan QBoxLayout sınıf sabitiyle düzeltildi. Bu bir test yardımcı kodu hatasıydı; geometri eşitliği/ortalanma/kırpılma koşulları korunur. Başarısız kaynak/PR koşuları 43258785867 / 43258856386; Düzeltme sonrası son kaynak/PR, hareket ve güncelleme paket kapıları PASS.

İkinci kaynak Windows kapısı (43260641334 / PR 43260652556) PASS; 50 geometri kaydı ve önceki tüm paket testleri geçti. Gerçek PNG incelemesinde büyük yazı/dar pencerede sayı alanı yanındaki Varsayılana dön sözcüklerinin parçalandığı görüldü. Aynı mevcut ResponsiveRow ile dar pencerede sayı ve sıfırlama alt alta dizildi; TR/EN tam sözcük, görünürlük, resize ve değer koruma regresyonu eklendi. Son paket bu ek düzeltmeyle yeniden doğrulandı; önceki yeşil kayıt yeni kaynak için PASS yerine kullanılmaz.

Üçüncü kaynak/PR (43264623349 / 43264673484) paket kontrolü PASS. PNG denetimi, çok büyük yazıdan sistem fontuna geçişin ilk karesinde fazla paragraf boşluğu yakaladı; yerel 150/500/1000 ms tekrarda kalıcı hata oluşmadı. Windows test yakalaması artık en az 800 ms ve iki aynı geometri örneği bekler; bekleyen metin-fit zamanlayıcısı varsa yakalamaz. Fazla büyük paragraf için ayrıca üst sınır denetimi ve regresyon eklendi. Bu bekleme yalnız test yakalamasındadır; uygulama kullanımına gecikme eklenmez ve render ölçümüne katılmaz. Son Windows görüntüsünde erken kare olduğu doğrulandı; yerleşmiş görünümde kalıcı boşluk gözlenmedi.

Son Windows yakalaması yerleşmiş geometri ve paragraf üst sınırıyla PASS; erken font-geçiş karesindeki boşluk kalıcı görünüm olarak tekrar oluşmadı. PR ilk denemesinde Microsoft indirme sunucusuna bağlantı zaman aşımı yaşandı (UND_ERR_CONNECT_TIMEOUT, 10 saniye); kontrol gevşetilmeden aynı kaynak yeniden çalıştırılıp geçildi.

Birleşmiş kaynak, yalnız dört imzalı release-metadata dosyası dışında doğrulanmış kaynakla birebir eşleşir. Otomatik mükerrer main koşusu 43272509434 iptal edilmiştir; buna PASS verilmez. Yayın dosyaları kaynak Windows testinin exact byte dosyalarıdır.

Windows ölçüsü: geniş açık/TR 1240×900; geniş koyu/sistem-font profilinin ilk Genel bakış karesi WM nedeniyle 1028×749, sonraki ana sayfaları 1600×900. Dar EN 540×749; büyük yazılı profiller 540×900. İstenen ve gerçek boyutlar ayrı kaydedilir; fiziksel ekran/telefon iddiası değildir.

Gerçek yeni kurulum Setup ve Portable, ilk açılış JSON kaydında koyu tema + sistem fontu doğruladı. Hareket açık koşuda on sayfanın Aion saati ilerledi; işletim sistemi tercihi test sonunda geri kondu. [Ekranlar](SCREEN_INVENTORY.md#6100-geometri-ve-optik-denge), [kanıtlar](VALIDATION.md#6100-aionia-v15-geometric-consistency-and-optical-balance).

Yalnız eşzamanlı Qt render çağrısı: kaynak Setup P95 61.58 ms / önceden belirlenen 2000 ms bütçe (50 kayıt). Bu başlangıç, uçtan uca gecikme, FPS, CPU/RAM/enerji benchmarkı değildir.

Görsel inceleme, asistanın gerçek Windows PNG dosyalarını view_image ile incelemesidir. Gerçek kullanıcı araştırması ve insan katılımcıyla görev testi NOT TESTED olarak kalır.
