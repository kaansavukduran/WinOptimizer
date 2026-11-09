# WinOptimizer Pro v3.0 — Kurulum & Değişiklik Rehberi

## Dosya Listesi

| Dosya | Açıklama |
|-------|----------|
| `WinOptimizer.ps1` | Ana script (motor) |
| `Calistir.bat` | Menülü başlatıcı |
| `config.json` | Yapılandırma (beyaz liste, profil, vs.) |
| `Rollback.ps1` | Registry geri yükleme aracı |

---

## Kurulum (2 Adım)

1. Tüm dosyaları şuraya kopyalayın: `C:\ProgramData\WinOptimizer\`
2. `Calistir.bat` → **Sağ tık → Yönetici olarak çalıştır**

> İlk çalıştırmada Görev Zamanlayıcı'ya otomatik kayıt yapılır.

---

## Kullanım Örnekleri (PowerShell)

```powershell
# Tüm görevler (normal)
.\WinOptimizer.ps1

# Dry-Run — hiçbir şey silmez, sadece rapor üretir
.\WinOptimizer.ps1 -DryRun

# Sadece temizlik ve virüs taraması
.\WinOptimizer.ps1 -Tasks 1,4

# Tek görev, dry-run ile önizle
.\WinOptimizer.ps1 -Tasks 2 -DryRun

# Haftalık profil ile çalıştır
.\WinOptimizer.ps1 -Profile Weekly

# Yönetici PowerShell olmadan (BAT üzerinden)
Calistir.bat
```

---

## v3.0 Yenilikleri

### Güvenlik & Sağlamlık
- **Rollback / Snapshot**: Her optimizasyon öncesi Registry anlık görüntüsü alınır (`Snapshots\` klasörü). `Rollback.ps1` ile geri yüklenir.
- **Beyaz Liste**: `config.json → Whitelist` ile belirtilen yollar hiçbir zaman silinmez.
- **Dry-Run Modu**: `-DryRun` parametresiyle neyin yapılacağı simüle edilir, gerçek işlem yapılmaz.
- **Servis Zaman Aşımı Koruması**: `Stop-ServiceSafe` / `Start-ServiceSafe` fonksiyonları script'in servis bekleyerek bloke olmasını önler.
- **CHKDSK Düzeltmesi**: `/f` yerine `/scan` kullanılır; sorun tespit edilirse `/f` bir sonraki yeniden başlatmada çalışacak şekilde zamanlanır (script donmaz).
- **Remove-MpThreat**: Artık `ThreatID` bazlı çalışır, parametresiz toplu silme yerine güvenli tehdit bazlı temizlik yapılır.

### Kullanıcı Deneyimi
- **HTML Rapor**: Her çalıştırma sonrası renkli, tablo tabanlı HTML rapor üretilir (`son_rapor.html`).
- **Toast Bildirimi**: Tamamlanınca Windows 11 bildirim merkezine özet bildirim gönderilir.
- **Kısmi Çalışma**: `-Tasks 1,3,5` gibi parametre ile sadece seçili görevler çalışır.
- **Menülü BAT**: `Calistir.bat` artık 5 seçenekli menü sunar (Tam, Hızlı, Güvenlik, Dry-Run, Özel).
- **Eski Log Temizliği**: `MaxLogAgeDays` günden eski loglar otomatik silinir (varsayılan: 30 gün).

### Yeni Modüller (Görev 6 içinde)
- **RAM Temizleyici**: .NET GC + Working Set küçültme ile boş RAM artırılır.
- **Ağ Optimizasyonu**: TCP Auto-Tuning, RSS, ECN, DCA parametreleri optimize edilir.
- **Donanım İzleme**: PhysicalDisk sağlık durumu, CPU yükü, boş RAM raporlanır.
- **Zamanlama Profilleri**: `config.json → ScheduleProfile` ile Daily/Weekly/Monthly seçilir.

### Kod Kalitesi
- `Get-WmiObject` → `Get-CimInstance` (modernleştirildi, WMI yerine CIM).
- Tüm fonksiyonlar `Add-Result` ile `$Script:Results` koleksiyonuna veri ekler → HTML raporu besler.
- `$Script:Config` ile merkezi yapılandırma; `config.json` yoksa otomatik oluşturulur.
- `#Requires -Version 5.1` ile uyumluluk garantisi.

---

## config.json Ayarları

| Anahtar | Açıklama | Varsayılan |
|---------|----------|------------|
| `Whitelist` | Asla silinmeyecek yollar | System32, vb. |
| `StartupBlacklist` | Başlangıçtan kaldırılacak uygulamalar | Spotify, Teams, vb. |
| `MaxLogAgeDays` | Log saklama süresi (gün) | 30 |
| `EnableToast` | Toast bildirimi açık/kapalı | true |
| `EnableHtmlReport` | HTML rapor üretimi | true |
| `ScheduleProfile` | Görev Zamanlayıcı profili | Weekly |

---

## Rollback (Geri Yükleme)

```powershell
# Yönetici PowerShell'de:
.\Rollback.ps1
```

En son 5 Registry snapshot'ı geri yüklenir. Snapshot'lar `C:\ProgramData\WinOptimizer\Snapshots\` klasöründe tutulur.

---

## Sorun Giderme

**Execution Policy hatası:**
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Toast bildirimi çalışmıyor:**
`config.json` → `"EnableToast": false` yapın.

**Belirli bir klasörü korumak istiyorum:**
`config.json → Whitelist` listesine ekleyin.
