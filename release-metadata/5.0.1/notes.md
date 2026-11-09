# WinOptimizer Aion 5.0.1

Windows 10 22H2 / Windows 11 x64 için bakım uygulaması.

[Windows x64 Setup.exe indir](https://github.com/kaansavukduran/WinOptimizer/releases/download/v5.0.1/WinOptimizer-Aion-5.0.1-Windows-x64-Setup.exe), dosyaya çift tıkla ve kurulumu tamamla. Başlat → WinOptimizer Aion ile aç. Sürümü Ayarlar → Hakkında bölümünde görebilirsin.

## 5.0.1 düzeltmesi

Kısmi sürücü yükleme başarısızlıkları, geri alma çakışmaları ve başarısız kalıcı silmeler artık başarı olarak gösterilmez. Böyle bir sonuçta Aion başarı tepkisi ve başarı sesi üretmez. Her sürücünün tamamlandı/başarısız sonucu Geçmiş ve yedekler içinde ayrı görünür. Önceki sürümler, etiketler, ayarlar ve geçmiş korunur.

## Uygulama

Pembe Aion kare animasyonları; Türkçe/English; tema, disleksi dostu yazı tipi, bağımsız yazı boyutu ve %80–%200 arayüz ölçeği; güvenli temizlik/geri alma, sürücü envanteri/yedeği ve seçmeli Windows Update sürücüleri; başlangıç, ağ ve güç araçları; yerel geçmiş ve dışa aktarma; imza/hash doğrulamalı uygulama içi güncelleme.

Kurulum dosyası Windows Authenticode sertifikasıyla imzalanmamıştır. Güncelleme metadatası gömülü Ed25519 anahtarıyla, indirilen paket SHA-256 ile doğrulanır. Kayıtlar %LOCALAPPDATA%\WinOptimizer Aion içinde kalır. Güvenli depoya taşımak henüz alan açmaz; kalıcı silme ayrı ve geri alınamayan işlemdir. Sürücü yedeği yalnızca üçüncü taraf sürücü deposunu kapsar; tam sistem yedeği veya her cihazda garantili eski sürüme dönüş değildir. BIOS/firmware güncellemesi yoktur.

## Doğrulama

[Windows derleme ve kurulu uygulama testi](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42687275191) geçti. 11 Node güvenlik/veri testi, 5 genel Chromium akışı ve ayrıca kısmi sürücü sonucu için gerçek arayüz regresyon testi geçti. Kısmi sürücü sonucu testi kontrollü bir UI senaryosudur; gerçek bir aygıta bilerek bozuk sürücü yüklenmedi. Windows test ortamı GitHub’ın sanal makinesidir. 5.0.0 → 5.0.1 uygulama içi yükseltme sonucu final yayın öncesi eklenir.

## English

Windows x64 only. Download Setup.exe, double-click, then open WinOptimizer Aion from Start. 5.0.1 correctly reports partial failures instead of celebrating success and lists each driver result in history. Existing versions and user data are preserved. The app includes bilingual accessibility settings, independent interface/text scaling, Aion sprite animation, safe cleanup/recovery, driver and startup tools, local exports and authenticated updates. No Authenticode certificate; updates verify Ed25519 metadata and package SHA-256.
