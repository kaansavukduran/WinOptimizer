# Driver workflow coverage (6.7)

This is a feature comparison, not a claim that WinOptimizer reproduces another vendor's private catalog or algorithms. Feature names were checked for [Driver Booster for Steam, Steam app 920490](https://store.steampowered.com/app/920490/Driver_Booster_for_Steam/), with repair-tool details from the [official Driver Booster manual](https://www.iobit.com/product-manuals/db-help/). A named tool does not mean identical diagnosis or hardware coverage.

| Workflow | WinOptimizer behavior | Remaining distinction |
| --- | --- | --- |
| Scan drivers | Windows device problem codes and applicable Windows Update offers | No IObit/OEM-wide proprietary version database; an old date is not a fault |
| Game Ready GPU updates | Applicable Windows Update offers, with official NVIDIA/AMD/Intel pages for newer vendor packages | Manufacturer-page download is manual; no private per-game readiness catalog |
| Stop scan | Cancels the read-only Windows inventory/update query | Driver/runtime installation is not interrupted mid-change |
| Driver installation | Selected Windows Update offers; automatic third-party package backup first | No blanket silent installation or forced version override |
| Driver recovery | Inspect signed packages from prior backups; reapply selected INF files with a fresh backup and Windows ranking | Forced rollback uses Device Manager; inbox/vendor apps are not fully backed up |
| Offline drivers | Export hardware IDs, search Microsoft catalog, import an extracted signed OEM/backup folder, apply without internet | Finding/downloading a package on the connected PC is manual |
| Ignore updates | Persistently ignore selected Windows Update offers atomically; restore selected/all visibility | Not a global ignore for all future versions of a hardware model |
| Audio/device/network repair | Service start, hardware rescan, DNS-cache repair with fresh verification | Does not guess every physical, VPN, audio-endpoint or router fault |
| Disconnected devices | Inspect/remove selected absent audio/Bluetooth/camera/printer entries; recheck absence | Other device classes and bulk removal are not offered |
| Missing game runtimes | Official Visual C++ v14 x86/x64 and legacy DirectX installers; HTTPS allowlist, Microsoft Authenticode, hash, license confirmation, protected staging, installed-indicator postcheck | Not a universal game-specific DLL repair catalog; PhysX/OpenAL and older VC generations are not managed; no arbitrary DLL downloads |
| Bad resolution | Display inventory, driver repair workflow and Windows display settings | Automatic resolution selection is not implemented |
| Incompatible drivers | Device codes, signed package inspection, recovery and Device Manager | No private compatibility blacklist or guaranteed diagnosis |
| Restore points | List/create verified Windows points; open System Protection/System Restore | Final system restoration is done in Windows; no automatic enabling or deletion |
| Gaming/focus | Temporary existing power plan, optional normal close requests for user-owned apps, persistent session, conflict-aware plan restoration | No blanket service stopping, force-kill, automatic app reopening or promised FPS gain |
| System information | Real OS/CPU/RAM/disk/security/driver information and export | Only what Windows providers expose |
| Automatic/scheduled/silent updates | Explicit user-initiated checks and installs | Background scheduling, idle auto-install, per-game silent detection and resumable driver downloads remain unimplemented |

## Package and runtime controls

Driver plans are cached server-side, expire after 30 minutes and are consumed once. Import rejects links and limits file count/size. Backups are checked against stored SHA-256 manifests; native application checks a hash-pinned file manifest, candidate catalogs and current files again. Windows validates/stages INF packages and chooses applicable drivers. Firmware packages are outside this release. A package accepted into the store is distinguished from a measured device-version change.

Runtime URLs are fixed Microsoft endpoints; redirects must remain on the HTTPS allowlist. Download sizes/time are bounded. The Microsoft publisher is verified before offering installation and again after copying to an administrator-only staging directory. The user confirms license acceptance. No installer bytes are bundled or redistributed in WinOptimizer. DirectX's optional legacy components cannot be separately uninstalled and do not replace the OS DirectX version.

## Primary implementation references

- [PnPUtil syntax and Windows driver ranking](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/pnputil-command-syntax)
- [Windows restore-point creation and frequency](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/checkpoint-computer?view=powershell-5.1)
- [Microsoft Visual C++ download endpoints](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170)
- [Microsoft DirectX June 2010 package](https://www.microsoft.com/en-us/download/details.aspx?id=8109)

## Native driver center

6.7 groups updates, searchable installed inventory, dated backup/recovery inspection, offline preparation and ignored offers in one native driver page. Game runtimes, restore points, focus and disconnected devices are categorized in the existing workshop. This organization does not expand the external catalog or bypass signed-package eligibility. Bulk ignore/show-again validates the whole selection before an atomic local state write and never installs a driver.
