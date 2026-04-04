# WinOptimizer Pro v4.0

**Windows 10/11 Kapsamlı Sistem Optimizasyon Aracı**

---

## Özellikler

| Görev | Açıklama |
|-------|----------|
| **1. Gereksiz Dosya Temizleme** | TEMP, tarayıcı önbellek, prefetch, crash dump, CBS log, thumbnail, çöp kutusu vb. |
| **2. Disk Temizliği** | cleanmgr + DISM Component Store sıkıştırma |
| **3. Registry Temizliği** | Geçersiz uninstall, dosya ilişkilendirme, Run kayıtları, MUI Cache |
| **4. Güvenlik Taraması** | Defender, güvenlik duvarı, UAC, BitLocker, açık portlar, virüs taraması |
| **5. Windows Güncelleme** | PSWindowsUpdate ile kontrol ve yükleme |
| **6. Uygulama Güncelleme** | winget ile tüm uygulamaları güncelleme |
| **7. Başlangıç Programları** | Registry, Task Scheduler ve Startup klasör analizi |
| **8. Hizmet Optimizasyonu** | Gereksiz Windows hizmetlerini devre dışı bırakma |
| **9. Ağ Optimizasyonu** | DNS flush, Winsock reset, TCP tuning, QoS |
| **10. Güç Planı** | Ultimate/High Performance, CPU min %100, PCIe optimizasyonu |
| **11. Sistem Sağlığı Raporu** | Donanım, disk, SMART, sıcaklık, işlem, SFC, olay günlüğü |

## Gereksinimler

- Windows 10 (1709+) veya Windows 11
- PowerShell 5.1 veya üzeri
- **Yönetici (Administrator) hakları** (tüm görevler için)
- winget (Görev 6 için) — [İndir](https://aka.ms/getwinget)

## Kurulum

1. `WinOptimizer` klasörünü istediğiniz yere kopyalayın (ör. `C:\WinOptimizer`)
2. İlk çalıştırmada `Logs`, `Backups` ve `Reports` klasörleri otomatik oluşturulur

## Kullanım

### Kolay Başlatma (BAT)
```
WinOptimizer-Baslat.bat
```
Otomatik olarak Yönetici hakları ister ve interaktif menüyü açar.

### PowerShell ile Doğrudan
```powershell
# İnteraktif menü
.\WinOptimizer.ps1

# Dry-Run (simülasyon — hiçbir şey değişmez)
.\WinOptimizer.ps1 -Mode DryRun

# Sessiz mod (sadece hatalar gösterilir)
.\WinOptimizer.ps1 -Mode Silent

# Belirli görevler
.\WinOptimizer.ps1 -Tasks 1,3,6

# Yardım
.\WinOptimizer.ps1 -Help
```

### Menü Seçenekleri
| Kısayol | Mod | Görevler |
|---------|-----|----------|
| A | Tam Optimizasyon | 1–11 tümü |
| B | Hızlı Temizlik | 1, 2 |
| C | Güvenlik Paketi | 4, 5, 6 |
| D | Performans Paketi | 8, 9, 10 |
| E | Dry-Run Simülasyon | Tümü (salt okunur) |
| F | Özel Görev | Kullanıcı seçer |
| R | Sistem Raporu | 11 |

## Klasör Yapısı

```
WinOptimizer/
├── WinOptimizer.ps1          # Ana script
├── WinOptimizer-Baslat.bat   # Kolay başlatıcı
├── README.md                 # Bu dosya
├── Logs/                     # Çalıştırma logları (30 gün sonra otomatik silinir)
├── Backups/                  # Registry yedekleri
└── Reports/                  # Sistem sağlığı raporları
```

## Güvenlik Notları

- **Registry Temizliği** (Görev 3): Silme öncesi otomatik `.reg` yedek alır
- **Hizmet Optimizasyonu** (Görev 8): Yalnızca bilinen güvenli hizmetleri devre dışı bırakır
- **Dry-Run modu**: Tüm görevleri simüle eder, hiçbir değişiklik yapmaz
- Tüm işlemler `Logs/` klasörüne kaydedilir

## v3.1 → v4.0 Değişiklik Günlüğü

- **DÜZELTME**: `Measure-Object` boş klasör hatası (`Get-SafeSize` fonksiyonu ile)
- **YENİ**: Görev 6 — winget ile uygulama güncelleme
- **YENİ**: Görev 7 — Başlangıç programları yönetimi
- **YENİ**: Görev 8 — Hizmet optimizasyonu
- **YENİ**: Görev 9 — Ağ optimizasyonu (TCP, DNS, Winsock, QoS)
- **YENİ**: Görev 10 — Güç planı optimizasyonu (Ultimate Performance)
- **YENİ**: Görev 11 — Kapsamlı sistem sağlığı raporu
- **İYİLEŞTİRME**: Tarayıcı önbellek temizliği (Chrome, Edge, Firefox, Brave, Opera)
- **İYİLEŞTİRME**: Thumbnail ve icon cache temizliği
- **İYİLEŞTİRME**: Modüler menü yapısı (A/B/C/D/E/F/R/Q)
- **İYİLEŞTİRME**: Komut satırı parametreleri (-Mode, -Tasks, -Help)
- **İYİLEŞTİRME**: DryRun ve Silent modları
- **İYİLEŞTİRME**: Otomatik log rotasyonu (30 gün)
- **İYİLEŞTİRME**: Renkli konsol çıktısı ve detaylı loglama

## Lisans

MIT License
