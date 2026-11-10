# SysMender donor adaptation — 6.3.0

Reviewed source: [OguzhanDUYAR/sysmender](https://github.com/OguzhanDUYAR/sysmender), commit `f1da72e5d7b371f775161989b1e2968c43c178a6` (Git commit verified; tree `e3dc98cb731d23a5390cb9e0269a1a1245a8ed97`). The audit reads actual Windows files; the README's scaffold description and newer feature matrix do not by themselves establish implementation or build results.

| Donor material | WinOptimizer adaptation |
| --- | --- |
| `apps/windows/Veri/BT.ps1`: readiness | Local OS/build/uptime and pending CBS/WU/file-operation indicators. Unreadable indicators stay unknown; raw pending-file paths are not returned. |
| Same file: events-system, events-app, crashes | System/Application critical/error records over 7 days and bug-check/unexpected-shutdown records over 14 days. Bounded newest 100, explicit provider failures and truncation. |
| Same file: dump-list | Dump filename/time/size only. No dump memory content is read or distributed. |
| Same file: defender, firewall | Current Defender status and active-store firewall profile values, with policy/third-party protection caveats and no setting changes. |
| Same file: update-history, critical-services | Local WUA history and selected service state/start mode, without online update searches or service configuration changes. |
| `apps/windows/DestekRaporu.cs` and `DestekAkisi.cs` | Review-first evidence and reduced support-report concept, independently implemented in the existing Node/Qt architecture. Event messages stay local; support exports use an explicit field allowlist. |
| Component-store inspection concept | Separate user-confirmed `Repair-WindowsImage -Online -CheckHealth` read of Windows' recorded state. Not RestoreHealth, ScanHealth or SFC repair; requires Windows administrator approval and may write the Windows diagnostic log. |

The donor catalog lists 66 tools; this release does not claim to port all 66 or achieve feature parity. Existing hardware/GPU/driver inventory, safe cleanup, startup, driver backups and restore points were retained rather than duplicated. Our 64-bit DXGI VRAM handling remains in place.

Candidate later work: full DISM/SFC repair with verified outcomes, software inventory, live process/performance data and guided symptom workflows. Not imported here: blanket debloat/tweaks, remote/enterprise administration, bulk software removal, arbitrary command runners, Linux functionality, donor branding or compiled donor executables. No global OEM driver database is supplied by this adaptation.

## Provenance and licensing

The SysMender root MIT notice (Copyright © 2026 Oğuzhan DUYAR) is preserved verbatim in `native/licenses/SysMender-MIT.txt`. Pending-restart logic is transitively adapted from WinUtil's MIT environment report, commit `2ef5e5dc7852634bc40ad789a3d1115ee3913c41`, Copyright © 2022 CT Tech Group LLC; its full notice is in `native/licenses/WinUtil-MIT.txt`. Both are bundled by the native packager. The project's existing GPLv3 license is unchanged. No legacy C# UI or unverified donor binary was copied into the runtime.

Implementation: `backend/Care.ps1`, `desktop/care.cjs`, service/bridge routes and `native/care.py`. Source attribution also appears in About. Normal scans are local, read-only and unelevated; only the separate recorded-state check requests elevation. Results persist only for the current session and are not collected on startup.

## Meaning of results

A successful read means data was obtained, not that Windows is healthy. Event 41, historical error records, dump files and old update failures do not establish an ongoing fault or root cause. Defender can be passive with another product or policy. Stopped on-demand services and inactive firewall profiles are not automatically faults. Missing logs/providers are unavailable, not clean. The component-store result is a recorded flag, not a comprehensive system-file scan.

Support JSON and clipboard summary omit event message bodies, dump contents and full file paths; this is a reduced report, not a guarantee that all metadata is anonymous. No report is sent anywhere automatically. Raw local event messages may be viewed in the expandable tree, and Event Viewer can be opened through a fixed Windows tool route.
