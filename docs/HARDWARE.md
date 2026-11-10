# Donanım envanteri / Hardware inventory

6.1.0 adds a native Qt **Donanım / Hardware** navigation tab. Scan once, browse an overview and expandable details, search model names or localized property names, choose a category, and export the existing report as JSON without rescanning. Results remain available while switching tabs or changing appearance/language in the current session. A new scan refreshes them; hardware data is not silently collected on startup.

| Category | Windows source / examples |
| --- | --- |
| System, CPU | CIM ComputerSystem/Processor: model/vendor, usable RAM, sockets, cores/threads, clocks/cache, architecture, virtualization |
| GPU | DXGI adapter description + CIM VideoController: adapter name, dedicated/shared memory, driver, active resolution/refresh where exposed |
| Memory modules/arrays | CIM PhysicalMemory/PhysicalMemoryArray: module capacity, DDR type, manufacturer/part, reported speeds and slots/capacity |
| Motherboard, BIOS | CIM BaseBoard/BIOS: vendor, model/version, BIOS release |
| Storage, volumes | CIM DiskDrive/LogicalDisk + Get-Disk: capacity/free space, firmware, bus, partitions/filesystem |
| Displays | EDID WmiMonitorID, fallback DesktopMonitor |
| Network, audio, battery | Get-NetAdapter, SoundDevice, Battery: interfaces/link state, audio devices, reported battery values |
| Other devices | PnPEntity: class, name/vendor, driver service, presence and Windows error code |

The backend does not download files, update drivers, modify settings or request elevation. Each category emits actual running and complete/failed progress. No-device and provider-unavailable results are distinguished; missing values are unknown. Partial provider failures keep the successfully read sections and finish with attention. At most 5,000 devices per category are displayed/exported, with an explicit limit indicator and total.

DXGI `DedicatedVideoMemory` is pointer-sized, represented as unsigned 64-bit bytes on the supported x64 platform. CIM `AdapterRAM` is uint32 and may overflow above 4 GiB; it is never presented as exact VRAM. If DXGI is unavailable, the CIM GPU can still be named, but VRAM is unknown. Shared GPU memory is a system-memory limit, never added to dedicated VRAM. Integrated/software/remote adapters can legitimately report zero dedicated memory. DXGI counts describe the adapter, not current GPU utilization or a workload's remaining budget.

RAM module totals and Windows-usable RAM are shown separately. Firmware-provided slot, memory-speed and maximum-capacity values are reported values, not a guarantee of upgrade compatibility. This inventory does not universally expose PSU/cooler models, temperatures, fan speeds, RAM timings, SMART health, monitor panel characteristics or hardware serial numbers. It does not infer failing hardware from an old driver date or generic status. Windows/provider availability and virtualized devices vary by machine.

Windows 10/11 x64, native Python/Qt interface; existing headless Node and Windows PowerShell 5.1 layer. No Chromium or browser engine dependency.

## 6.2.0 readability

The overview uses compact capacity values; exact byte counts remain in expanded fields and full JSON/text reports. Software/remote adapters are labelled when DXGI provides their flags. Copy summary uses the local clipboard; Save text report writes UTF-8 using the existing scan, with no network or rescan. Search/category choices survive tab changes within the session. A visible no-match message and Clear action explain empty filtered results. Match counts count report entries, not unique physical devices.

Hardware progress counts the latest terminal Windows receipt for each of the fourteen known categories, once per category. Failure/skip receipts advance completed work while remaining failures/skips in the log; the percentage is work processed, not a health score. Unbounded operations retain indeterminate progress. Operation detail visibility is saved independently; collapsing the table preserves live summary counts, trace collection and full-log export.
