# Verification evidence

Production release: [5.3.0](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v5.3.0). Production application source/tag: `d67947e2e172dfdab36103f52f164bd277596973`. Earlier evidence is retained below.

## 5.3.0 interactive companion and 5.2 workshop

36 Node tests and 17 Chromium scenarios passed. Coverage includes pointer directions/dead zone, four petting zones, keyboard activation, persisted independent settings, reduced motion, disabled/offscreen behavior, scan-result pointer following, 150% mascot with 200% narrow UI, and firmware exclusion. Workshop tests cover signed local package inspection, one-use plans and changed files, selected updates and exact ignores, bounded imports, Microsoft runtime publisher/hash verification, absent-device rechecks and conflict-aware focus restoration. Production dependency audit reported zero vulnerabilities at validation time.

[Source Windows build/install](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42725411279), [PR validation](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42725419940), [main merge](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42726497251) and [immutable publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42726582946) succeeded. Artifact SHA-256 and ZIP CRC, embedded-key Ed25519 signature, source commit and all four published asset digests were checked. Installer: 134,466,232 bytes; SHA-256 `c2635bf1980b0def3a612b40ecf25597213366138c30580dc922f815a28f185b`.

[Real installed 5.2.0 → 5.3.0 update](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42726691878) passed using the app's update button. English, dark theme, 135% UI, 125% text, OpenDyslexic and existing activity remained. The installed app passed scan and pointer/petting checks; its Turkish light/dark/scan/workshop/pointer/petting screenshots are in [screenshots](screenshots/). VM values in screenshots describe that runner.

5.2 source [42721023776](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42721023776) passed real official Microsoft DirectX download, publisher validation, installation and installed-indicator postcheck. [5.1.0 → 5.2.0 update](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42722973347) preserved settings/history. An earlier screenshot helper expected a stale button label; the test-only fix was rerun successfully without changing published binaries.

Private Drive source/history/release readbacks passed byte/hash, ZIP CRC and Git-bundle verification. The downloaded helper reconstructed the original 5.3.0 installer from downloaded parts with the exact SHA-256 above. No private signing key was included. Physical hardware permutations, all driver classes and OEM catalogs are not exhaustively certified. The application has no independent global/OEM catalog or Authenticode certificate; see [coverage](DRIVER-COVERAGE.md) and [catalog](DRIVER-CATALOG.md).

## Earlier 5.0.1 evidence

| Evidence | Result |
| --- | --- |
| Node security/data checks | 11 passed: scoped cleanup, personal/recent-file protection, link/traversal rejection, changed files, one-use plans, restore conflicts, actual purge bytes, settings persistence/independence, milestone deduplication, non-executable imports, shell payload isolation, signature/platform/channel/URL/hash checks, corrupt/interrupted downloads, partial-result classification. |
| Real Chromium UI | 6 passed: bilingual state, invalid scale/reset, narrow 200% with 125% text/OpenDyslexic/high contrast, keyboard, reduced motion, disable journey/companion, source-frame animation, and partial-driver failure feedback/history. Partial driver results are explicit UI fixtures, not deliberate hardware damage. |
| TypeScript/Vite | Production build passed. Production dependency audit: zero vulnerabilities at validation time. |
| Fonts | Regular and bold cmap include Ç Ğ İ Ö Ş Ü ç ğ ı ö ş ü; actual bundled font loaded in Chromium. Original OTF/OFL files retained, no runtime font download. |
| [Windows build/install](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42687275191) | PS 5.1 parse and real system inventory, driver export/hash verification, reversible HKCU fixture, real Setup.exe install, actual installed cleanup/restore, driver inventory and persisted appearance passed. |
| [Windows final UI coverage](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42688246954) | All checks passed, including all 6 browser scenarios. Application code unchanged from the production source; metadata and UI regression coverage were added. |
| [5.0.0 → 5.0.1 installed update](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42688518853) | Real old package installed, real sample data created, Settings → Updates used, signed metadata/hash verified, app restarted, version 5.0.1 and language/dark theme/135% scale/125% text/OpenDyslexic/activity preserved. |
| [Earlier baseline → 5.0.0](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42684849845) | Earlier pair independently passed. |
| [Publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42688251498) | Original artifact SHA-256/ZIP CRC, manifest Ed25519 signature, source commit, architecture, size and installer hash verified before immutable upload. |
| Drive readback | Source ZIP CRC and Git bundle verification passed after downloading actual stored bytes. All installer backup parts were downloaded, hashed and recombined to the exact original package SHA-256. Private project ownership/sharing re-read. |

Installer bytes: 128250297. SHA-256: `9e687a2a8776de50c29350483c01b708c962ea2da8b758998d0c6a08e9b83d65`.

Limits: hosted Windows VM coverage, not every physical Windows 10/11 device. No BIOS/firmware updater or complete system-image backup. No Windows Authenticode certificate. Update authentication is Ed25519-authenticated metadata plus SHA-256. Browser preview is explicitly labelled and cannot execute Windows operations or fabricate device data. Offline local flows do not make update availability claims; physical network-disconnection scenarios were not separately certified.


## 5.1.0 Scan & Fix

19 Node tests and 8 Chromium scenarios passed, including expired/forged repair plans, changed/disabled targets, partial/unverified outcomes, explicit confirmation, manual-guidance labeling, retained scan results and 200% narrow layouts. Production npm audit: zero findings. Local PowerShell parsing and real Windows PowerShell 5.1 inventory passed.

Source [42707694779](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42707694779), PR [42707734459](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42707734459), main [42708567170](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42708567170) and publication [42708918343](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42708918343) succeeded. The installed app read real devices/services/network/display/runtime data with no unavailable providers on the Windows runner. This is VM evidence, not universal hardware coverage. Repairs were not tested by deliberately damaging devices; before/after failure paths use controlled fixtures.

[Installed 5.0.1 → 5.1.0 upgrade](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42709194171) verified version 5.1.0, dark theme, English, 135% interface, 125% text, OpenDyslexic and existing history. The updated installed application ran Scan & Fix again. Downloaded artifact digests and ZIP CRCs were checked; Drive parts were downloaded, hashed and reconstructed using the supplied PowerShell helper to the original installer SHA-256.

Tagged source: `5d696ccbdbd7d4eaee8dfa0041fcf744507c05ed`; installer 128,258,942 bytes, SHA-256 `b4898218d8203460abc8e5585659508503a367cd030fb693be404e06ce5d40aa`. Authenticode remains unsigned; in-app updates verify Ed25519 metadata and the package hash. Exact scan/repair limits are in [SCAN-FIX.md](SCAN-FIX.md).
