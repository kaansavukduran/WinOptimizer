# WinOptimizer Aion 5.0.0

Yalnızca Windows 10 22H2 / Windows 11 x64 içindir.

## İndir ve kur

[Windows x64 Setup.exe](https://github.com/kaansavukduran/WinOptimizer/releases/download/v5.0.0/WinOptimizer-Aion-5.0.0-Windows-x64-Setup.exe) dosyasını indir, çift tıkla ve kurulumu tamamla. Başlat → WinOptimizer Aion yolundan aç. İlk iş olarak Sistemi kontrol et düğmesini kullan.

## Yenilikler

- Pembe Aion kimliği, gerçek kare animasyonları ve isteğe bağlı gerçek bakım ilerlemesi.
- Türkçe/English; açık, koyu, sistem ve yüksek kontrast tema. Bağımsız %80–%200 arayüz ölçeği, doğrudan yüzde girişi, yazı boyutu, çevrimdışı OpenDyslexic ve hareket/ses ayarları.
- Önizlemeli, 7 gün yaş filtresi olan temizlik, geri alınabilir güvenli depo, çakışma korumalı geri alma ve ayrı kalıcı silme.
- Gerçek sistem/güvenlik bilgileri, sürücü envanteri, üçüncü taraf sürücü yedeği ve seçmeli Windows Update sürücüleri.
- Başlangıç kayıtları ve güç planında geri dönüş; ağ/DNS araçları; yerel geçmiş, ayar ve rapor dışa aktarma.
- Ayarlar → Güncellemeler üzerinden düğmeyle kontrol ve imza/hash doğrulanan güncelleme.

## Kurulum ve veri

Kurulum dosyası Windows Authenticode sertifikasıyla imzalanmamıştır; Windows yayıncıyı bilinmeyen olarak gösterebilir. Güncelleme metadatası, uygulamaya gömülü Ed25519 anahtarıyla doğrulanır; installer SHA-256 özeti ayrıca kontrol edilir. SHA256SUMS.txt dosyası yayımlanan paketin özetini içerir.

Kayıtlar %LOCALAPPDATA%\WinOptimizer Aion altında kalır. Güncelleme/kaldırma bunları silmez. Güvenli depoya taşımak alan açmaz; Geçmiş ve yedekler → Kalıcı sil ayrı ve geri alınamayan bir işlemdir. Sürücü yedeği tam sistem yedeği veya her aygıtta garantili eski sürüme dönüş değildir. BIOS/firmware güncellemesi yoktur. İnternet isteyen işlemler: Windows Update, uygulama güncelleme kontrolü ve indirme. Yerel bakım çevrimdışı çalışır.

## English

Windows x64 only. Download Setup.exe, double-click to install, then open WinOptimizer Aion from Start. The bilingual app provides safe cleanup and restore, driver inventory/backup/selected Windows Update drivers, startup recovery, network/power tools, independent accessibility preferences, and frame-by-frame Aion. Data is kept locally. The installer has no Authenticode certificate; in-app updates verify Ed25519-authenticated metadata and the package SHA-256. No telemetry, account, arbitrary driver catalog or firmware update.

## Validation

Kaynak: e2f54e019e3268c1eecd981aa1d937f6ea65e16d. Yerel kontroller: 10 Node testi, 5 Chromium akışı, TypeScript/Vite derlemesi ve üretim bağımlılığı denetimi geçti. [Windows kurulum testi](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42683121474), [paket yayını](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42684689805) ve [iki gerçek paketle uygulama içi güncelleme](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42684849845) geçti. Güncelleme eski paketten düğmeyle başlatıldı; yeni uygulama yeniden açıldı, 5.0.0 sürümü ve dil/tema/%135 ölçek/%125 yazı/OpenDyslexic/geçmiş kayıtları doğrulandı. Test ortamı GitHub’ın Windows sanal makinesidir; fiziksel cihazlarda bütün sürücü çeşitleri test edilmiş değildir. Paket: 128.250.532 bayt. SHA-256: `55680d128171c1914fd136673f9b4ea93712b370fff265ea0ef0346ef1977160`.
