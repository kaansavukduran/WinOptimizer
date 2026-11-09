# WinOptimizer Aion Forge

Durum: **IDLE, Windows sürümü teslim edildi.** Yetkili depo: https://github.com/kaansavukduran/WinOptimizer. Dal: `main`. Kullanıcı açıkça yalnızca Windows istedi; başka işletim sistemi paketi üretme.

## Son doğrulanmış yayın

- [WinOptimizer Aion 5.0.1, Latest](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v5.0.1).
- Uygulama kaynağı ve sürüm etiketi: `fc0e0dedc58e33041159b567e06acdc0671b55b9`. Bu dosyayı içeren sonraki commit, belge ve yedek kapanışıdır; çalışır uygulama kodu yeniden yazılmadı.
- Paket: `WinOptimizer-Aion-5.0.1-Windows-x64-Setup.exe`, 128.250.297 bayt, SHA-256 `9e687a2a8776de50c29350483c01b708c962ea2da8b758998d0c6a08e9b83d65`.
- [Kaynak derlemesi ve kurulu uygulama](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42687275191), [son Windows/6 tarayıcı kontrolü](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42688246954), [imzalı meta veriyle yayın](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42688251498), [5.0.0 → 5.0.1 uygulama içi yükseltme](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42688518853): başarılı.
- Önceki [5.0.0](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v5.0.0) ve [5.0.0-beta.1](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v5.0.0-beta.1), etiketleri ve paketleri korunur. Beta Pre-release; son kararlı Latest.
- [PR #1](https://github.com/kaansavukduran/WinOptimizer/pull/1) birleştirildi; ilk uygulama kaynağı `e2f54e019e3268c1eecd981aa1d937f6ea65e16d`, merge `a08e5fd7a842d37c57c4159bece2076332fe0240`.

## Uygulanan ürün

Electron/React gerçek Windows uygulaması; sabit eylem listeli PowerShell 5.1 arka ucu. Yedi gün yaş filtreli Temp/Chrome/Edge önbellek taraması, önizleme, geri alınabilir depo, çakışma korumalı geri alma ve ayrı kalıcı silme. Kişisel klasörler, Prefetch, toplu registry/hizmet/ağ değişiklikleri ve DISM ResetBase yeni uygulamada yoktur. Orijinal kod ve tarihçe `legacy/` içinde korunur, yeni uygulamada çalıştırılmaz.

Gerçek sistem durumu; sürücü envanteri/üçüncü taraf paket yedeği/seçmeli Windows Update sürücüleri; geri alınabilir HKCU başlangıç kayıtları; DNS/ağ ve mevcut güç planları; yerel geçmiş/rapor/ayar dışa aktarma. Sürücü yedeği tam sistem yedeği veya garantili eski sürüme dönüş değildir. 5.0.1 kısmi başarısızlığı başarı saymaz ve sürücü sonuçlarını ayrı gösterir.

TR/EN, dört tema, bağımsız arayüz ölçeği/yazı boyutu/font/satır ve harf aralığı/vurgu/yoğunluk/hareket/ses tercihleri. %80–%200 ölçek, %5 adım, elle yüzde ve bağımsız sıfırlama. Türkçe harfleri kapsayan paketli OpenDyslexic. Kullanıcı referansıyla eşleşen dört sütun/sekiz satır Aion şeridi: boşta, okuma, kısa tepki; sabit poz ve sistem azaltılmış hareket desteği. Yalnız gerçek üç kontrolü sayan, tekrarlarla artmayan isteğe bağlı bakım yolculuğu. Ayarlar ana gezinmenin en altında.

## Doğrulama

11 Node güvenlik/veri testi ve 6 gerçek Chromium arayüz senaryosu; TypeScript/Vite derlemesi; üretim bağımlılığı denetimi temiz. Türkçe/English, 135% ve 200% ölçek, 125% yazı, OpenDyslexic/yüksek kontrast/dar pencere, klavye, yeniden açılış, bağımsız sıfırlama, hareket azaltma ve oyunlaştırmayı kapatma kontrol edildi.

Windows sanal makinesinde PowerShell 5.1 parser; gerçek sağlık/sürücü/ağ/güç bilgisi; sürücü yedeği dosya özetleri; geçici HKCU başlangıç kaydını kaldırma/geri alma; gerçek NSIS temiz kurulum; kurulu uygulamadan geçici dosya taşıma/geri alma ve sürücü listeleme geçti. İki gerçek yayımlanmış paket arasında güncelleme uygulamanın düğmesiyle başlatıldı, uygulama yeniden açıldı, sürüm ve ayar/geçmiş koruması doğrulandı. Bozuk imza, hash ve kesik indirme kurulabilir dosya bırakmaz. Kısmi sürücü sonucu UI testi kontrollü test verisidir; bir aygıt bilerek bozulmadı. Fiziksel Windows 10/11 cihazlarının her donanımı test edilmiş değildir.

## Özel Drive yedeği

[WinOptimizer](https://drive.google.com/drive/folders/1weoq7A_Y6jjhVgR8eb3QrnES9cxGurGE), kullanıcının verdiği Yazılım Geliştirme klasöründedir. Sahibi Kaan; paylaşılmamış olduğu yeniden okundu. Kaynak ZIP, tüm erişilebilir dallar/etiketler/geçmiş için Git bundle ve commit/tarih/özet makbuzları saklandı. Özel anahtarlar tarandı ve yüklenmedi. [Doğrulama makbuzu](https://drive.google.com/file/d/1BGFfpQ-FFwQceUp5aBlMA8469a0ezR4p/view) kaynak ZIP/Git bundle/parça dosyalarının gerçek geri okuma SHA-256 ve arşiv kontrollerini kaydeder.

`Sürümler/5.0.0-beta.1`, `Sürümler/5.0.0`, [Sürümler/5.0.1](https://drive.google.com/drive/folders/1MGlxB4y8_kmvmcLqtwrx9I38Ut87MfHo) kaynak, paket yedeği, notlar, imzalı meta veri ve makbuzları içerir. Drive bağlantısında tek dosya limiti 100 MiB olduğundan kurulum dosyaları iki kayıpsız parçadır. `installer-parts.json`, `Yedegi-Birlestir.bat/.ps1` ve README ile özgün Setup.exe üretilir; üç sürümün birleştirilmiş SHA-256 özetleri özgün paketlerle eşleşti. GitHub Releases üzerinde her sürüm tek, gerçek Setup.exe dosyasıdır.

## Sonraki tur için sınırlar

- Çalışır uygulamayı yeniden kurma; güncel main/PR/Actions ve bu nottan devam et. Kullanıcı değişikliklerini ezme, yayımlanmış dosya/etiketleri değiştirme.
- Authenticode sertifikası yoktur. Güncelleyici ayrı Ed25519 imzalı meta veri + paket SHA-256 doğrular. Özel imzalama anahtarı yalnızca özel oturum çalışma alanında, depo/yedek dışında tutulur. Kalıcı GitHub Secrets erişimi 403 nedeniyle kurulamadı; sonraki sürümden önce güvenli anahtar kalıcılığını çöz. Güvenilen açık anahtarı sessizce değiştirme ve özel anahtarı Git/Drive'a koyma.
- Yerel bağlı GitHub kimliği uploads.github.com için 401 verdi. Bu yüzden `publish.yml`, deponun kendi contents:write GITHUB_TOKEN yetkisiyle paketleri yükler; imza/hash/kaynak commit eşleşmesini kontrol eder. `release-metadata/release-ids.json` tam yayın kimliklerini korur. Yeni sürüm için yeni draft kimliği ve imzalı meta veri gerekir.
- Windows derleme akışı hedef sürümü package.json'dan alır. Yükseltme akışı eski sürüm etiketi ve beklenen sürüm girdilerini alır. Sonraki yeni sürümde önceki yayımlanmış beta paketini yeniden etiketleme.
- OEM entegrasyonları, daha çok tarayıcı profili ve donanıma özgü kurtarma gelecekte ayrı kapsamdır. Evrensel hızlanma, firmware güncellemesi veya tam sistem yedeği iddiası yoktur.
