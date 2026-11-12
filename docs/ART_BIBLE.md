# WinOptimizer görsel ve etkileşim kuralları

AIONIA v1.1 uygulanır. Bu bir bakım uygulamasıdır: sıcak, sade, okunaklı ve öngörülebilir. Fragaria Interactive üst marka, AIONIA evren/tasarım standardıdır; Fragaria Games oyun yayın markası bu aracı oyun yapmaz. Arayüz metni sistem/Verdana/OpenDyslexic ile okunur; pixel font veya zorunlu pixel art dönüşümü yapılmaz.

## Ortak bileşen sistemi

Açık tema: arka plan `#fcf7fb`, yüzey `#ffffff`, metin `#302838`, sınır `#8e748a`. Koyu tema: `#18151e`, `#29222f`, `#fff5fa`, `#aa8fa8`. Yüksek kontrast: siyah/yakın siyah/beyaz/sarı. Vurgu varsayılanı `#b82e69`, kullanıcı tarafından bağımsız değişir. Odak rengi her iki yüzeyde 3:1 altına düşerse mavi/pembe veya okunaklı nötrden seçilir. Ana düğme yazısı siyah/beyaz seçimiyle en az 4.5:1 hedefler. Kontrol sınırları 3:1 hedefler. Bunlar renk çifti ölçümleridir, tüm ürün için WCAG sertifikası değildir.

4 px köşe, ölçeklenen tutarlı boşluk, metinle birlikte seçili/başarısız/atlanan durum, aynı yerel düğme ve form bileşenleri kullanılır. F1 rehberi, büyük yazıda kaydırılabilir. Sekmeler sığmadığında aynı sıradaki bütün bölümler tek seçicide bulunur. Yeni kontrol veya sayfa seçimi bakım puanı üretmez.

## Karakterler ve kaynaklar

12.11.2026 tarihinde 00_BAŞLA, v1.0 ve ardından güncellenen v1.1, çilek referansı ve klasörde bulunan 19 görsel incelendi. [Manifest](AIONIA-REFERENCES.json) dosya kimliği, hash, boyut ve onay durumunu kaydeder. Aion: pembe aksolotl, mavi uçlu solungaçlar, mavi gözler, beyaz önlük ve DNA kuyruk detayı. Kurt: gri/krem, turkuaz gözler ve paftada mor kol izi. Kuzu: krem yün, amber göz, bazı varyantlarda hale. Ömer: sıcak kahverengi/krem baykuş. Emre: açık kahverengi tavşan, mavi gömlek/kırmızı kravat. Bunlar gözlenen referans özellikleridir; kanon kararı değildir.

Aion A/B arka kuyruk pozları, Kuzu v01/v02, motion/canonical paftalar farklıdır. “Canonical” dosya adı nihai kullanıcı onayı sayılmaz. Emre'nin yalnız model paftası vardır; sprite sheet yoktur. Paftalarda önden T pozu (Ömer'de kanatlar açık) gözlendi; her karakter için ayrı, bağımsız T pozu dosyası bulunmuş sayılmaz. Çilek JPG'si logo referansıdır; kesin logo onayı yoktur. Onay klasörü boştu. Bu dosyalar uygulama paketine alınmaz, türev grafik üretilmez. Önceden kullanıcı tarafından istenmiş WinOptimizer Aion'u, çarklı ikon ve mevcut üç etkileşim paftası aynen korunur; diğer karakterler bu bakım aracına zorla eklenmez.

## Çalışan animasyon sözleşmesi

Yerel `native/mascot.py` çalışma davranışı esastır. Core ve sections: 256×256 hücre, 4 sütun × 6 satır, 360 ms/kare, 4 kare döngü; success bir kez oynar ve idle'a döner. Pet: 192×208 hücre, 8×11, 16 yön satır 9–10; sevilme satır 3/4, 4/5 kare, 240 ms/kare. Pivot altta ortada, en/boy korunur. Bu varlıklar mevcut yumuşak çizimli uygulama görselleridir; pixel-perfect oyun sprite'ı diye sunulmaz. Oyun hitbox'ı yok; tıklama bölgesi karakter widget'ıdır.

Windows azaltılmış hareketi ve uygulama hareket/görünürlük ayarları korunur. Gizlenince animasyon zamanlayıcısı durur. Başarı animi tek başına işlem kanıtı değildir; gerçek adım günlüğü esas alınır. Kaynak/hak kayıtları mevcut `ASSETS.json` ve üçüncü taraf bildirimlerinde korunur.
