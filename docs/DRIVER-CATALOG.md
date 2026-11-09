# Automatic driver sources and a future catalog

Current WinOptimizer uses the supported Windows Update Agent COM API to search for driver updates applicable to the current PC. It stores installed inventory and per-operation plans locally; it does not currently operate an independent global driver catalog. The Microsoft Update Catalog and NVIDIA/AMD/Intel buttons are official-page handoffs, not automated OEM download adapters.

## Practical source order

1. **Windows Update Agent:** enumerate applicable driver offers, exact update/revision identity, manufacturer/model/hardware ID, download size and reboot requirements. Let Windows validate applicability and choose packages. WUA is a per-PC source, not a dump of every driver in Microsoft's catalog.
2. **Official OEM/vendor adapters:** add one documented feed/API or explicitly supported download workflow at a time. Each adapter needs a stable source contract, known publisher, package-format handling and release/architecture matching. A support page alone is not an automated feed. Avoid assuming an undocumented endpoint is stable.
3. **Verified local packages:** inspect user-imported OEM INF/CAT folders and driver-store backups. Package signatures and file manifests are rechecked before Windows stages the selected INF. This already supports offline application of a folder transferred from a connected PC.

A future catalog should index package metadata rather than duplicate vendor installer binaries: hardware and compatible IDs, INF model sections, provider/class, supported OS builds and architecture, version/date, signature/catalog status, SHA-256, official URL, size, release notes and reboot behavior. Store the catalog version/source/last check, and sign a remotely delivered metadata catalog with a dedicated catalog key. Keep binaries on official distribution hosts wherever possible.

## Matching and verification

Device name strings are insufficient. Match the device's ordered hardware/compatible IDs to the INF models and target OS/architecture constraints. Windows ranking also considers signature, features and identifier match; an old date or a higher version alone is not proof that another package is suitable. Display installed and candidate versions separately, explain unknown compatibility, and do not force a lower-ranked package.

A source adapter can refresh metadata on a schedule, but installation still needs a separate user-authorized policy. Download into a bounded cache, verify signature and file hash, create a driver backup, apply only selected eligible packages, then reread device status/version and surface failures/reboot requirements. Do not mark a launched settings page or accepted package as a verified device repair.

Match locally by default. Building a shared catalog from client hardware reports would be a new data-sharing feature requiring explicit product scope and consent; this application currently has no telemetry or such upload.

## Primary references

- [Windows Update Agent API](https://learn.microsoft.com/en-us/windows/win32/api/_wua/)
- [Searching for driver updates](https://learn.microsoft.com/en-us/windows/win32/api/wuapi/nf-wuapi-iupdatesearcher-search)
- [Hardware identifiers](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/hardware-ids)
- [Windows driver ranking](https://learn.microsoft.com/en-us/windows-hardware/drivers/install/how-windows-ranks-driver-packages)
