# WinOptimizer Pro v2.0 — Kurulum ve Kullanım Kılavuzu

## Dosya Listesi

| Dosya | Açıklama |
|-------|----------|
| `WinOptimizer.ps1` | Ana PowerShell scripti (asıl işi yapan motor) |
| `Calistir_YoneticiOlarak.bat` | Çift tıkla çalıştırma dosyası |
| `panel.html` | Görsel kontrol paneli (tarayıcıda açın) |

---

## Kurulum

### Adım 1 — Dosyaları Kopyalayın
Tüm dosyaları şu konuma kopyalayın:
```
C:\ProgramData\WinOptimizer\
```

### Adım 2 — İlk Çalıştırma
`Calistir_YoneticiOlarak.bat` dosyasına **sağ tıklayın → Yönetici olarak çalıştır**

> İlk çalıştırmada Görev Zamanlayıcı'ya otomatik kayıt yapılır.

### Adım 3 — Kontrol Paneli (Opsiyonel)
`panel.html` dosyasını herhangi bir tarayıcıda açın.

---

## Çalıştırma Yöntemleri

### Yöntem A — BAT Dosyası (Önerilen)
```
Calistir_YoneticiOlarak.bat → Sağ tık → Yönetici olarak çalıştır
```

### Yöntem B — PowerShell Doğrudan
```powershell
# PowerShell'i Yönetici olarak açın, sonra:
Set-ExecutionPolicy Bypass -Scope Process -Force
.\WinOptimizer.ps1
```

### Yöntem C — Otomatik (Sistem Başlangıcında)
İlk çalıştırmanın ardından Görev Zamanlayıcı'ya kayıt otomatik yapılır.
Her Windows başlangıcında arka planda sessizce çalışır.

---

## Görevler ve Açıklamalar

| # | Görev | Yapılan İşlem |
|---|-------|---------------|
| 1 | Gereksiz Dosya Temizleme | TEMP, önbellek, çöp kutusu, .tmp/.bak, Windows.old |
| 2 | Disk Temizliği | cleanmgr /sagerun, Optimize-Volume, TRIM |
| 3 | Güncelleme Onarımı | Servis sıfırlama, DLL kaydı, WinSock, BITS |
| 4 | Virüs Temizliği | Defender imza güncelleme, QuickScan, tehdit temizleme |
| 5 | Dosya Sistemi Onarımı | SFC /scannow, DISM RestoreHealth, CHKDSK |
| 6 | Optimizasyon | Güç planı, servisler, görsel efektler, DNS, Registry |
| 7 | Otomatik Başlatma | Görev Zamanlayıcı kaydı (SYSTEM yetkisi) |

---

## Log Dosyaları

Tüm loglar şu konuma kaydedilir:
```
C:\ProgramData\WinOptimizer\
  ├── optimizer_YYYYMMDD_HHMMSS.log   ← Detaylı log
  └── son_rapor.txt                   ← Özet rapor
```

---

## Güvenlik Notları

- Script **yalnızca** Microsoft'un resmi araçlarını kullanır (SFC, DISM, Defender, cleanmgr)
- Hiçbir üçüncü taraf program indirmez veya çalıştırmaz
- Kritik sistem dosyalarına dokunmaz
- Her çalıştırmada otomatik geri yükleme noktası oluşturur

---

## Sorun Giderme

**"Execution Policy" hatası:**
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**"Yönetici yetkisi" hatası:**
BAT dosyasını sağ tıklayıp "Yönetici olarak çalıştır" seçin.

**Görev Zamanlayıcı görevi göremiyorsanız:**
- Görev Zamanlayıcı → Görev Zamanlayıcı Kitaplığı
- "WinOptimizer_AutoRun" görevini arayın
