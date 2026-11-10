# Verification evidence

## 6.2.0 Native update replacement and readable results

Application/tag source `fc60edaed7aa75ae78b3deaac8ddccb20179248c`, PR #9, merge `9dba27a974fc8926b09de27db0a0348a80032048`. [Release v6.2.0](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v6.2.0) is stable/latest. [Source Windows](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42777535853), [PR](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42777542808), [main](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42778260279), [immutable publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42778350270) and [actual native 6.1.0 → 6.2.0 upgrade](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42778713731) passed.

47 Node and 18 native Qt checks passed, covering preserved hardware search, clipboard/UTF-8 report output, unknown data, real-receipt category progress, collapsed log visibility/counts, saved preferences, clean installer handoff and launch failure recovery. Real installed and portable packages read fourteen categories, copied the actual Windows inventory summary and formatted the full text report. Portable reopening and data isolation passed. The package scan rejects browser-engine payloads; the GUI remains Python/Qt Widgets with headless Node/PowerShell. [Turkish compact Windows view](screenshots/WinOptimizer-6.2.0-Windows-Donanim.png) shows the test VM's hardware.

The old native update negative control [6.0.0 → 6.1.0](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42776288899) reached the real confirmation through Windows UI Automation, then exposed registration 6.1.0 with the unchanged 6.0.0 executable hash. It is a failing historical pair, not a certified upgrade. The new installer stages the complete new payload and retries atomic MoveFileEx replacement while the old executable remains locked. Registration and restart follow successful replacement; failures leave the old executable. Installer/client handoffs request a fresh onefile environment. A real Windows test holds the installed EXE open without delete sharing, verifies the installer waits, releases the lock, and verifies the exact new payload with no leftover staging file.

The successful 6.1.0 → 6.2.0 run invokes Settings, Updates, Check for updates, Update and restart, and Continue on the installed native app. It checks the installed EXE against the published portable SHA-256, registration 6.2.0, and actual running application 6.2.0. English, dark theme, 135% UI, 125% text, OpenDyslexic, cleanup/restore history and milestones were preserved. Upgrade artifact `13744404860`: SHA-256 `57d0dd43d8015d5a815c0c2ec098748eda40ac70aba02eea063e4b2a31a483c9`; ZIP CRC and actual receipts verified.

Source artifact `13745030924`: SHA-256 `27848a4251b47a54feaa0f70e76a414895b671efe824262ee7b0b764ed991b32`; original digest and ZIP CRC verified. Embedded-key Ed25519 metadata, all five published asset sizes/digests, and all seven original icon payloads at 16/24/32/48/64/128/256 pixels in both EXEs were checked.

| Package | Bytes | SHA-256 |
| --- | --- | --- |
| Setup | 94,171,235 | `e24f9ab650e54a46acbe8bf688ddb4cf642773015625ce9a186ee768d1f5b2e4` |
| Portable | 94,046,497 | `c57f9356d28ca451c4b277574e79c92a3175b8708c893ff679d9f0db105c407f` |

Hardware percentage is processed category work, not a health score. Missing values/providers and unknown operation totals remain explicit. Physical GPU/provider combinations and all disk/filesystem failures are not exhaustively certified; [hardware scope](HARDWARE.md) applies. Portable updates remain manual replacement beside Data; installer Authenticode signing remains unavailable. In-app installer updates authenticate Ed25519 metadata plus SHA-256.

Source/history and whole Setup/Portable private Drive readbacks passed size/hash, ZIP CRC and Git-bundle checks. Final evidence and the cumulative private receipt retain previous records. Private signing keys are excluded.


## 6.1.0 Hardware and front-facing Aion

Application/tag source `350a93c4751d283a57cca72fe95077d5028e7786`, merged through PR #8. 46 Node checks and 12 native Qt checks passed. [Source Windows build](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42745105796), [PR](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42745111433), [main](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42745759295), [immutable publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42745776245) and [installed 5.3.0 → 6.1.0 upgrade](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42745955196) succeeded. Release [v6.1.0](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v6.1.0) is stable/latest; prior 6.0.1 angled-icon preview remains a historical prerelease.

Actual Windows PowerShell 5.1 parsed the inventory and compiled the DXGI C# helper. Both installed and portable packages scanned fourteen categories through their native Qt Hardware tab and recorded actual category completion events. The runner reported system, CPU, GPU, memory/arrays, motherboard, BIOS, storage/volumes, display, network and PnP devices; audio and battery correctly reported no devices. Reopening, installed/portable data isolation, real cleanup/restore and official Microsoft runtime checks passed. [Turkish 100% view](screenshots/WinOptimizer-6.1.0-Windows-Donanim.png) shows the Windows runner's hardware, not the user's computer.

UI/service fixtures check a 12 GiB dedicated GPU value, unknown fallback VRAM, DDR5, category/search behavior, missing providers versus absent devices, read-only unelevated invocation, retained session results and export without rescanning. DXGI fields are uint64; the Windows VM supplied values above 4 GiB for shared memory. A physical GPU with more than 4 GiB dedicated VRAM was not separately exercised. [Hardware sources and limitations](HARDWARE.md) describe unsupported sensors/PSU information and firmware-provided values.

Final source artifact `13731436656`: SHA-256 `a0a1f33c2d06737d9bef3b4ebae3fbfa1ff76fc950b9edb6f4818691232b53a4`. Original artifact SHA-256/ZIP CRC and embedded-key Ed25519 metadata were verified. All five published asset sizes/digests match the source build. Both PE files contain all seven original front-facing icon payloads at 16/24/32/48/64/128/256 pixels.

| Package | Bytes | SHA-256 |
| --- | --- | --- |
| Setup | 94,160,972 | `fdf23af1e99e1f618a49b4e8d0aa2b67c5003c18c2971d49309b822365c8c9a9` |
| Portable | 94,037,141 | `79227d0401dcd571ce6e9b27dca0c0e6be439e0dbe3a7a157173358bad2387bc` |

Downloaded upgrade evidence `13731322441` passed SHA-256 `aed80b06c4ba1e73b2ac1681f32039acfa302c4689817f7b12f48ce46b7f779e` and ZIP CRC. It verifies version 6.1.0, English/dark/135% UI/125% text/OpenDyslexic, original cleanup/restore events and milestones. This is the tested 5.3.0 migration pair; no separate 6.0.0 → 6.1.0 in-app pair was certified. Installer Authenticode signing remains unavailable; authenticated in-app updates use Ed25519 metadata and SHA-256. Portable updates remain manual EXE replacement beside Data.

Private Drive backup readbacks for source ZIPs, all-history Git bundles and whole Setup/Portable files passed size/SHA-256, ZIP CRC and Git-bundle checks. No private signing key was uploaded. The canonical private receipt retains previous verification records and records the new source/package evidence.


Production release: [6.0.0](https://github.com/kaansavukduran/WinOptimizer/releases/tag/v6.0.0). Production application source/tag: `d5090af906b313eb8e63160c354bda54f7edda6b`. Earlier evidence is retained below.

## 6.0.0 native Windows GUI

45 Node/backend tests and 10 native PySide6/Qt UI tests passed. The interface is Qt Widgets/QPainter, not a browser surface. The packaged application includes CPython and a SHA-pinned official Node24.22.1 runtime; no separately installed Python/Node/browser is required. PyInstaller archive entries were checked for Electron, Chromium and Qt WebEngine payloads and none were present. Previous Chromium UI tests describe earlier versions, not the 6.x native UI.

[Source build/install](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42736382969), [PR validation](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42736390974), [merge](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42737067232) and [publication](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42737192913) succeeded. The opt-in packaged Qt UI self-test used the real native entry, clicked its controls, ran actual Windows health and local diagnostic inventory, moved/restored a real aged Temp file and reopened the portable executable. Portable settings were beside its EXE and installed settings remained byte-identical. These are hosted Windows VM/internal UI self-test results; they are not a claim of exhaustive physical hardware or external UI Automation certification.

[Installed 5.3.0 → 6.0.0 migration](https://github.com/kaansavukduran/WinOptimizer/actions/runs/42737857096) passed: the old app's update button downloaded/authenticated/ran the new Setup; the native app reopened; English/dark/135% UI/125% text/OpenDyslexic remained. The original cleanup and restore events and health/scan milestones remained. Exported receipts were downloaded with artifact SHA-256 and ZIP CRC checks, and their exact version/settings/history assertions were reread. A previous successful migration run was extended with a test-only history check; published binaries were not changed.

Native UI fixtures verify bilingual Update all without individual checkboxes, confirmation/cancel, 24 offers, partial failures, native navigation, independent large appearance settings, explicit local scan/skip reasons, retained chronological export and latest-state display, per-driver outcomes with identical titles, portable update separation and primary-action visibility. Backend tests cover 32-item hash-pinned plans, ignored/firmware exclusion, cleanup protections and native progress line delivery. The PowerShell5.1 integration tests read actual progress events and reject tampered plans before Windows Update mutation. Driver installation failures and large offer lists use controlled fixtures; no device was deliberately damaged.

Setup: 93,478,533 bytes, SHA-256 `532a90c7932b4ad1a3b654aa5e7cea28d3a41c5328e2e1c23e262488ed98f1be`. Portable: 93,426,145 bytes, SHA-256 `4ed4e7e047e0096fb0f6f71dff08ea51c1b4be24558f46014ae616a27b4c0bf7`. Both signed-manifest descriptors and all five GitHub release asset digests matched before/after publication. Whole Setup/Portable files, source ZIPs and Git bundles were downloaded from private Drive and compared byte-for-byte; ZIP CRC and Git bundle verification passed. Private signing keys were excluded.

Authenticode remains unavailable. Portable updates currently use manual browser download/file replacement and are not an automatically verified self-update. The installed migration test crosses from 5.3 to native6; a future native6-to-native6 update pair does not yet exist. Full original CLI/Driver Booster parity is not claimed; see [legacy coverage](LEGACY-COVERAGE.md) and [driver coverage](DRIVER-COVERAGE.md). Actual native Windows screenshots are in [screenshots](screenshots/).

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
